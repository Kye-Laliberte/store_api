const BASE_URL = "http://localhost:8000";
const user_URL = `${BASE_URL}/users`;

export async function Emaillogin(email) {
  const res = await fetch(`${user_URL}/login`, {
    method: "POST",  
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });
 
  if (!res.ok){
    throw new Error("Faled to log in");
  }
  const data = await res.json();
  return data;
}