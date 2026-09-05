import api from "./axios";

export async function Emaillogin(email, password) {
  /** Logs in and stores the bearer token for subsequent API calls. */
  try {
    const response = await api.post(`/users/login`, { email, password });
    const data = response.data;
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("store_user", JSON.stringify(data));
    return data;
  } catch (error) {
    console.error("Error logging in:", error);
    throw error;
  }
}

export async function register(email, password) {
  const response = await api.post("/users/addUser", null, {
    params: { email, password },
  });
  return Emaillogin(email, password);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("store_user");
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
    const respon = await api.put(`/users/${user_id}/status`, null, { params: { status } });
    return respon.data;
  } catch (error) {
    console.error("failed to change user status", error);
    throw error;
  }
}
