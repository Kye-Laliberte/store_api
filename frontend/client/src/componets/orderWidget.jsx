import { useState } from "react";
import {order_Cart} from '/src/api/orderClient'
export default function CartWindow({ user, refresh, cart}) {
    const [confirmOrder, setConfirmOrder] = useState(false);

    async function handleOrderCart() {
        try {
            
            await order_Cart(user);

            //reset checkbox after successful order
            setConfirmOrder(false);
            
            // refresh user/cart data here
            console.log(user)
            await refresh(user);
          
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div className='cart-window'>
            <h3>Your Cart</h3>
            <label>
                <input
                    type="checkbox"
                    checked={confirmOrder}
                    onChange={(e) => setConfirmOrder(e.target.checked)}
                />
                Confirm order
            </label>

            <button
                onClick={handleOrderCart}
                className='order-button'
                disabled={
                    user.user_status !== 'active' || !confirmOrder}>
                Order Cart
            </button>
        </div>
    );
}