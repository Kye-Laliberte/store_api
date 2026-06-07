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

    def prepare_cart_items(self, cart_id: int):
        """prepares cart items for order processing by returning a list of tuples (cart_item, item) for each item in the user's cart"""
        
        prepared_cart_items = (self.db.query(models.CartItem, models.Item)
                                            .join(models.Item, models.CartItem.item_id == models.Item.id)
                                            .filter(models.CartItem.cart_id == cart_id, models.Item.quantity > 0).all()
        )

        if not prepared_cart_items:
           return None
        return prepared_cart_items
    
    def get_active_items(self, item_id:int):
        """get active item by id, if item is not found or not in stock, return None"""
        out=self.db.query(models.Item).filter(models.Item.id == item_id, models.Item.quantity > 0).first()
        if not out:
            return None
        return out
    
    def create_item(self, name:str, description:str, price:float, quantity:int):
        """create a new item in the database, if an item with the same name already exists, raise an error"""
        if self.db.query(models.Item).filter(models.Item.name==name).first():
            raise error(status_code=400, detail=f"Item with name {name} already exists")
        new_item = models.Item(name=name, description=description, price=price, quantity=quantity)
        self.db.add(new_item)
        self.db.flush()  # flush to get the new item ID before returning
        return new_item
    
    def get_items(self, item_id:int):
        """get item by id, if item is not found return None"""
        out=self.db.query(models.Item).filter(models.Item.id==item_id).first()
        if not out:
            return None
        return out
    
    def stock_check(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """check stock for each item in the cart,"""    
        for cart_item, item in cart_items:
            if cart_item.quantity > item.quantity or cart_item.quantity <= 0:
                logging.error(f"Not enough stock for item {item.name}.Requested: {cart_item.quantity}, Available: {item.quantity}")
                raise error(status_code=400, detail=f"Not enough stock for item {item.name}")
        return True
    
    def create_order(self, user_id: int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """create order."""
        
        # this is a raw sql query to calculate the total price of all items in the cart.  
        total_price =self.db.execute( text("SELECT SUM(cart_items.quantity * items.price) " \
        "FROM cart_items JOIN items ON cart_items.item_id = items.id" \
        " WHERE cart_items.cart_id = :cart_id").bindparams(cart_id=cart_items[0][0].cart_id)).scalar() or 0.00
        if total_price <= 0:
            raise error(status_code=400, detail="Total price must be greater than 0")
        
        new_order = Order(total_price=total_price, user_id=user_id)
        self.db.add(new_order)
        self.db.flush()  # flush to get the new order ID before creating order items
        return new_order
        
    def remove_unavalibale_items(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """"if item has a stock quantity of 0, it removes it from the cart and returns a list of the removed items"""
        removed_items = []
        for cart_item, item in cart_items:
            if item.quantity <= 0:
                self.db.delete(cart_item)
                removed_items.append(item)
        self.db.flush()  # flush to apply the deletions before returning
        return removed_items

    def create_orderItems(self, order_id: int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """create order items for the order and 
        return the order items info (order_id,item_id):int ,quantity:int, price_at_order:float"""
        #self.stock_check(cart_items)

        # this is a raw sql query to create order items for the order and return the order items info (order_id,item_id):int ,quantity:int, price_at_order:float
        # in a list of tuples (order_item, item)
        order_items = self.db.execute(text("""INSERT INTO order_items 
                                           (order_id, item_id, quantity, price_at_order)
                                        SELECT :order_id, 
                                           cart_items.item_id, cart_items.quantity, items.price as price_at_order
                                        FROM cart_items JOIN items ON cart_items.item_id = items.id
                                        WHERE cart_items.cart_id = :cart_id""").bindparams(order_id=order_id, cart_id=cart_items[0][0].cart_id))
            
        return order_items

    def process_order(self, order_id:int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """update stock quantity for each item in the cart after order is created"""
        for cart_item, item in cart_items:
            item.quantity -= cart_item.quantity# update stock quantity for each item in the cart after order is created
            self.db.add(item)  # mark item as modified for update      
            if item.quantity < 0:
                logging.error(f"Stock quantity for item {item.name} cannot be negative after processing order {order_id}")
                raise error(status_code=500, detail=f"Stock quantity for item {item.name} cannot be negative after processing the order")
            self.db.add(item)  # mark item as modified for update   
        return True
    
    def clear_cart(self, cart_id: int):
        """clear cart items after order is created"""
        try:    
            self.db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).delete()
            
            return True
        except Exception as e:
            logging.error(f"Error clearing cart {cart_id}: {e}")
            self.db.rollback()
            raise error(status_code=500, detail="An error occurred while clearing the cart")