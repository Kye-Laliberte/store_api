from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models


router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart



#purchies items