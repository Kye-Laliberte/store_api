from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..alembic import sqlAmodels as models


router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart



#purchies items