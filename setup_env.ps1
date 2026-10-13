$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repositoryRoot = $PSScriptRoot
$envPath = Join-Path $repositoryRoot ".env"

if (Test-Path -LiteralPath $envPath) {
    throw ".env already exists. It was left unchanged to protect your database credentials and JWT key."
}

function Read-Setting {
    param(
        [string]$Prompt,
        [string]$Default
    )

    $answer = Read-Host "$Prompt [$Default]"
    if ([string]::IsNullOrWhiteSpace($answer)) {
        return $Default
    }
    return $answer.Trim()
}

function New-UrlSafeSecret {
    param([int]$ByteCount)

    $randomBytes = New-Object byte[] $ByteCount
    $randomNumberGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $randomNumberGenerator.GetBytes($randomBytes)
    }
    finally {
        $randomNumberGenerator.Dispose()
    }

    return [Convert]::ToBase64String($randomBytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

$postgresUser = Read-Setting -Prompt "PostgreSQL user" -Default "store_api"
if ($postgresUser -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
    throw "PostgreSQL user must only uses number and letters, and cannot start with a digit."
}

$postgresDatabase = Read-Setting -Prompt "PostgreSQL database" -Default "store_db"
if ($postgresDatabase -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
    throw "PostgreSQL database must only uses number and letters, and cannot start with a number."
}

$postgresHost = Read-Setting -Prompt "PostgreSQL host for local connections" -Default "localhost"
if ($postgresHost -notmatch '^[A-Za-z0-9.-]+$') {
    throw "PostgreSQL host may contain only letters, digits, dots, and hyphens."
}

$databasePortText = Read-Setting -Prompt "PostgreSQL host port" -Default "5432"
$databasePort = 0
if (-not [int]::TryParse($databasePortText, [ref]$databasePort) -or
    $databasePort -lt 1 -or $databasePort -gt 65535) {
    throw "PostgreSQL port must be an integer between 1 and 65535."
}

$frontendPortText = Read-Setting -Prompt "Frontend port" -Default "5173"
$frontendPort = 0
if (-not [int]::TryParse($frontendPortText, [ref]$frontendPort) -or
    $frontendPort -lt 1 -or $frontendPort -gt 65535) {
    throw "Frontend port must be an integer between 1 and 65535."
}

$postgresPassword = New-UrlSafeSecret -ByteCount 32
$jwtSecret = New-UrlSafeSecret -ByteCount 48
$databaseUrl = "postgresql://${postgresUser}:${postgresPassword}@${postgresHost}:${databasePort}/${postgresDatabase}"

$envContents = @(
    "POSTGRES_USER=$postgresUser"
    "POSTGRES_PASSWORD=$postgresPassword"
    "POSTGRES_DB=$postgresDatabase"
    "DB_HOST=$postgresHost"
    "DB_PORT=$databasePort"
    "DATABASE_URL=$databaseUrl"
    "JWT_SECRET_KEY=$jwtSecret"
    "FRONTEND_PORT=$frontendPort"
)

$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($envPath, $envContents, $utf8WithoutBom)

Write-Host "Created repository-root .env with generated database and JWT secrets."
Write-Host "Keep .env private and untracked. Start PostgreSQL and run .\security_test.ps1 to check the database connection and JWT key."
