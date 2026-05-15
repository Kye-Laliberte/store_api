
import api from '/src/api/axios';
import '/src/App.css';
import { getItem, getAllItems } from '/src/api/itemsClient';
import { addToCart,viewCart } from '/src/api/CartClient';
import { useEffect, useState } from 'react';
import { useNavigate} from 'react-router-dom';
import UserWidget from'/src/componets/UserWidget';

export default function CartPage(){
  /** prints a list of all the items in the database with at least 1 item.
   *  gives the user a input and button interface for each.
   * input for quantity and the button adds it to your cart.
   * most have cart for this to work
  */
const [items, setItems]= useState([]);
const [quantities, setQuantities] = useState({});
const [incart, setcartitem]= useState({});
const user_id=localStorage.getItem("user_id");
// keeps the user_id up to date if its in localStorage
    useEffect(()=>{
    async function lodeCart(){
      try{
        
        //if(user_id){
          const data = await viewCart(user_id);
          setCart(data);//}
      }catch(error){
        console.error("faled to lode cart",error)}
    } 
  })

    useEffect(()=>{
      /** fetches a list[] of items and set it to items*/
      getAllItems()
      .then(data=>{console.log("ITEMS:",data);
      setItems(data);})
    .catch(err => console.error(err));
    },[]);
    
async function ToCart(item){
      /** sends the given items_id to addToCart().js to add the quantity in the input field */
      const user_id=localStorage.getItem("user_id");
      if(!user_id )
          {alert("sign in.");
            return;
          }
      const quantity = Number(quantities[item.id]);
      try{
      const  data= await addToCart(user_id,item.id,quantity);

      }catch(err){
      console.error(err);
      alert("failed to add item");
      }
    };
    
    function ProductCard({
    item,quantity,
    onQuantityChange,onAddToCart}) {
    return (
        <div className="item-block">
            <h3>{item.name}</h3>
            <input
                type="number"
                inputMode="numeric"
                min="1"
                placeholder="quantity"
                value={quantity ?? ""}
                onChange={(e) =>
                    onQuantityChange(
                        item.id,
                        e.target.value
                    )}/>
            <button
                className="basic-button"
                onClick={() => onAddToCart(item)}
                disabled={!Number(quantity) || Number(quantity) <= 0}>
                Add To Cart</button>
              <p>{item.description}</p>
            <p>price {item.price}$</p>
            <p>{item.quantity} left</p></div>
);
}

    function ItemList({
    items,quantities,
    onQuantityChange,onAddToCart}) {
    if (items.length === 0) {
        return <p>no items</p>;
    }
    return (
        <div className='item-Display'>

            {items?.map((item) => (
                <ProductCard
                    key={item.id}
                    item={item}
                    quantity={quantities[item.id]}
                    onQuantityChange={onQuantityChange}
                    onAddToCart={onAddToCart}
                />))}
        </div>
    );
}
function handleQuantityChange(itemId,value){
        setQuantities((prev) => ({
            ...prev,[itemId]: value}));}

 async function handleAddToCart(item) {
        const user_id =
            localStorage.getItem("user_id");

        if (!user_id) {
            alert("sign in.");
            return;}

        const quantity = Number(quantities[item.id]);
        
            if (!quantity || quantity <= 0) {
              alert("enter valid quantity");
              return;}

        try {
            const idata = await addToCart(
              user_id,item.id,quantity);

            if (idata){
                alert(`${idata.quantity} ${idata.name} now in your order`);}

        } catch (err) {
            console.error(err);
            alert("failed to add item");}
    }


  return(
      <div>
        <ItemList
        items={items}
        quantities={quantities}
        onQuantityChange={
          handleQuantityChange}
        onAddToCart={handleAddToCart}/>
      </div>
    )




/*

    return(
        <div>
          <h2>Items Available</h2>
        <div className='item-Display'>
          
        {items.length === 0 ? (
  <p>no items</p>
) : (
  items.map(item => (
    
    <div key={item.id} className='item-block'>
      <h3>{item.name}</h3>
      
      <input
        type="number"
        placeholder="quantity"
        value={quantities[item.id] ?? ""}
        onChange={(e) => setQuantities(prev=>({
            ...prev,[item.id]: e.target.value
          }))
          }/>

      <button onClick={() => ToCart(item)}
      className='basic-button'
      disabled={!Number(quantities[item.id]) || Number(quantities[item.id])<=0}>
        
        Add To Cart
      </button>

      <p>{item.description}</p>
      <p>price {item.price}$</p>
      <p>{item.quantity} left</p>
    </div>
  ))
)}
  </div> 
  </div>);
        
       
*/       
}
