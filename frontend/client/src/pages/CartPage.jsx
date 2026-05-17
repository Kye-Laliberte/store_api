
import api from '/src/api/axios';
import '/src/App.css';
import CartViewer from '/src/componets/cart_viewer';
import { getItem, getAllItems} from '/src/api/itemsClient';
import { addToCart,viewCart } from '/src/api/CartClient';
import { useEffect, useState } from 'react';
import { useNavigate} from 'react-router-dom';
import UserWidget from'/src/componets/UserWidget';
import {ItemList} from'/src/componets/cart_componets'
export default function CartPage(){
  /** prints a list of all the items in the database with at least 1 item.
   *  gives the user a input and button interface for each.
   * input for quantity and the button adds it to your cart.
   * most have cart for this to work
  */
const [items, setItems]= useState([]);
const [quantities, setQuantities] = useState({});
const [incart, setCart]= useState({});
// keeps the user_id up to date if its in localStorage




async function refresh() {
    try{
        const user_id=localStorage.getItem("user_id");
        const itemsData=await getAllItems();
        setItems(itemsData);
        if (user_id) {
            const cartData = await viewCart(user_id);
            
            setCart(cartData);
        }
    } catch (error) {
        console.error(
            "failed to refresh",
            error
        );   
    }
}


 useEffect(()=>{
  refresh();
 },[]);






function handleQuantityChange(itemId,value){
      if(!Number(value))
      {
        console.error("incorect data type",value)
      } 
      setQuantities((prev) => ({
            ...prev,[itemId]: value}));}
         

 async function handleAddToCart(item) {
        const user_id =
            localStorage.getItem("user_id");

        if (!user_id) {
            alert("sign in.");
            return;}

        const quantity = Number(quantities[item.id]);
        
            if (!quantity || quantity <= 0) {
              console.error("invalid quantity",quantity)
              alert("enter valid quantity");
              return;}

        try {const idata = await addToCart(
              user_id,item.id,quantity);

            if (idata){
                alert(`${idata.quantity} ${idata.name} now in your order`);}

        } catch (err) {
            console.error(err);
            alert("failed to add item");}
    }


  return(
      <div>
        <ItemList
        items={items}
        quantities={quantities}
        onQuantityChange={
          handleQuantityChange}
        onAddToCart={handleAddToCart}/>
        <CartViewer
        key={1}
        cart={incart}/>
      </div>
    )




/*

    return(
        <div>
          <h2>Items Available</h2>
        <div className='item-Display'>
          
        {items.length === 0 ? (
  <p>no items</p>
) : (
  items.map(item => (
    
    <div key={item.id} className='item-block'>
      <h3>{item.name}</h3>
      
      <input
        type="number"
        placeholder="quantity"
        value={quantities[item.id] ?? ""}
        onChange={(e) => setQuantities(prev=>({
            ...prev,[item.id]: e.target.value
          }))
          }/>

      <button onClick={() => ToCart(item)}
      className='basic-button'
      disabled={!Number(quantities[item.id]) || Number(quantities[item.id])<=0}>
        
        Add To Cart
      </button>

      <p>{item.description}</p>
      <p>price {item.price}$</p>
      <p>{item.quantity} left</p>
    </div>
  ))
)}
  </div> 
  </div>);
        
       
*/       
}
