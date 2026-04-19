import { useState, useEffect } from "react";
import {Emaillogin} from '../api/userClient';
const BASE_URL = "http://localhost:8000";
const user_URL = `${BASE_URL}/users`;

export default function UserWidget() {
const [ userId, setUserId] = useState("");
const user_id = localStorage.getItem("user_id");    
const [ email, setEmail] = useState("");
// load saved user on page load
   useEffect(() => {
    const saved = localStorage.getItem("user_id");
    if (saved !== null)
         {setUserId(saved)};
    
  }, []);
    
    
    function SaveData() {
    if (!userId) {
      alert("Enter a user id");
      return;
    }
    localStorage.setItem("user_id", userId);
    alert(`User set to ${userId}`);
    }
    
    async function inmail(){
    if (!email){
        alert("Enter your email to sign in");
        return;
    }
    try{
        const data = await Emaillogin(email);
        localStorage.setItem("user_id", data.id);
        if (!data || !data.id) {
        alert("Invalid email");
        return;
      }
       setUserId(data.id);
       
      alert(`User set to ${data.id}`);
    }catch (err) {
      console.error(err);
      alert("Login failed");    
    }
    localStorage.setItem("user_id", userId);
    }

  return (
    <div style={{ marginBottom: "20px" }}>
      <input
        type="number"
        placeholder="User ID"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
      />
      <button onClick={SaveData}>Set User</button>
      
      <input
        type="text"
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
    <button onClick={inmail}>Set User by email</button>

    </div>
  );
}