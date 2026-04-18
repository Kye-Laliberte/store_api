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
async function login(email) {
  const res = await fetch("http://127.0.0.1:8000/login", {
    method: "POST",  
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });

  const data = await res.json();
  localStorage.setItem("user_id", data.user_id);
}