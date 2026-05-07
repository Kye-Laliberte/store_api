from symtable import Class
from fastapi import HTTPException
from api.database import get_db
import logging
import api.models.sqlAmodels as models
import api.psycopg_models as pmod # pydantic models
from sqlalchemy.orm import Session

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
    
    def get_items(self, item_id:int):
        out=self.db.query(models.Item).filter(models.Item.id==item_id).first()
        if not out:
            return None
        return out