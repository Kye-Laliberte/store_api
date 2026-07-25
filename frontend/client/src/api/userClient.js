import api from "./axios";

export async function Emaillogin(email) {
  /** fetches the user info with email*/
  try {
    const response = await api.post(`/users/login`, { email });
    const data = response.data;
    if (data.cart_id == null) {
      alert("A cart is needed before you can shop");
    }
    return data;
  } catch (error) {
    console.error("Error logging in:", error);
    throw error;
  }
}

export async function getUser(user_id){
  /** retreves user info based on ther user_id*/
  try{
  const response = await api.get(`/users/${user_id}`);

    if(response.data.user_status != "active"){
      console.warn("inactive user",response.data)}

    return response.data;

}catch(error){
  console.error("Error fetching user", error);
    throw error;
}

}

export async function UserStatus(user_id, status = 'active') {
  try {
    const respon = await api.put(`/users/${user_id}/status`, { status });
    return respon.data;
  } catch (error) {
    console.error("failed to change user status", error);
    throw error;
  }
}
