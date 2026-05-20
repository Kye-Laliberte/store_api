import api from '/src/api/axios';
import '/src/App.css';
import { addToCart,viewCart } from '/src/api/CartClient';

export function ItemList({
    items,quantities,user,
    onQuantityChange,onAddToCart}) {
    if (!Array.isArray(items)||items.length === 0) {
        return <p>no items</p>;
    }
    return (
        <div className='item-Display'>

            {items?.map((item) => (
                <ProductCard
                    key={item.id}
                    item={item}
                    cart_id={user.cart_id}
                    quantity={quantities[item.id]}
                    onQuantityChange={onQuantityChange}
                    onAddToCart={onAddToCart}
                />))}
        </div>
    );

  }

  function ProductCard({item,quantity,
    onQuantityChange,onAddToCart,cart_id}) {
    return (
        <div className="item-block">
            <h3>{item.name}</h3>
            <input
                type="number"
                inputMode="numeric"
                min="1"
                placeholder="quantity"
                value={quantity ?? ""}
                onChange={(e) =>
                    onQuantityChange(
                        item.id,
                        e.target.value
                    )}/>
            <button
                className="basic-button"
                onClick={() => onAddToCart(item)}
                disabled={!Number(quantity) || Number(quantity) <= 0 || cart_id===null}>
                Add To Cart</button>
              <p>{item.description}</p>
            <p>price {item.price}$</p>
            <p>{item.quantity} left</p></div>
);
}    
  
          
