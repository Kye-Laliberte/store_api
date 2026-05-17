import api from '/src/api/axios';
import '/src/App.css';
import { useState, useEffect } from "react";
import { addToCart,viewCart } from '/src/api/CartClient';
import { useNavigate} from 'react-router-dom';


 export default function CartViewer({cart}){
    
    
    return(
        <div className='cart-window'>
            <h3>Your Cart</h3>
           

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

