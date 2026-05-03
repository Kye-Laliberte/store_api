from api.database import get_db
import logging
import api.models.sqlAmodels as models
import api.psycopg_models as pmod # pydantic models
from sqlalchemy.orm import Session

def getcart(user_id: int, db: Session):
    """reusable serves to retreave a users carts info and then returns a pydantic model"""
    try:
        cart=(db.query(models.Cart).filter(models.Cart.user_id==user_id).first())
        if not cart:
            return None
        
        v=pmod.carts(id=cart.id,user_id=user_id,purchase_date=cart.purchase_date)
        return v
    except Exception as e:
        logging(f"error reteving user cart{e}")
        raise e

def getcaritem(cart_id:int,item_id:int, db: Session):
    try:
        cartitem=(db.query(models.CartItem)
                  .filter(models.CartItem.id==cart_id,models.CartItem.item_id==item_id))
    except Exception as e:
        logging(f"error reteving cartitem{e}")
        raise e