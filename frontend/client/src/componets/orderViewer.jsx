 import { useState, useEffect } from "react";
import {order_Cart,todaysOrders,orderDetails} from '/src/api/orderClient'
 
export default function ViewOrders({user}){
    const [orders,setorders] = useState([]);
    const [showOrders, setShowOrders] = useState(false);

function OrderCard({order}){
    const [expanded, setExpanded] = useState(false);
    console.log("orders",order);
    return(
    <div>
        <p>total price:{order.total_price}</p>
        <button onClick={()=> setExpanded(!expanded)}>
            {expanded ? "Hide " : "Expand "}
             order</button>
         {expanded && (<OrderDetails order_id = {order.id}/>)}
    </div>
    );
}


function OrderDetails({ order_id }) {
    const [details, setDetails] = useState([]);

    useEffect(() => {
        async function loadDetails() {
            const data = await orderDetails(order_id);
            setDetails(data);
        }
        loadDetails();
    }, [order_id]);

    return (
        <div>
            {details.map(item => (
                <p key={item.id}>{item.name}</p>
                ))}
        </div>
    );
}

async function lodeOrders(){
    const orders = await todaysOrders(user.id); 
    setorders(orders);
    setShowOrders(!showOrders);
    console.log("orders",orders);
}


    
    return(
    <div>
        <button
        disabled={!user?.id}
        onClick ={()=>lodeOrders()} >
            todays orders
        </button>
        {showOrders && (
            orders.map(order => (
                <OrderCard key={order.id} order={order} />
            ))
        )}

    </div>
    );
}