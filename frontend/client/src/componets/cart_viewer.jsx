import api from '/src/api/axios';
import '/src/App.css';
import { useState, useEffect } from "react";
import { addToCart,viewCart } from '/src/api/CartClient';
import { useNavigate} from 'react-router-dom';


 export default function CartViewer({cart}){
    
    console.log("Cart-Items",cart) 
    if(Array.isArray(cart))
        alert("11111")
    return(
        <div>
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
    return(<div className='item-block'>
            <h4>{item.name}</h4>
            <p>{item.description}</p>
            <p>price {item.price}$</p>
            <p>{item.quantity}</p>
    </div>)
}


}

