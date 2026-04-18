
//import reactLogo from './assets/react.svg';
//import viteLogo from './assets/vite.svg';
//import heroImg from './assets/hero.png';
//import './App.css';
//import { getItem } from './api/itemsClient';
import { useEffect } from 'react';
//import { getAllItems } from './api/itemsClient';
import { useNavigate} from 'react-router-dom';

export default function CartPage(){
    const nav = useNavigate();
    return(
        <div><h2>Shop</h2>
        <p>brouse items</p>
        <button onClick={()=> nav("/")}>Home</button>
        </div>
        );
}
