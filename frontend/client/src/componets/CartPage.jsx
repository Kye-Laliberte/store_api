
//import reactLogo from './assets/react.svg';
//import viteLogo from './assets/vite.svg';
//import heroImg from './assets/hero.png';
//import './App.css';
import { getItem, getAllItems } from '../api/itemsClient';
import { useEffect, useState } from 'react';
import { useNavigate} from 'react-router-dom';


const Base_url="http://127.0.0.1:8000";
const Cart_URL = `${Base_url}/carts`;
const item_url =`${Base_url}/items`


export default function CartPage(){
    
    const [items, setItems]= useState([]);
    const nav = useNavigate();
    
    useEffect(()=>{
        fetch(`${item_url}/get_all`)
        .then( res=> res.json())
        .then(data=>{console.log("ITEMS:",data);
            setItems(data);})
    .catch(err => console.error(err));
    },[]);

    return(
        <div>
        <h2>Items</h2>
        {items.length===0 ? (
      <p> no items</p> 
    ) : ( 

    items.map(items=>(
      <div key={items.id}>
        <h3>{items.name}</h3>
        <p>{items.description}</p>
        <p>price {items.price}$</p>
        <p>{items.quantity} left</p>
        <button onClick={()=> addToCart(items.id)}>
            AddToCart</button>
      </div>
    ))
    )}
  </div>
        
       
        );
}
