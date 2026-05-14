import api from "/src/api/axios"


export async function order_Cart(user_id) {
    try{
    const out = await api.post(`/orders/${user_id}/orderCart`
        );
        return out.data    
    }catch(error){
        console.error("error ording your cart",error)
        throw error
    }
}

export async function past_orders() {
    try{
    const out = await api.post(`/orders/${user_id}/vieworders`,
        {user_id:user_id});
        return out.data    
    }catch(error){
        console.error("error ording your cart",error)
        throw error
    }

}