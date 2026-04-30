import { cache } from "react";

const BASE_URL = "http://localhost:8000";
const Cart_URL = `${BASE_URL}/carts`;


export async function addToCart(user_id,item_id,quantity) {
    /**  adds quantity of item_id to user_id cart and returns the cartItem info*/
    try{
        const out= await fetch(
            `${Cart_URL}/${user_id}/additem`,{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({             
                    item_id,
                    quantity
                })});
    if (!out.ok) {
      throw new Error("failed request");
    }
    return await out.json();
    }catch(err){
        console.error("error adding item to cart ", err)
        throw err;
    }
}    
export async function viewCart(user_id) {
    /**not tested should return a list[] of Items object in user_ids cart*/
    try{
        const respon= await fetch(
            `${Cart_URL}/${user_id}/viewcart`,{
                method: "get",
                headers: {"Content-Type": "application/json"},
               });
    if (respon==HTMLOutputElement.arguments(400))
        {console.error()}

    if (!respon.ok) {
      throw new Error("failed request");
    }
    return await respon.json();    
    }catch(err){
        console.error("failed to find cart",err)
    }
    
}
   
export async function addCart(user_id){
    try{
        const cart = await fetch(
        `${Cart_URL}/${user_id}/newcart`,{
        method: "post",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id,
            user_id,
            purchase_dat
        })});
        
    if (!respon.ok) {
      throw new Error("failed request");
    }
    return await cart.json
    }catch(err){
        console.error("failed to add cart", err)
    }
    
} 
