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
                })
            }
        );
    if (!response.ok) {
      throw new Error("failed request");
    }
    return await response.json();
    }catch(err){
        console.error("error adding item to cart ", err)
        throw err;
    }
    
   
} 
