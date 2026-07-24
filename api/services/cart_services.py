from symtable import Class
from fastapi import HTTPException
from database import get_db
import logging
import models.sqlAmodels as models
import psycopg_models as pmod # pydantic models
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def newcart(user_id,db:Session):
    """deletes a users existing cart if it exists then
      creates a new cart for a user and returns the cart sql model"""
    cart_date = datetime.now()
    new_cart = models.Cart(user_id=user_id, cart_date=cart_date)
    user=filter_user(user_id=new_cart.user_id,status=pmod.UserStatus.active,db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        existing_cart = db.query(models.Cart).filter(models.Cart.user_id == new_cart.user_id).delete()
        if existing_cart:
            logging.info(f"Existing cart for user {new_cart.user_id} deleted.")
    except Exception as e:
        logging.error(f"the cart still has cartitems {new_cart.user_id}: {e}")
    try:
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        logging.info(f"New cart created for user {new_cart.user_id} with cart ID {new_cart.id}.")
        return new_cart
    except Exception as e:
        logging.error(f"Error creating new cart for user {new_cart.user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating a new cart")

def FindCart(user_id:int,cart_id:int,db:Session):
    """this gets a cart User info when a user_id and Cart_id are in a relashinship """
    try:
        cart=(db.query(models.Cart.id,models.Cart.cart_date,models.Cart.user_id,models.User.status)
          .filter(models.Cart.user_id == user_id, models.Cart.id == cart_id)
          .join(models.User, models.User.id == models.Cart.user_id)).first()
    
        if not cart:
            return None
        
        return cart
    
    except Exception as e:
        logging.error(f"error retrieving user cart: {e}")
        raise e

def getcart(user_id: int, db: Session):
    """reusable serves to retreave a users carts info and then returns a pydantic model"""
    try:
        # this query will join with 
        cart=(db.query(models.Cart.id,models.Cart.cart_date,models.Cart.user_id,models.User.status)
              .filter(models.Cart.user_id == user_id)
              .join(models.User, models.User.id == models.Cart.user_id)).first()

        if not cart:
            return None
        
        return cart
    except Exception as e:
        logging.error(f"error retrieving user cart: {e}")
        raise e

def getcaritem(cart_id:int,item_id:int, db: Session):
    try:
        cartitem = (db.query(models.CartItem)
                  .filter(models.CartItem.cart_id == cart_id,  models.CartItem.item_id == item_id)).first()
        if not cartitem:
            return False
        
        return cartitem    
    except Exception as e:
        logging(f"error reteving cartitem{e}")
        raise e
    
def get_user(user_id:int,db:Session):
    """this gets a user model by there user_id even if there status is not active and returns the sql model"""
    try:
        user=(db.query(models.User).filter(models.User.id == user_id).first())
        if not user:
            return None        
        return user
    except Exception as e:
        logging(f"error reteving user {e}")
        raise e
def filter_user(user_id:int,db:Session,status:pmod.UserStatus=pmod.UserStatus.active):
    """this gets a user model by there user_id but filters by the givin status and returns the sql model status defaults to active."""
    try:
        user=(db.query(models.User).filter(models.User.id == user_id).first())
        if not user:
            return None        
        if user.status != status:
            return False
        return user
    except Exception as e:
        logging(f"error reteving user {e}")
        raise 

def get_user_Email(email:str,db:Session):
    try:
        email = email.strip()
        user=(db.query(models.User).filter(models.User.email == email).first())
        if not user:
            return None
        
        if user.status != pmod.UserStatus.active:
            return False
            
        return  user
    except Exception as e:
        logging(f"error reteving user {e}")
        raise e
    
def delete_cart(cart_id:int,db:Session):
    """deletes a cart and all cartitems that are related to the cart_id"""
    try:
        if not db.query(models.Cart).filter(models.Cart.id == cart_id).first():
            raise HTTPException(status_code=404, detail=f"Cart with id {cart_id} not found.")    
        
        db.query(models.CartItem).filter(models.CartItem.cart_id==cart_id).delete()
        db.query(models.Cart).filter(models.Cart.id==cart_id).delete()
        db.commit()
        return True
    except Exception as e:
        logging.error(f"Error occurred while dropping the cart for cart {cart_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while dropping the cart")

def new_user(email:str,password:str,db:Session):
    exists=get_user_Email(email=email,db=db)

    if(exists is not None):
        raise HTTPException(status_code=400, detail="email already in use")
    
    if len(password.encode('utf-8')) < 8:
        raise HTTPException(status_code=400, detail="Password too short.")
    
    hashed_password = pwd_context.hash(password)

    if(len(hashed_password)>72):
        raise HTTPException(status_code=400, detail=f"{len(hashed_password)}Password too long (max 72 bytes).")
    
    user = models.User(email=email, password_hash=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def additemCart(item_id:int,user:pmod.cartpacage,quantity:int,db:Session):
    """adds an item to a users cart if the user is active and the item is in stock"""
    
    user_id=user.user_id
    
    cart=FindCart(user_id=user_id,cart_id = user.cart_id,db=db)

    if not cart:
            raise HTTPException(status_code=404,detail=" cart not found.")
    
    if cart.status != pmod.UserStatus.active:
        raise HTTPException(status_code=400, detail="User is not active. Cannot add items to cart.")

    Item=(db.query(models.Item).filter(models.Item.id==item_id, models.Item.quantity > quantity).first())
    if not Item:
            raise HTTPException(status_code=404,detail=f"item with id {item_id} not found or out of stock")
    
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
        return pmod.CartItemsOut(item_id=out.item_id, quantity=out.quantity,
                     name=Item.name,description=Item.description,price=Item.price,totalprice=Item.quantity*Item.price)
         
    except Exception as e:
        logging.error(f"Error checking for existing cart info for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while checking for existing cart item")
    except KeyError as e:
        logging.error(f"Key error while processing cart item for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while processing cart item {e}")



