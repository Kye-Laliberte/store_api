import { useState } from "react";
import { Emaillogin, register, logout } from '/src/api/userClient';
import '/src/App.css';

export default function UserWidget({user,setUser,refresh}) {
/**a basic log_in system to get the user_id.
 * you can do it with email, or user_id
 * B aware this is a Local storage set up so you have to put ina id or email firt.
 *  */ 
const [ email, setEmail] = useState("");
const [ password, setPassword] = useState("");
const [ isRegistering, setIsRegistering] = useState(false);
 
    //for testing put in user id th sign in
    async function inmail(){
    try{
        const data = isRegistering
          ? await register(email, password)
          : await Emaillogin(email, password);
        if (!data) {
        console.error("Authentication failed");
        return;
      }
      setUser(data);
      await refresh(data);
    }catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;
      alert(detail || (isRegistering ? "Registration failed" : "Login failed"));
    }}

    function signOut() {
      logout();
      setUser(null);
    }

  return (
  
    <div style={{ marginBottom: "20px" }}>
     
      {!user?.id ? <p>not logged in</p> : <p>current user: {user.email}</p>}
     
     <input
        type="text"
        placeholder="email"
        value={email ?? ""}
        
        onChange={(e) => {setEmail( e.target.value)}}
      />
    <input
        type="password"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
    <button onClick={inmail}
    className='button2'
    disabled={!email || !password}
    >{isRegistering ? "Register" : "Log in"}
    </button>
    <button onClick={() => setIsRegistering((value) => !value)} className='button2'>
      {isRegistering ? "Have an account?" : "Create account"}
    </button>
    {user?.id && <button onClick={signOut} className='button2'>Log out</button>}
      
    </div>
  );
}