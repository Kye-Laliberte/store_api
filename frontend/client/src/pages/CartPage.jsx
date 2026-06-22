
import api from '/src/api/axios';
import '/src/App.css';
import CartViewer from '/src/componets/cart_viewer';
import { getItem, getAllItems} from '/src/api/itemsClient';
import { addToCart,viewCart,deleatCart,new_Cart} from '/src/api/CartClient';
import { useEffect, useState } from 'react';
import { useNavigate} from 'react-router-dom';
import UserWidget from'/src/componets/UserWidget';
import {ItemList} from'/src/componets/cart_componets'
import { getUser } from '/src/api/userClient';


export default function CartPage({user,setUser,incart,setCart}){
  /** prints a list of all the items in the database with at least 1 item.
   *  gives the user a input and button interface for each.
   * input for quantity and the button adds it to your cart.
   * most have cart for this to work
  */
const [items, setItems]= useState([]);
const [quantities, setQuantities] = useState({});
const [refreshKey, setRefreshKey] = useState(0);

const trigger_refresh=()=>{
    setRefreshKey(k => k + 1);
}

function Log_Out({setUser}){
setUser(null)
return(
<button onClick={() => logout(setUser)}>
  Logout
</button>
);
}

async function refreshUser(user_id){
    setUser(await getUser(user_id));
}

async function refreshCart(user){
    if(user?.cart_id){
        setCart(await viewCart(user.id,user.cart_id)); 
    }else{console.warn("no cart")}
    
}

async function refreshItems(){
    setItems(await getAllItems());
}


async function refresh(user){
    await refreshItems();
    if(user?.id){
        refreshUser(user.id);
        refreshCart(user);        
    }
    
}

async function refresh2(user) {
    try{
        const itemsData= await getAllItems();        
        setItems(itemsData);
        console.log("ITEMS",itemsData);
        console.log("USER",user);
        if(user?.id)
            {
             const users = await getUser(user.id)
                setUser(users)
                

            if (users?.cart_id){
                const cartData = await viewCart(users.id);
                setCart(cartData);
                console.log("cartItem",cartData) 
            }
            else{
                console.warn("No cart"); 
            } 
        }else{
            console.warn("No user_id");
        }
         
    }catch (error) {
        console.error("failed to refresh",error);
    }}
 
    useEffect(()=>{
  refresh(user);
 },[]);

async function handle_cartRemovel(User){
    if (!User?.cart_id){
        alert("No active cart")
        return;}
        try{
            await deleatCart(User.id,User.cart_id)         
            await refresh(User)
        } catch(err){
            console.error(err);
            alert("failed to drop cart");
        }
}

async function handleNewCart(User){
    if(!User?.id){
        alert("not signed in")
        return;}
   
    try{
        
       const cart =await new_Cart(User.id)
        await refresh(User)
        return cart
    } catch(error){
        console.error(error);
        alert("faled to create new cart")
    }

}

function handleQuantityChange(itemId,value){  
    
      setQuantities((prev) => ({
            ...prev,[itemId]: Number(value)}));}
         

 async function handleAddToCart(item) {
        
        if (!user) {
            alert("sign in.");
            return;}
        
        const quantity = Number(quantities[item.id]);
        
            if (!quantity || quantity <= 0) {
              console.error("invalid quantity",quantity)
              alert("enter valid quantity");
              return;}
        try {
        
        if (!user?.cart_id){
            
            alert("adding new cart")
            
            const cart = await handleNewCart(user)
            const  idata = await addToCart(user.id,item.id,quantity,cart.id)
        }else{
            const idata = await addToCart(user.id,item.id,quantity,user.cart_id);
        }
            
                await refresh(user);

        } catch (err) {
            console.error(err);
            alert("failed to add item");}
    }


  return(
      <div>

         <p>sign in</p>
        <UserWidget
        
        user={user}
        setUser={setUser}
        refresh={refresh}
        onOpenCart ={()=> setShowCart(true)}
        />
        
        <ItemList
        key={2}
        items={items}
        user={user}
        quantities={quantities}
        onQuantityChange={handleQuantityChange}
        onAddToCart={handleAddToCart}
        newCart={handleNewCart}
        />

        <CartViewer
        key={1}
        user={user}
        cart={incart}
        refresh={refresh}
        dropcart={handle_cartRemovel}
        new_Cart={handleNewCart}/>

      </div>
    )

}
