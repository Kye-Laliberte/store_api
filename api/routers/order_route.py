from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
import  api.models.ordermodels as Omodels
from typing import List, Optional
from api.psycopg_models import users,userOut
from datetime import datetime
import api.models.psyc_order as pmodels
router = APIRouter(prefix="/orders", tags=["orders"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"order route is under construction"}

@router.get("/{user_id}/vieworders", response_model=List[pmodels.orders])
def viewOrders(user_id:int,db: Session=Depends(get_db)):
    orders= db.query(Omodels.Order).filter(Omodels.Order.user_id==user_id).all()
    
    if not orders:
        raise HTTPException(status_code=404,detail=f"no orders found for {user_id}")
    
    return orders

@router.get("/getallorders", response_model=List[pmodels.orders])
def getAllOrders(db: Session=Depends(get_db)):
    orders = db.query(Omodels.Order).all()
    return orders

@router.get("/{user_id}/vieworderdetails", response_model=List[pmodels.orderInfo])
def viewOrderDetails(user_id:int,db: Session=Depends(get_db)):
    """ shows all detals of past orders incluting item infermation and price at order time"""
    orderDetails = (db.query(Omodels.Order.id,
                             Omodels.Order.order_date,
                             Omodels.OrderItem.item_id,
                             Omodels.OrderItem.quantity,
                             Omodels.OrderItem.price_at_order,
                             models.Item.name,
                             models.Item.description
                             )
                             .join(Omodels.OrderItem, Omodels.Order.id == Omodels.OrderItem.order_id)
                             .join(models.Item, Omodels.OrderItem.item_id == models.Item.id)
                             .filter(Omodels.Order.user_id == user_id).all())
    
    if not orderDetails:
        raise HTTPException(status_code=404, detail="No orders found for this user")
        
    return orderDetails