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
    
def get_user(user_id:int,db:Session):
    try:
        user=(db.query(models.User).filter(models.User.id==user_id).first())
        if not user:
            return None
        
        if user.status != pmod.UserStatus.active:
            return False
            
        out=pmod.users(id=user_id,email=user.email,created_at=user.created_at)
        return out
    except Exception as e:
        logging(f"error reteving user {e}")
        raise e

def get_user_Email(email:int,db:Session):
    try:
        user=(db.query(models.User).filter(models.User.email==email).first())
        if not user:
            return None
        
        if user.status != pmod.UserStatus.active:
            return False
            
        out=pmod.users(id=user.id,email=email,created_at=user.created_at)
        return out
    except Exception as e:
        logging(f"error reteving user {e}")
        raise e