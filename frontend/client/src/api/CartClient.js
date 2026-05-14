import { cache} from "react";
import api from "./axios";



export async function addToCart(user_id,item_id,quantity) {
    /**  adds quantity of item_id to user_id cart and returns the cartItem info*/
    try{
        const out= await api.post(
            `carts/${user_id}/additem`,
            {item_id:item_id,quantity:quantity});
        if(out.status !== 200){
            throw new Error(`Failed to add item to cart: ${out.statusText}`);
        }
    return out.data;
    }catch(err){
        console.error("error adding item to cart ", err)
        throw err;
    }
}    
export async function viewCart(user_id) {
    /**not tested should return a list[] of Items object in user_ids cart*/
    try{
        const respon= await api.get(`/carts/${user_id}/viewcart`);
        if(respon.status !== 200){
            throw new Error(`Failed to view cart: ${respon.statusText}`);
        }
    return respon.data;
    }catch(err){
        console.error("failed to find cart",err)
        throw err;
    }
}
   
export async function addCart(user_id){
    /** creates a new cart for user_id and returns the cart info */
    try{
        const cart = await api.post(
            `/carts/${user_id}/newcart`,{
            id: user_id,
            cart_date: new Date()});
    
            if(cart.status !== 200){
            throw new Error(`Failed to remove item from cart: ${cart.statusText}`);}

            return await cart.data;
    }catch(err){
        console.error("failed to add cart", err)
        throw err;
    }
} 

export async function removeItemFromCart(user_id,item_id){
    try{
        const response=await api.delete(`/carts/${user_id}/removeitem`,{data:{item_id:item_id}});
        
        if(response.status !== 200){
            throw new Error(`Failed to remove item from cart: ${response.statusText}`);
        }
        return response.data;
    
    }catch(err){
        console.error("failed to remove item from cart", err)

        throw err;
    }    
}