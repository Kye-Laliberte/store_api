
import api from '/src/api/axios';
import '/src/App.css';
import CartViewer from '/src/componets/cart_viewer';
import { getItem, getAllItems} from '/src/api/itemsClient';
import { addToCart,viewCart } from '/src/api/CartClient';
import { useEffect, useState } from 'react';
import { useNavigate} from 'react-router-dom';
import UserWidget from'/src/componets/UserWidget';
import {ItemList} from'/src/componets/cart_componets'
import { getUser } from '../api/userClient';
export default function CartPage({user,setUser,incart,setCart}){
  /** prints a list of all the items in the database with at least 1 item.
   *  gives the user a input and button interface for each.
   * input for quantity and the button adds it to your cart.
   * most have cart for this to work
  */
const [items, setItems]= useState([]);
const [quantities, setQuantities] = useState({});
// keeps the user_id up to date if its in localStorage


async function refresh(User) {
    try{
        const itemsData= await getAllItems();        
        setItems(itemsData);
        console.log("ITEMS",itemsData)
        console.log("USER",User)
        if(User.id??0)
            {
             const users = await getUser(User.id)
                setUser(users)
                

            if (users.cart_id){
                const cartData = await viewCart(users.id);
                setCart(cartData);
                console.log("cartItem",cartData) 
            }
            else{
                alert("no cart");
                setCart(null) 
            } 
        }else{
            alert("no user_id")
        }
         
    }catch (error) {
        console.error(
            "failed to refresh",
            error
        );   
    }
}
 useEffect(()=>{
  refresh(user);
 },[]);


function handleQuantityChange(itemId,value){  
    
      setQuantities((prev) => ({
            ...prev,[itemId]: Number(value)}));}
         

 async function handleAddToCart(item) {
        
        if (!user) {
            alert("sign in.");
            return;}
        if (!user.cart_id){
            alert("No active cart")
            return;
        }

        const quantity = Number(quantities[item.id]);
        
            if (!quantity || quantity <= 0) {
              console.error("invalid quantity",quantity)
              alert("enter valid quantity");
              return;}

        try {const idata = await addToCart(
              user.id,item.id,quantity);

            if (idata){
                alert(`${idata.quantity} ${idata.name} now in your order`);}
            
                await refresh(user);

        } catch (err) {
            console.error(err);
            alert("failed to add item");}
    }


  return(
      <div>

         <p>sign in</p>
        <UserWidget
        key={2}
        user={user}
        setUser={setUser}
        ref={refresh}
        onOpenCart ={()=> setShowCart(true)}
        />
        
        <ItemList
        items={items}
        user={user}
        quantities={quantities}
        onQuantityChange={handleQuantityChange}
        onAddToCart={handleAddToCart}/>
        <CartViewer
        user={user}
        cart={incart}
        ref={refresh}/>
      </div>
    )


}
