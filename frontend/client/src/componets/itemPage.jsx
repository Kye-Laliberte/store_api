//import { useState } from 'react';
//import reactLogo from './assets/react.svg';
//import viteLogo from './assets/vite.svg';
//import heroImg from './assets/hero.png';



import { useEffect } from 'react';
import { getAllItems,getItem } from './api/itemsClient';

function itemAPP()
    {
    const [items, setItems] = useState([]);

  
  useEffect(() => {
  getAllItems().then(data => {
        console.log("Items:", data);
        setItems(data); 
      })
      .catch(err => console.error(err));
  }, []);
 

  // check if items are loaded
  if (items.length === 0) {
    return <p>Loading items...</p>;
  }

  if (items.error) {
    return <p>Error: {items.error}</p>;
  }
  //if (!items.id)
  //  return<p>404 not found</p>
  
  return ( 
  <div>
    <h1>Items</h1>
    {items.length===0 ? (
      <p> no items</p> 
    ) : ( 
    items.map(items=>(
      <div key={items.id}>
        <h3>{items.name}</h3>
        <p>{items.description}</p>
        <p>{items.price}</p>
        <p>{items.quantity}</p>
      </div>
    ))
    )}
  </div>
);
}
  
export default APP;