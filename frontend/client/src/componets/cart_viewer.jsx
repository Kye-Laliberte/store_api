import api from '/src/api/axios';
import '/src/App.css';
import { useState, useEffect } from "react";
import { addToCart,viewCart } from '/src/api/CartClient';
import {order_Cart} from '/src/api/orderClient'
import { useNavigate} from 'react-router-dom';


 export default function CartViewer({cart,user,ref}){
    if(user.id==undefined){
         return(<p>not loged in</p>);
            }
        console.log("USER",user.cart_id)
    if(user.cart_id==null){
            return(<div>
                <h3>no cart</h3>
            </div>);
           }
    
    return(
            
        <div className='cart-window'>
            <h3>Your Cart</h3>       
           

            <button
           onClick={()=>order_Cart( user={user},ref={ref})}
           className='button2'
           disabled={user.user_status != 'active'}>
            order cart
           </button>

            { Array.isArray(cart) && cart.length>0 ? ( 
                cart.map( (item) => (
                    <CartItems 
                    key={item.item_id}
                    item={item}/>
                ))

            
            
            ) : ( 
                <p>Cart empty</p>
                
            )}
        </div>
    );
    
    function CartItems({item}){
    return(<div className='cart-items'>
            <h4>{item.name}</h4>
            <p>{item.description}</p>
            <p>{item.quantity} in Cart </p>
            <p>total cost:{item.totalprice}</p>
    </div>)
}


}

