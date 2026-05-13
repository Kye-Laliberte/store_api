from symtable import Class
from fastapi import HTTPException
from api.database import get_db
import logging
import api.models.sqlAmodels as models
import api.psycopg_models as pmod # pydantic models
from sqlalchemy.orm import Session
from api.models.ordermodels import OrderItem, Order
from sqlalchemy import text
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class error(HTTPException):
    """Base class for other exceptions"""
    pass
    def __init__(self, status_code: int, detail: str):
        """Initialize the error with a status code and detail message."""
        super().__init__(status_code=status_code, detail=detail)

class Serviceitems:


    def __init__(self, db: Session):
        self.db = db


    def get_active_items(self, item_id:int):
        out=self.db.query(models.Item).filter(models.Item.id==item_id and models.Item.quantity>0).first()
        if not out:
            return None
        return out
    
    def create_item(self, name:str, description:str, price:float, quantity:int):
        if self.db.query(models.Item).filter(models.Item.name==name).first():
            raise error(status_code=400, detail=f"Item with name {name} already exists")
        new_item = models.Item(name=name, description=description, price=price, quantity=quantity)
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item
    
    def get_items(self, item_id:int):
        out=self.db.query(models.Item).filter(models.Item.id==item_id).first()
        if not out:
            return None
        return out
    
    def stock_check(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """check stock for each item in the cart,"""    
        for cart_item, item in cart_items:
            if cart_item.quantity > item.quantity:
                logging.error(f"Not enough stock for item {item.name}.Requested: {cart_item.quantity}, Available: {item.quantity}")
                raise error(status_code=400, detail=f"Not enough stock for item {item.name}")
        return True
    
    def create_order(self, user_id: int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """create order."""
        # this is a raw sql query to calculate the total price of all items  a cart.  
        total_price =self.db.execute( text("SELECT SUM(cart_items.quantity * items.price) " \
        "FROM cart_items JOIN items ON cart_items.item_id = items.id" \
        " WHERE cart_items.cart_id = :cart_id").bindparams(cart_id=cart_items[0][0].cart_id)).scalar() or 0.00
        if total_price <= 0:
            raise error(status_code=400, detail="Total price must be greater than 0")
        
        new_order = Order(total_price=total_price, user_id=user_id)
        self.db.add(new_order)
        self.db.flush()  # flush to get the new order ID
        
        return new_order
        
    
    def create_orderItems(self, order_id: int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """create order items for the order and return the order items info (order_id,item_id):int ,quantity:int, price_at_order:float"""
        #self.stock_check(cart_items)


        # this is a raw sql alchemy query to create the sql model OrederItems for each item in the cart and return the order items info (order_id,item_id):int ,quantity:int, price_at_order:float 
        orderitems= self.db.execute(text("""ADD OrderItem (order_id, item_id, quantity, price_at_order)
                                         SELECT :order_id, cart_items.item_id, cart_items.quantity, items.price as price_at_order
                                         FROM cart_items JOIN items ON cart_items.item_id = items.id
                                         WHERE cart_items.cart_id = :cart_id""").bindparams(order_id=order_id, cart_id=cart_items[0][0].cart_id))
        self.db.add(orderitems)
        """
        order_items = []
        for cart_item, item in cart_items:
            order_item = OrderItem(
                order_id=order_id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price_at_order=item.price
            )
            self.db.add(order_item)
            order_items.append(order_item)"""
        self.db.commit()
        return orderitems

    def process_order(self, order_items: list[tuple[OrderItem, models.Item]]):
        """update stock quantity for each item in the cart after order is created"""
        
        #update stock quantity for each item in the cart after order is created using raw sql query 
        self.db.execute(text("""UPDATE items SET quantity = quantity - :quantity
                                FROM order_items
                                WHERE items.id = order_items.item_id AND order_items.order_id = :order_id""")
                                .bindparams(quantity=order_items[0][0].quantity, order_id=order_items[0][0].order_id))
            
        self.db.commit()
        return True
    
    def clear_cart(self, cart_id: int):
        """clear cart items after order is created"""
        try:    
            self.db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).delete()
            self.db.commit()
            return True
        except Exception as e:
            logging.error(f"Error clearing cart {cart_id}: {e}")
            self.db.rollback()
            raise error(status_code=500, detail="An error occurred while clearing the cart")