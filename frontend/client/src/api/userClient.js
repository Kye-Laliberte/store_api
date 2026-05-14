import api from "./axios";
const BASE_URL = "http://localhost:8000";
const user_URL = `${BASE_URL}/users`;

export async function Emaillogin(email) {
  /** fetches the user info with email*/
  const response = await api.post(`/users/login`, {
    email:email
  });
  try{
  const data = response.data;
  if (data.cart_id==null)
    alert("a cart is needed before you can shop")
  return data;
}catch(error){
  console.error("Error logging in:", error);
    throw error;
}
}  


export async function getUser(user_id){
  /** retreves user info based on ther user_id*/
  try{
  const response = await api.get(
    `/users/${user_id}`,
    {user_id:user_id});
    
    return response.data;

}catch(error){
  console.error("Error fetching user", error);
    throw error;
}

}