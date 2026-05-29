import '/src/App.css';
import {  useState, useEffect } from 'react';

import { Routes, Route, useNavigate} from 'react-router-dom';
 
import CartPage from '/src/pages/CartPage';
import UserWidget from'/src/componets/UserWidget';

function  App() {
  const [user, setUser] = useState({id:null,email:null,cart_id:null,UserStatus:'inactive'});
  const [incart, setCart]= useState({});
  const nav = useNavigate();
  return(
    <div>
      <h1>Store</h1>
       
        <CartPage useerId={user?.id}
        incart={incart}
        setCart={setCart}
        user = {user}
        setUser={setUser}
        onClose={() => setShowCart(false)}
        />
      
    </div>
  );


 //<Route path="/cart" element={<CartPage/>}/>
 //<li><button onClick={() => nav("/cart")}>ShopPage</button></li> 
/*<Routes>
        <Route path="/" element={<CartPage/>}/>
        <Route path="/admin" element={<AdminPage/>}/>
        <Route path="/orders" element={<OrderPage/>}/>
      </Routes>
      

      <p>navigaton buttons</p>
      <nav>
      <li><button onClick={() => nav("/")}
        >ShopPage</button>
        </li> 
        <li><button onClick={() => nav("/orders")}
          >Orders</button></li>
        <li><button onClick={() => nav("/admin")}
          >Admin</button></li>
        
      </nav>*/
}
 export default App;

  
