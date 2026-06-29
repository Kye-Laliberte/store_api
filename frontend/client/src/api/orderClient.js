import api from "/src/api/axios"


export async function order_Cart(user) {
    try{
       
    const out = await api.post(`/orders/${user.id}/orderCart`);
        return out.data;
        
    }catch(error){
        console.error("error ording your cart",error);
        throw error;
    }
}

export async function all_orders(user_id) {
    try{
    const out = await api.get(`/orders/${user_id}/vieworders`);
       
        return out.data;    
    }catch(error){
        console.error("error ording your cart",error);
        throw error;}
}

export async function todaysOrders(user_id){
    try{
        const out = await api.get(`/orders/${user_id}/TodayOrders`);
        return out.data;
    
    }catch(error){
        console.error("error loding orders")}
}

export async function orderDetails(order_id) {
    
    try{
        const out = await api.get(`/orders/${order_id}/details`);

    return out.data;

    }catch(error){
        console.error("faild to get order detals",error);
        throw error;
    } 
}