const BASE_URL = "http://localhost:8000";
const Cart_URL = `${BASE_URL}/carts`;


async function addToCart(item_id) {
    try{
        const response = await fetch(
            `${Cart_URL}/{user_id}/additem`,{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    item_id: item_id,
                    quantity: 1
                })
            }
        )
        const data= await response.json();
        console.log("Added:",data);

    }catch(err){
        console.error("error ading to cart ", e)
    }
    
   
} 
