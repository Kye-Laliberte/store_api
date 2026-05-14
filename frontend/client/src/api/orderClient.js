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

export async function past_orders(user_id) {
    try{
    const out = await api.get(`/orders/${user_id}/vieworders`
       );

    if (out.status==204){
        return []
    }    
        return out.data    
    }catch(error){
        console.error("error ording your cart",error)
        throw error
    }

}