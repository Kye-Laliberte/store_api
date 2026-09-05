import '/src/App.css';
import { useState } from 'react';
 
import CartPage from '/src/pages/CartPage';

function  App() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('store_user')) || null;
    } catch {
      return null;
    }
  });
  const [incart, setCart]= useState({});
  return(
    <div>
      <h1>Store</h1>
       
        <CartPage useerId={user?.id}
        incart={incart}
        setCart={setCart}
        user = {user}
        setUser={setUser}
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

  
