import logging

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
    """ shows all past orders for a user"""
    orders= db.query(Omodels.Order).filter(Omodels.Order.user_id==user_id).all()
    
    if not orders:
        raise HTTPException(status_code=404,detail=f"no orders found for {user_id}")
    
    return orders

@router.get("/getallorders", response_model=List[pmodels.orders])
def getAllOrders(db: Session=Depends(get_db)):
    """returns all orders in the database, for testing purposes only"""
    orders = db.query(Omodels.Order).all()
    return orders

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

@router.post("/{user_id}/createorder",response_model=pmodels.ordersout)
def createOrder(user_id:int, db: Session=Depends(get_db)):
    """orders all Items in a user's cart, creates an order and orderitems, updates stock quantity, and clears the cart
    returns the order info (order_id,user_id):int ,total_price:float  
     order_date:DateTime,  number_of_items:Int."""
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found for this user")
   
    cartItems = (db.query(models.CartItem, models.Item)
                 .join(models.Item, models.CartItem.item_id == models.Item.id)
                 .filter(models.CartItem.cart_id==cart.id)).all()
    if  not cartItems:
        raise HTTPException(status_code=400,detail="cart is empty")
    
    #stop if any item in the cart is more than available in stock
    for cart_item, item in cartItems:
        if item.quantity < cart_item.quantity:
            logging.error(f"Insufficient stock for item {item.id} while creating order for user {user_id}")
            raise HTTPException(status_code=400, detail=f"Insufficient stock for item {item.name}")

    try:
        # create order
        total_price = sum(cart_item.quantity * item.price for cart_item, item in cartItems)
        new_order = Omodels.Order(total_price=total_price, user_id=user_id)
        db.add(new_order)
        db.flush()  # flush to get the new order ID
        
    # create order items
        itemNames = []
        order_items =[]
        for cart_item, item in cartItems:
            order_item = Omodels.OrderItem(
                order_id=new_order.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price_at_order=item.price
                )
            itemNames.append( item.name)
            db.add(order_item)
            item.quantity -= cart_item.quantity  # update stock quantity
            val={"order_id":new_order.id,"item_id":item.id,"name": item.name,"totalprice": cart_item.quantity*item.price,"quantity":cart_item.quantity}
            order_items.append(val)
            
            db.delete(cart_item)  # clear cart item
        v=({"id": new_order.id, "total_price": new_order.total_price,"user_id":user_id,
            "order_date": new_order.order_date, "number_of_items": len(cartItems)})
        
        order = pmodels.ordersout(**v)           
        db.commit()
        db.refresh(new_order)
        return order
    
    except Exception as e:
        logging.error(f"Error creating order items for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating order items") 
    
 

    # Return order details
   
    

    
    
