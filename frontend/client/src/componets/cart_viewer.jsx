import api from '/src/api/axios';
import '/src/App.css';
import { useState, useEffect } from "react";
import { addToCart,viewCart,removeFromCart,deleatCart } from '/src/api/CartClient';
import {order_Cart} from '/src/api/orderClient'
import { useNavigate} from 'react-router-dom';
import CartWindow from './orderWidget';



function LeaveCart({user, dropcart}){
        return ( 
        <div>
            <h4>remove cart</h4>
            <button
            className='button2'
            disabled ={!user?.cart_id}
            onClick={() => dropcart(user)}
            >deleate cart</button>
            
        </div>);
    }

 export default function CartViewer({cart,user,refresh,dropcart}){
    
    if(!user?.id){
         return(<p>not loged in</p>);
            }
    if(!user?.cart_id){
            return(<div>
                <h3>no cart</h3>
            </div>);
           }
    
    return(
        <div>
            <LeaveCart
        user={user}
        dropcart={dropcart}/>
             
        <div className='cart-window'>
                                    
        <CartWindow user={user} refresh={refresh}/>

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
        </div>
    );

    async function remove_item({item,user}){
        await removeFromCart(user,item.item_id)
        
        await refresh(user)
    }
    
    function CartItems({item}){
    return(<div className='cart-items'>
            <h4>{item.name}</h4>
            <p>{item.description}</p>
            <p>{item.quantity} in Cart </p>
            <p>total cost:{item.totalprice}</p>
            <button className='button2' disabled={!item.item_id} 
            onClick={ ()=> remove_item({item:item,user:user},refresh)}>leave item</button>
            
    </div>)
}


}

