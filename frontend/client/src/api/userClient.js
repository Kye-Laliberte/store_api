const BASE_URL = "http://localhost:8000";
const user_URL = `${BASE_URL}/users`;

export async function Emaillogin(email) {
  /** fetches the user info with email*/
  const response = await fetch(`${user_URL}/login`, {
    method: "POST",  
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });
 
  if (!response.ok){
    throw new Error("Faled to log in");
  }
  const data = await response.json();
  return data;
}

export async function getUser(user_id){
  /** retreves user info based on ther user_id*/
  try{
  const response = await fetch(`${user_URL}/${user_id}`,{
    method:"GET",
    headers:{ "Content-Type": "application/json" },
    });
    
 if( !response.ok){
      throw new Error("404, no user at that User_id");}
      const data = await response.json();
      return data;
}catch(error){
  console.error("Error fetching user", error);
        throw error;
}

}