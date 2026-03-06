from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..import sqlAmodels as models


router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcom to the store grab a cart"}

@router.get("{cart_id}/viewcart")
def viewCart():
    print()
    
router.get("/getall")
@router.post("/NewCart")
def newcart():
    print()

@router.post("/{item_id}/addToCart")
def additem():
    print()

@router.delete("/leaveCart")
def leaveCart():
    print()

@router.put("/{item_id}/leaveitem")
def leaveitem():
    print()

router.put("/purchaseItems")
def purchaseItems():
    print()

#purchies items