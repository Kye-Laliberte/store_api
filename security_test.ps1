$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repositoryRoot = $PSScriptRoot
$envPath = Join-Path $repositoryRoot ".env"

if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
    throw ".env is missing. Run .\setup_env.ps1 from the repository root first."
}

function Get-EnvValue {
    param(
        [string[]]$Lines,
        [string]$Name
    )

    $prefix = "$Name="
    foreach ($line in $Lines) {
        $trimmedLine = $line.Trim()
        if ($trimmedLine.StartsWith($prefix, [StringComparison]::Ordinal)) {
            $value = $trimmedLine.Substring($prefix.Length).Trim()
            if ($value.Length -ge 2) {
                $firstChar = $value[0]
                $lastChar = $value[$value.Length - 1]
                if (($firstChar -eq '"' -and $lastChar -eq '"') -or
                    ($firstChar -eq "'" -and $lastChar -eq "'")) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
            }
            return $value
        }
    }

    return $null
}

$envLines = Get-Content -LiteralPath $envPath
$jwtSecret = Get-EnvValue -Lines $envLines -Name "JWT_SECRET_KEY"
if ([string]::IsNullOrWhiteSpace($jwtSecret)) {
    throw "JWT_SECRET_KEY is missing from .env."
}
if ($jwtSecret -ne $jwtSecret.Trim()) {
    throw "JWT_SECRET_KEY must not have surrounding whitespace."
}

$jwtKeyBytes = [Text.Encoding]::UTF8.GetBytes($jwtSecret)
if ($jwtKeyBytes.Length -lt 32) {
    throw "JWT_SECRET_KEY must contain at least 32 UTF-8 bytes."
}

$jwtHeader = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('{"alg":"HS256","typ":"JWT"}')).TrimEnd('=').Replace('+', '-').Replace('/', '_')
$jwtPayload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('{"sub":"setup-check"}')).TrimEnd('=').Replace('+', '-').Replace('/', '_')
$jwtSigningInput = "$jwtHeader.$jwtPayload"
$hmac = [System.Security.Cryptography.HMACSHA256]::new($jwtKeyBytes)
try {
    $signature = $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($jwtSigningInput))
}
finally {
    $hmac.Dispose()
}
if ($signature.Length -ne 32) {
    throw "HS256 signing check failed."
}
Write-Host "[OK] JWT secret meets the HS256 key requirements."

$databaseUrl = Get-EnvValue -Lines $envLines -Name "DATABASE_URL"
if ([string]::IsNullOrWhiteSpace($databaseUrl) -or $databaseUrl -notmatch '^postgres(?:ql)?://') {
    throw "DATABASE_URL must be a PostgreSQL URL."
}

$databaseHost = Get-EnvValue -Lines $envLines -Name "DB_HOST"
if ([string]::IsNullOrWhiteSpace($databaseHost)) {
    $databaseHost = "localhost"
}
if ($databaseHost -eq "postgres") {
    $databaseHost = "localhost"
}

$databasePortText = Get-EnvValue -Lines $envLines -Name "DB_PORT"
$databasePort = 0
if (-not [int]::TryParse($databasePortText, [ref]$databasePort) -or
    $databasePort -lt 1 -or $databasePort -gt 65535) {
    throw "DB_PORT must be an integer between 1 and 65535."
}

if (-not (Test-NetConnection -ComputerName $databaseHost -Port $databasePort -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    throw "Cannot reach PostgreSQL at ${databaseHost}:$databasePort. Start the database with 'docker compose up -d postgres' and check DB_HOST/DB_PORT."
}

Write-Host "[OK] PostgreSQL is accepting TCP connections at ${databaseHost}:$databasePort."
Write-Host "The database check verifies network reachability only; it does not authenticate to PostgreSQL."
