import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from sqlalchemy import text
from api.database import get_db
import api.models.sqlAmodels as models
import  api.models.ordermodels as Omodels
from typing import List, Optional
from api.psycopg_models import users,userOut, UserStatus
from datetime import datetime
import api.models.psyc_order as pmodels
from api.services.cart_services import getcart
from api.services.item_s import Serviceitems, error
router = APIRouter(prefix="/orders", tags=["orders"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"order route is under construction"}

@router.get("/{user_id}/vieworders", response_model=List[pmodels.orders])
def viewOrders(user_id:int,db: Session=Depends(get_db)):
    """ shows all past orders for a user"""
    
    
    orders= db.query(Omodels.Order).filter(Omodels.Order.user_id==user_id).all()

    if not orders:
        raise HTTPException(status_code=204,detail= "no orders")
    try:    
      
        return orders
    
    except Exception as e:
        logging(f"faled to conect {e}")
        raise HTTPException(status_code=400,detail=f"error {e}")
    
    
@router.get("/getallorders", response_model=List[pmodels.orders])
def getAllOrders(db: Session=Depends(get_db)):
    """returns all orders in the database, for testing purposes only"""
    orders = db.query(Omodels.Order).all()
    return orders
@router.get("/{order_id}/details", response_model=List[pmodels.orderInfo])
def get_order_details(order_id:int, db: Session=Depends(get_db)):
    """returns the details of an order including item information and price at order time"""
    try:
        order_details = (db.query(Omodels.Order.id,
                             Omodels.Order.order_date,
                             Omodels.OrderItem.item_id,
                             Omodels.OrderItem.quantity,
                             Omodels.OrderItem.price_at_order,
                             models.Item.name,
                             models.Item.description,
                             )
                             .join(Omodels.OrderItem, Omodels.Order.id == Omodels.OrderItem.order_id)
                             .join(models.Item, Omodels.OrderItem.item_id == models.Item.id)
                             .filter(Omodels.Order.id == order_id).all())
    except Exception as e:
        logging.error(f"Error retrieving order details for order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving order details")
    if not order_details:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_details


@router.get("/{user_id}/vieworderdetails", response_model=List[pmodels.orderInfo])
def viewOrderDetails(user_id:int,db: Session=Depends(get_db)):
    """ shows all detals of past orders incluting item infermation and price at order time
    returns a list of OrderItems with item detalies"""
    try:
        orderDetails = (db.query(Omodels.Order.id,
                             Omodels.Order.order_date,
                             Omodels.OrderItem.item_id,
                             Omodels.OrderItem.quantity,
                             Omodels.OrderItem.price_at_order,
                             models.Item.name,
                             models.Item.description,
                             )
                             .join(Omodels.OrderItem, Omodels.Order.id == Omodels.OrderItem.order_id)
                             .join(models.Item, Omodels.OrderItem.item_id == models.Item.id)
                             .filter(Omodels.Order.user_id == user_id).all())
    except Exception as e:
        logging.error(f"Error retrieving order details for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving order details")
    except KeyError as e:
        logging.error(f"Key error while processing order details for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing order details")
    
    if not orderDetails:
        raise HTTPException(status_code=404, detail="No orders found for this user")
        
    return orderDetails
  
    
@router.post("/{user_id}/orderCart",response_model=pmodels.ordersout)
def orderCart(user_id:int, db: Session=Depends(get_db)):
    """orders all Items in a user's cart, creates an order and orderitems, updates stock quantity, and clears the cart
    returns the order info (order_id,user_id):int ,total_price:float  
     order_date:DateTime,  number_of_items:Int."""
    service=Serviceitems(db)
    cart=getcart(user_id=user_id,db=db)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found for this user")
    if cart.status != UserStatus.active:
        raise HTTPException(status_code=400, detail="user is not active")
    
    cartItems=service.prepare_cart_items(cart_id=cart.id)
    if not cartItems:
        raise HTTPException(status_code=204, detail="No items in cart to order")
    try:   
        service.stock_check(cartItems)
        new_order=service.create_order(user_id, cart_items=cartItems)
        service.create_orderItems(order_id=new_order.id, cart_items=cartItems)
        service.process_order(order_id=new_order.id, cart_items=cartItems)
        service.clear_cart(cart_id=cart.id)

        db.commit()# commit the order.
        db.refresh(new_order)  # refresh to get the order date and total price after commit
        # clear cart items after order is created
    except Exception as e:
        logging.error(f"Error creating order for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the order")
    
    #service.process_order(new_order.order_items.all())
    # update stock quantity for each item in the cart after order is created
    number_of_items = db.execute(text("""SELECT SUM(quantity) FROM order_items WHERE order_id = :order_id""").bindparams(order_id=new_order.id)).scalar() or 0
    
    return pmodels.ordersout(id=new_order.id, total_price=new_order.total_price, user_id=user_id, order_date=new_order.order_date, number_of_items=number_of_items)

    
    
