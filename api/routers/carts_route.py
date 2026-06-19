import logging
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
from typing import List, Optional
from api.psycopg_models import CartItemsOut,carts,create_cartItem,createCart,UserStatus,userOut
from datetime import datetime
from api.services.cart_services import filter_user, getcart, get_user, newcart
router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcome to the store grab a cart"}


@router.get("/{user_id}/viewcart",response_model=List[CartItemsOut])
def viewCart(user_id:int,db: Session=Depends(get_db)):
    """retreves all items in the cart that relar to the user_id and returns a list of models with the item name, description, price and quantity"""
    
    cart=getcart(user_id, db)

    if not cart:
        raise HTTPException(status_code=404,detail=f"no cart found ")
    
    if cart.status != UserStatus.active:
        raise HTTPException(status_code=400, detail="User is not active. Cannot view cart.")
    
    cart_items = (db.query(models.CartItem.item_id,
                           models.CartItem.quantity,
                           models.Item.description,
                           models.Item.name,
                           models.Item.price)
                           .join(models.Item, models.CartItem.item_id == models.Item.id)
                                 .filter(models.CartItem.cart_id == cart.id).all())
    if not cart_items:
        logging.info(f"Cart {cart.id} for user {user_id} is empty.")
        raise HTTPException(status_code=204, detail=f"User {user_id} has an empty cart.")
    
    

    return[
        CartItemsOut(
            item_id=items.item_id,
            quantity=items.quantity,
            description=items.description,
            price=items.price,
            name=items.name,
            totalprice=items.quantity*items.price
            )
        for items in cart_items
        ]

@router.get("/getallcarts",response_model=List[carts])
def GetCarts(db: Session = Depends(get_db)):
    """retreves all of the carts info and returns a list of cart models"""
    out=db.query(models.Cart).all()
    return out

@router.post("/{user_id}/additem/{cart_id}",response_model=CartItemsOut)
def additem(user_id:int,cart_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    """adds a item to the cart if it is alredy there it updates the quantity to the new quantity, returns a item model with item name, description, price and quantity"""
    
    quantity=item.quantity
    item_id=item.item_id
    
    if quantity<=0:
        raise HTTPException( status_code=400,detail="cant add less than 1 items to a cart")
    
    
    cart=getcart(user_id=user_id,db=db)

    if not cart:
            raise HTTPException(status_code=404,detail=" cart not found.")
    
    if cart.status != UserStatus.active:
        raise HTTPException(status_code=400, detail="User is not active. Cannot add items to cart.")

    Item=(db.query(models.Item).filter(models.Item.id==item_id).first())
    if not Item:
            raise HTTPException(status_code=404,detail=f"item with id {item_id} not found")
    
    if Item.quantity < quantity:
            logging.error(f"Insufficient stock for item {item_id} while adding to cart for user {user_id}")
            raise HTTPException(status_code=400, detail=f"Insufficient stock for item {item_id}")
    
    try:
        existing = (
            db.query(models.CartItem)
            .filter(models.CartItem.cart_id == cart.id, models.CartItem.item_id == item_id).first())
        
        if existing:
            existing.quantity = quantity
            out = existing
        else:
            out =models.CartItem(cart_id=cart.id, item_id=item_id, quantity=quantity)
             
           
        db.add(out)
        db.commit()
        db.refresh(out)
        return CartItemsOut(item_id=out.item_id, quantity=out.quantity,
                     name=Item.name,description=Item.description,price=Item.price,totalprice=Item.quantity*Item.price)
         
    except Exception as e:
        logging.error(f"Error checking for existing cart info for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while checking for existing cart item")
    except KeyError as e:
        logging.error(f"Key error while processing cart item for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while processing cart item {e}")

@router.post("/{user_id}/newcart", response_model=carts)
def newCart(user_id:int, db: Session = Depends(get_db)):
    """creates a new cart for the user if one does not already exist"""
    
    user=filter_user(user_id=user_id,status=models.UserStatus.active,db=db)
    if not user:
        raise HTTPException(status_code=404, detail="user not found or is inactive")
    
    exists=getcart(user_id,db) 
    if exists:
         #return {"mesage": True  }
         raise HTTPException(status_code=200,detail="cart alredy active")
         #return exists
    cart_date = datetime.now()
    try:
        
        new_cart = models.Cart(user_id=user_id, cart_date=cart_date)
        out_cart=newcart(cart=new_cart,db=db)

        if not out_cart:
            raise HTTPException(status_code=500, detail="Failed to create new cart")
        
        return out_cart
    
    except Exception as e:
        logging.error(f"Error creating new cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating a new cart")
    
@router.delete("/{cart_id}/removeitem/{item_id}",response_model=create_cartItem)
def leaveitem(item_id:int,cart_id:int,db:Session=Depends(get_db)):
    """delete a cartItem that  relats to carts.id== cartitems.cart_id belongs to carts.user_id
    returns item_id quantity of cartitem"""
    
    cartitem=(db.query(models.CartItem)
              .filter(cart_id==models.CartItem.cart_id,item_id==models.CartItem.item_id).first())
    if not cartitem:
        raise HTTPException(status_code=404, detail="Item not in cart.")
    
    try:    
        db.delete(cartitem)
        db.commit()
        item=create_cartItem(item_id=cartitem.item_id,quantity=cartitem.quantity)
        return item
    except Exception as e:
        logging.error(f"Error occurred while querying cart item for cart {cart_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while removing item from cart")
    
    
@router.delete("/{user_id}/dropCart/{cart_id}",response_model=carts)
def dropcart(user_id:int,cart_id:int,db:Session=Depends(get_db)):
    """removes all items from the cartItems tabel pertaning to the user_id and removes the cart from the Cart tebel"""
   
    cart=getcart(user_id,db)
    if  not cart:
        raise HTTPException(status_code=404,detail="no cart active or found")
    
#    if cart.status != UserStatus.active:
#        raise HTTPException(status_code=400, detail="User is not active. Cannot drop cart.")
    
    try:    
        db.query(models.CartItem).filter(models.CartItem.cart_id==cart.id).delete()
        db.query(models.Cart).filter(models.Cart.id==cart.id,models.Cart.user_id==cart.user_id).delete()
        db.commit()
        return carts(id=cart.id,user_id=cart.user_id,cart_date=cart.cart_date)
    except Exception as e:
        logging.error(f"Error occurred while dropping the cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while dropping the cart")
        

        
    
               
    

    