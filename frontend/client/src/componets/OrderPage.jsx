import { useState } from 'react';
//import reactLogo from './assets/react.svg';
//import viteLogo from './assets/vite.svg';
//import heroImg from './assets/hero.png';
//import './App.css';
//import { getItem } from '/api/itemsClient';
import { useEffect } from 'react';
import { useNavigate} from 'react-router-dom';
import UserWidget from'../componets/UserWidget';
//<button onClick={()=> nav("/")}>Home</button>
export default function OrderPage(){
    const nav = useNavigate();
    return(
        <div>
            <h2>Order</h2>
            <p>View your orders</p>
            
        </div>
    )
    
}