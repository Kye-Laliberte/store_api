from ..database import get_db
import logging
import api.models.sqlAmodels as models
from ..import psycopg_models as pmod # pydantic models
from sqlalchemy.orm import Session

def getcart(user_id: int, db: Session):
    try:
        cart=(db.query(models.Cart).filter(models.Cart.user_id==user_id).first())
        if not cart:
            return None
        cartmod={"id":cart.id,"user_id":user_id,"purchase_date":cart.purchase_date} 
        v=pmod.carts(id=cart.id,user_id=user_id,purchase_date=cart.purchase_date)
        return v
    except Exception as e:
        logging(f"error reteving user cart{e}")
        raise 

