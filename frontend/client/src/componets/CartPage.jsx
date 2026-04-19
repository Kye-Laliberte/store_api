
//import reactLogo from './assets/react.svg';
//import viteLogo from './assets/vite.svg';
//import heroImg from './assets/hero.png';
//import './App.css';
import { getItem, getAllItems } from '../api/itemsClient';
import { addToCart } from '../api/CartClient';
import { useEffect, useState } from 'react';
import { useNavigate} from 'react-router-dom';
import UserWidget from'../componets/UserWidget';

const Base_url="http://127.0.0.1:8000";
const Cart_URL = `${Base_url}/carts`;
const item_url =`${Base_url}/items`


export default function CartPage(){
const [items, setItems]= useState([]);
const [quantities, setQuantities] = useState({});

  useEffect(() => {
      const saved = localStorage.getItem("user_id");
      if (saved == null)
        {alert.CartPage("curent no user_id")};

    }, []);

    async function ToCart(item){
      const user_id=localStorage.getItem("user_id");
      if(!user_id )
          {alert("sign in.");
            return;}
      const quantity = quantities[item.id];

    if (!quantity || quantity <= 0) {
      alert("enter a valid quantity");
      return;
      }
      
      try{
      const  data= await addToCart(user_id,item.id,quantity)
      
      if(data)
        alert(`added item ${data.name} to your order`)
      
      }catch(err){
      console.error(err);
      alert("failed to add item");
      }

    }
    
    useEffect(()=>{
        fetch(`${item_url}/get_all`)
        .then( res=> res.json())
        .then(data=>{console.log("ITEMS:",data);
            setItems(data);})
    .catch(err => console.error(err));
    },[]);
    

    return(
        
        <div>
          <p>sign in</p> 
          <UserWidget/>
        <h2>Items</h2>
       
        {items.length === 0 ? (
  <p>no items</p>
) : (
  items.map(item => (
    <div key={item.id}>
      <h3>{item.name}</h3>

      <input
        type="number"
        placeholder="quantity"
        value={quantities[item.id] || ""}
        onChange={(e) =>
          setQuantities({
            ...quantities,
            [item.id]: e.target.value
            
          })
        }
      />

      <button onClick={() => ToCart(item)}>
        Add To Cart
      </button>

      <p>{item.description}</p>
      <p>price {item.price}$</p>
      <p>{item.quantity} left</p>
    </div>
  ))
)}
  </div> );
        
       
       
}
