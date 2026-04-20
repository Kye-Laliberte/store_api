import { cache } from "react";

const BASE_URL = "http://localhost:8000";
const Cart_URL = `${BASE_URL}/carts`;


export async function addToCart(user_id,item_id,quantity) {
    try{
        const response = await fetch(
            `${Cart_URL}/${user_id}/additem`,{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({             
                    item_id,
                    quantity
                })});
    if (!response.ok) {
      throw new Error("failed request");
    }
    return await response.json();
    }catch(err){
        console.error("error adding item to cart ", err)
        throw err;
    }
}    
export async function viewCart(user_id) {
    try{
        const respon= await fetch(
            `${Cart_URL}/${user_id}/viewcart`,{
                method: "get",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    item_id,
                    name,
                    price,
                    quantity,
                    description
                })});
    if (!respon.ok) {
      throw new Error("failed request");
    }
    return await respon.json();    
    }catch(err){
        console.error("failed to find cart")
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
    return await cart.json
    }catch(err){
        console.error("failed to add cart")
    }
    
} 
