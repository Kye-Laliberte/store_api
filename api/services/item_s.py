from symtable import Class
from fastapi import HTTPException
from api.database import get_db
import logging
import api.models.sqlAmodels as models
import api.psycopg_models as pmod # pydantic models
from sqlalchemy.orm import Session
from api.models.ordermodels import OrderItem, Order

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
        """create order ."""
        total_price = sum(cart_item.quantity * item.price for cart_item, item in cart_items)
        new_order = Order(total_price=total_price, user_id=user_id)
        self.db.add(new_order)
        self.db.flush()  # flush to get the new order ID
        return new_order
    
    def create_orderItems(self, order_id: int, cart_items: list[tuple[models.CartItem, models.Item]]):
        """create order items for the order and return the order items info (order_id,item_id):int ,quantity:int, price_at_order:float"""
        order_items = []
        for cart_item, item in cart_items:
            order_item = OrderItem(
                order_id=order_id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price_at_order=item.price
            )
            self.db.add(order_item)
            order_items.append(order_item)
        self.db.commit()
        return order_items

    def process_order(self, order_items: list[tuple[OrderItem, models.Item]]):
        """update stock quantity for each item in the cart after order is created"""
        for order_item, item in order_items:
            item.quantity -= order_item.quantity  # update stock quantity
            self.db.add(item)  # add updated item to session
        return True