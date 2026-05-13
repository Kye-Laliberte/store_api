
import reactLogo from'./assets/react.svg';
import viteLogo from './assets/vite.svg';
import heroImg from './assets/hero.png';
import './App.css';
import {  useState, useEffect } from 'react';

import { Routes, Route, useNavigate} from 'react-router-dom';
import OrderPage from './componets/OrderPage'; 
import CartPage from './componets/CartPage';
import AdminPage from './componets/AdminPage';  
import UserWidget from'./componets/UserWidget';

function  App() {
  const [showCart, setShowCart] = useState(false);
  const [user, setUser] = useState(null);
  
  const nav = useNavigate();
  return(
    <div>
      <h1>Store</h1>
        <p>sign in</p>
        <UserWidget
        user={user}
        setUser={setUser}
        onOpenCart ={()=> setShowCart(true)}
        />

        <CartPage useerId={user?.id}
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

  
