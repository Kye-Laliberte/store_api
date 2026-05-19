import { useState, useEffect } from "react";
import {Emaillogin,getUser} from '/src/api/userClient';
import api from '/src/api/axios';
import '/src/App.css';

export default function UserWidget({user,setUser,ref}) {
/**a basic log_in system to get the user_id.
 * you can do it with email, or user_id
 * B aware this is a Local storage set up so you have to put ina id or email firt.
 *  */ 
const [ userId, setUserId] = useState("");
const [ email, setEmail] = useState("");
 
    //for testing put in user id th sign in
    async function SaveData() {
      
      const data= await getUser(userId)
      
      if(!data){
        alert(`no user at ${userId}`);
        return;
      }
      
      console.log("data",data) 
      await ref(data);  
      console.log(user) 
      
    }

    // this is for email sign in will ad pasword in at a later time
    async function inmail(){
    try{
        const data = await Emaillogin(email);
        if (!data) {
        alert("Invalid email");
        return;
      }
        
      alert(`User set to ${data.id}`);
      ref(data);
    }catch (err) {
      console.error(err);
      alert("Login failed");    
    }}

  return (
  
    <div style={{ marginBottom: "20px" }}>
      
      <input
        type="number"
        placeholder="user_id"
        value={userId ?? ""}
        
        onChange={(g) => {setUserId( g.target.value)}}
          
      />
      <button
      onClick={() => {SaveData()}
      } className='button2'
      disabled={!Number(userId)} 
      
      >Set User</button>
      
      <p></p>
     
     <input
      
        type="text"
        placeholder="email"
        value={email ?? ""}
        
        onChange={(e) => {setEmail( e.target.value)}}
      />
    <button onClick={() => inmail()}
    className='button2'
    disabled={!email}
    >Set User by email
      
    </button>

    </div>
  );
}