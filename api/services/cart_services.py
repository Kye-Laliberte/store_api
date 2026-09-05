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



        

def newcart(db: Session, user_id: int):
    """deletes a users existing cart if it exists then
      creates a new cart for a user and returns the cart sql model"""
    cart_date = datetime.now()
    new_cart = models.Cart(user_id=user_id, cart_date=cart_date)
    user=UserService(db,user_id).filter_user(user_id=new_cart.user_id,status=pmod.UserStatus.active,db=db)
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
        logging.error(f"error retrieving cartitem: {e}")
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
    
    user = models.User(email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def additemCart(item_id:int,user:pmod.cartpacage,quantity:int,db:Session):
    """adds an item to a users cart if the user is active and the item is in stock"""
    
    user_id=user.user_id
    
    cart=FindCart(user_id=user_id,cart_id = user.cart_id,db=db)

    logging.info(f"FindCart result for user {user_id}, cart {user.cart_id}: {cart}")

    if not cart:
        raise HTTPException(status_code=404,detail=" cart not found.")
    
    if cart.status != pmod.UserStatus.active:
        raise HTTPException(status_code=400, detail="User is not active. Cannot add items to cart.")

    item=(db.query(models.Item).filter(models.Item.id==item_id).first())
    logging.info(f"Item query result for item_id={item_id}, required_qty={quantity}: {item}")

    if not item:
            raise HTTPException(status_code=404,detail=f"item with id {item_id} not found or out of stock")
    
    if item.quantity < quantity:
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
             
         
    except Exception as e:
        # Log full stack trace to help diagnose the server-side failure
        logging.exception(f"Error checking for existing cart info for user {user_id} and item {item_id}")
       
        db.rollback()
        
        raise HTTPException(status_code=500, detail=f"Internal error")
    except KeyError as e:
        logging.error(f"Key error while processing cart item for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while processing cart item {e}")
    db.add(out)
    db.commit() 
    db.refresh(out)
            # convert Decimal price values to float for pydantic and compute total using the cart item's quantity
    return pmod.CartItemsOut(item_id=out.item_id,
                             quantity=out.quantity,
                            name=str(item.name),
                            description=item.description,
                            price=float(item.price),
                            totalprice=float(out.quantity) * float(item.price))





class CartService:
    def __init__(self, db: Session, user_id: int, cart_id: int):
        self.db = db

        self.userService = UserService(db, user_id=user_id, email=None)  # Initialize UserService with user_id
        if not self.userService.filter_user(status=pmod.UserStatus.active):  # Filter user by active status
            raise HTTPException(status_code=400, detail="User is not active. Cannot modify cart.")

        self.cart = FindCart(cart_id=cart_id)
        if not self.cart:
            raise HTTPException(status_code=404, detail="Cart not found for this user")
        

    def FindCart(self,cart_id:int):
        """this gets a cart User info when a user_id and Cart_id are in a relashinship """
        try:
            cart=(self.db.query(models.Cart.id,models.Cart.cart_date,models.Cart.user_id,models.User.status)
          .filter(models.Cart.user_id == self.UserService.user.id, models.Cart.id == cart_id)
          .join(models.User, models.User.id == models.Cart.user_id)).first()
    
            if not cart:
                return None
        
            return cart
    
        except Exception as e:
            logging.error(f"error retrieving user cart: {e}")
            raise e

    
    def getcart(self, cart_id: int):
        """reusable serves to retreave a users carts info and then returns a pydantic model"""
        
        # this query will join with 
        cart=(self.db.query(models.Cart.id,models.Cart.cart_date,models.Cart.user_id,models.User.status)
            .filter(models.Cart.user_id == self.UserService.user.id, models.Cart.id == cart_id)
            .join(models.User, models.User.id == models.Cart.user_id)).first()

        if not cart:
            logging.info(f"No cart found for user {self.UserService.user.id}.")
            raise HTTPException(status_code=404, detail="Cart not found for this user")
            
        return cart
        


class UserService:
    def __init__(self, db: Session, user_id: int|None, email: str|None):
        self.db = db
        if user_id is not None and email is not None:
            raise ValueError("Provide either user_id or email, not both.")

        self.user = self.get_user(user_id=user_id, email=email)  # Retrieve the user model during initialization

    def filter_user(self, status: pmod.UserStatus = pmod.UserStatus.active):
        """Filter the user by status. Returns the user model if it matches the status, otherwise returns None."""
        if not self.user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if self.user.status != status:
            return None
        
        return self.user

    def get_user(self, user_id: int | None = None, email: str | None = None):
        """Retrieve the user model for the given user_id."""
        try:
            if user_id is not None:
                user = (self.db.query(models.User).filter(models.User.id == user_id).first()) 
            elif email is not None:
                email = email.strip()
                user = (self.db.query(models.User).filter(models.User.email == email).first())
            else:
                raise ValueError("Either user_id or email must be provided.")

            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except Exception as e:
            logging.error(f"Error retrieving user {user_id or email}: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while retrieving the user")

    