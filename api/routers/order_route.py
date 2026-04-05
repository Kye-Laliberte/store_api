from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import sqlAmodels as models
import  models.ordermodels as Omodels
from typing import List, Optional
from psycopg_models import users,userOut
from datetime import datetime
router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"order route is under construction"}