import { useState, useEffect } from "react";
import {Emaillogin,getUser} from '../api/userClient';
const BASE_URL = "http://localhost:8000";
const user_URL = `${BASE_URL}/users`;
import '../App.css';
export default function UserWidget() {
/**a basic log_in system to get the user_id.
 * you can do it with email, or user_id
 * B aware this is a Local storage set up so you have to put ina id or email firt.
 *  */ 
const [ userId, setUserId] = useState("");
const user_id = localStorage.getItem("user_id");    
const [ email, setEmail] = useState("");
const [user, setUser] = useState("");
// load saved user on page load
   useEffect(() => {
    const saved = localStorage.getItem("user_id");
    if (saved !== null)
         {setUserId(saved)
        
         };
        
  }, []);
    
    //for testing put in user id th sign in
    async function SaveData() {
      const id= await getUser(userId)
      if(!id){
        alert(`no user at ${userId}`);
        return;
      }
      
      localStorage.setItem("user_id", userId);
      alert(`User set to ${userId}`);
    }

    // this is for email sign in will ad pasword in at a later time
    async function inmail(e){
    
    try{
        const data = await Emaillogin(email);
        localStorage.setItem("user_id", data.id);
        if (!data) {
        alert("Invalid email");
        return;
      }
       
       
      alert(`User set to ${data.id}`);
    }catch (err) {
      console.error(err);
      alert("Login failed");    
    }
    localStorage.setItem("user_id", data.id);//will set to just data, temporary for testing
    }

  return (
    
    <div style={{ marginBottom: "20px" }}>
      <input
        type="number"
        placeholder="user_id"
        value={userId ?? ""}
        
        onChange={(g) => setUserId( g.target.value)}
          
      />
      <button
      onClick={() => SaveData()
      } className='button2'
      disabled={!userId} 
      
      >Set User</button>
      
      <p></p>
     
     <input
      
        type="text"
        placeholder="email"
        value={email ?? ""}
        
        onChange={(e) => setEmail( e.target.value)}
      />
    <button onClick={() => inmail()}
    className='button2'
    disabled={!email}
    >Set User by email
      
    </button>

    </div>
  );
}