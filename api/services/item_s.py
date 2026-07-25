from fastapi import HTTPException
import logging
import models.sqlAmodels as models
from sqlalchemy.orm import Session
from models.ordermodels import Order
from sqlalchemy import text
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class error(HTTPException):
    """Base class for other exceptions"""
    pass
    def __init__(self, status_code: int, detail: str):
        """Initialize the error with a status code and detail message."""
        super().__init__(status_code=status_code, detail=detail)



class OrderProcessing:
    """Class to handle order processing logic, including stock checks, order creation, and cart management."""
    def __init__(self, db: Session,user_id:int,cart_id:int):
        self.db = db
        self.user_id = user_id
        self.cart_id = cart_id
    def prepare_cart_items(self):
        """prepares cart items for order processing by returning a list of tuples (cart_item, item) for each item in the user's cart"""
        
        prepared_cart_items = (self.db.query(models.CartItem, models.Item)
                                            .join(models.Item, models.CartItem.item_id == models.Item.id)
                                            .filter(models.CartItem.cart_id == self.cart_id).all()
        )
        
        return prepared_cart_items
    def pre_order_checks(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """perform pre-order checks such as stock availability and  if cart_items exceed the stock
        for right now it returns the input and HTTP"""
        if not cart_items:
            return []    
            
        invalid_items = (self.db.query(models.CartItem, models.Item)
        .join(models.Item,models.CartItem.item_id == models.Item.id
        ).filter(models.CartItem.cart_id == self.cart_id,
        models.CartItem.quantity > models.Item.quantity).all())
        
        if invalid_items:
            raise HTTPException(status_code=400,detail="Some cart items exceed available stock.")       
        return cart_items
    
    def CartItems(self,cart_items: list[tuple[models.CartItem, models.Item]] ):
        """this deletes cart_items where the cart quantity is more that the item quantity"""
        
        #removs the cart_items.quantity > item.quantity- cart_items.quantity
        out_of_stock=self.db.execute(text("""DELETE FROM cart_items USING items"""))

    def create_order(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """Create the order and order items in the database without committing.
        This function prepares the Order ORM object, flushes to populate its id,
        creates the order_items rows, and returns the Order object. The caller
        is responsible for transaction management (commit/rollback) or should
        call process_order which wraps the whole flow in a transaction.
        """
        total_price = self.db.execute(text("""SELECT SUM((cart_items.quantity) * items.price) 
        FROM cart_items JOIN items ON cart_items.item_id = items.id 
        WHERE cart_items.cart_id = :cart_id"""), {"cart_id": cart_items[0][0].cart_id}).scalar() or 0
        new_order = Order(total_price=total_price, user_id=self.user_id)
        self.db.add(new_order)
        # flush so new_order.id is available for returning and for any dependent SQL
        self.db.flush()
        # create order items rows (INSERT ... RETURNING)
        order_items = self.create_orderItems(order_id=new_order.id, cart_items=cart_items)
        return new_order
    
    def create_orderItems(self, order_id:int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """create order items for a given order"""
        
        cart_items_data = self.db.execute(text("""INSERT INTO order_items (order_id, item_id, quantity, price_at_order) 
                                               SELECT :order_id, cart_items.item_id, cart_items.quantity, items.price 
                                               FROM cart_items JOIN items ON cart_items.item_id = items.id
                                               WHERE cart_items.cart_id =:cart_id RETURNING order_id, item_id, quantity, price_at_order"""), 
                                               {"order_id": order_id, "cart_id": self.cart_id}).fetchall()
        
        if not cart_items_data:
            return []
        return cart_items_data
    
    def update_stock(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """Update stock quantity for each item in the cart after order is created.
        Raises an error on failure so the caller can rollback the transaction.
        """
        try:
            result = self.db.execute(text("""
            UPDATE items
            SET quantity = items.quantity - cart_items.quantity
            FROM cart_items
            WHERE items.id = cart_items.item_id
            AND cart_items.cart_id = :cart_id"""),
            {"cart_id": self.cart_id})
            return True
        except Exception as e:
            # Propagate the failure so a surrounding transaction will be rolled back
            logging.error(f"Error updating stock for cart {self.cart_id}: {e}")
            raise error(status_code=500, detail=f"An error occurred while updating stock quantities: {e}") from e
    
    def clear_cart(self):
        """Clear cart items after order is created. Does not commit; expects caller to manage the transaction."""
        try:
            self.db.query(models.CartItem).filter(models.CartItem.cart_id == self.cart_id).delete()
            return True
        except Exception as e:
            logging.error(f"Error clearing cart {self.cart_id}: {e}")
            raise error(status_code=500, detail="An error occurred while clearing the cart")

    def process_order(self, cart_items: list[tuple[models.CartItem, models.Item]]):
        """Process an order as a single atomic transaction: run pre-order checks,
        create the order and order_items rows, update stock, and clear the cart.
        Uses a transactional context so either everything commits or everything
        is rolled back.
        """
        # perform pre-order checks first
        prepared_cart_items = self.pre_order_checks(cart_items)
        if not prepared_cart_items:
            raise error(status_code=400, detail="No items in cart to order")

        # Use the session transaction to make the whole operation atomic
        try:
            with self.db.begin():
                new_order = self.create_order(prepared_cart_items)
                if not new_order:
                    raise error(status_code=500, detail="An error occurred while creating the order")
                # update stock (will raise on failure)
                self.update_stock(prepared_cart_items)
                # clear cart rows
                self.clear_cart()
            # transaction committed successfully
            return new_order
        except Exception as e:
            # re-raise well-formed HTTPException-like errors or wrap unexpected ones
            if isinstance(e, HTTPException) or isinstance(e, error):
                raise
            logging.error(f"Order processing failed for user {self.user_id}, cart {self.cart_id}: {e}")
            raise error(status_code=500, detail=f"An error occurred while processing the order: {e}") from e
    
    
def get_active_items(item_id:int,db:Session):
    """get active item by id, if item is not found or not in stock, return None"""
    out=db.query(models.Item).filter(models.Item.id == item_id, models.Item.quantity > 0).first()
    if not out:
        return None
    return out
    
def createItem(name:str, description:str, price:float, quantity:int,db:Session):
    """create a new item in the database, if an item with the same name already exists, raise an error"""
    if db.query(models.Item).filter(models.Item.name == name).first():
        raise error(status_code=400, detail=f"Item with name {name} already exists")
    
    new_item = models.Item(name=name, description=description, price=price, quantity=quantity)

    db.add(new_item)
    db.commit()
    return new_item
    
def get_items(item_id:int,db:Session):
    """get item by id, if item is not found return None"""
    out=db.query(models.Item).filter(models.Item.id==item_id).first()
    if not out:
        return None
    return out
    
    
   