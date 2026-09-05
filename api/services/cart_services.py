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


def getcart(user_id: int, db: Session):
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).first()

def FindCart(user_id: int, cart_id: int, db: Session):
    """this gets a cart User info when a user_id and Cart_id are in a relashinship """
    try:
        cart=(db.query(models.Cart.id,models.Cart.cart_date,models.Cart.user_id,models.User.status)
      .filter(models.Cart.user_id == user_id, models.Cart.id == cart_id)
      .join(models.User, models.User.id == models.Cart.user_id)).first()
    except Exception as e:
        logging.error(f"error retrieving user cart: {e}")
        raise e
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found for this user")
    return cart
        

def newcart(db: Session, user_id: int):
    """deletes a users existing cart if it exists then
      creates a new cart for a user and returns the cart sql model"""
    cart_date = datetime.now()
    new_cart = models.Cart(user_id=user_id, cart_date=cart_date)
    
    if not UserService(db=db, user_id=user_id).filter_user(status=pmod.UserStatus.active):
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


def getcart_item(cart_id:int,item_id:int, db: Session):
    try:
        cartitem = (db.query(models.CartItem)
                  .filter(models.CartItem.cart_id == cart_id,  models.CartItem.item_id == item_id)).first()
        if not cartitem:
            return False
        
        return cartitem    
    except Exception as e:
        logging.error(f"error retrieving cartitem: {e}")
        raise e


    getcaritem = getcart_item
  

def new_user(email:str,password:str,db:Session):
    if db.query(models.User).filter(models.User.email == email).first():
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



class CartService:
    def __init__(self, db: Session, user_id: int, cart_id: int):
        self.db = db

        self.userService = UserService(db, user_id=user_id, email=None)  # Initialize UserService with user_id
        if not self.userService.filter_user(status=pmod.UserStatus.active):  # Filter user by active status
            raise HTTPException(status_code=400, detail="User is not active. Cannot modify cart.")

        cart = self.FindCart(cart_id=cart_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found for this user")
        self.cart = cart

    def FindCart(self,cart_id:int):
        """this gets a cart User info when a user_id and Cart_id are in a relashinship """
        try:
            cart=(self.db.query(models.Cart.id,models.Cart.cart_date,models.Cart.user_id,models.User.status)
          .filter(models.Cart.user_id == self.userService.user.id, models.Cart.id == cart_id)
          .join(models.User, models.User.id == models.Cart.user_id)).first()
        except Exception as e:
            logging.error(f"error retrieving user cart: {e}")
            raise e
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found for this user")
        return cart
        
    def delete_cart(self, cart_id:int):
        """deletes a cart and all cartitems that are related to the cart_id"""
        try:
            if not self.db.query(models.Cart).filter(models.Cart.id == cart_id).first():
                raise HTTPException(status_code=404, detail=f"Cart with id {cart_id} not found.")    

            self.db.query(models.CartItem).filter(models.CartItem.cart_id==cart_id).delete()
            self.db.query(models.Cart).filter(models.Cart.id==cart_id).delete()
            self.db.commit()
            return True
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error occurred while dropping the cart for cart {cart_id}: {e}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail="An error occurred while dropping the cart")

    def additemCart(self,item_id:int,quantity:int,):
        """adds an item to a users cart if the user is active and the item is in stock"""
    
        user_id=self.userService.user.id
        
        logging.info(f"FindCart result for user {user_id}, cart {self.cart.id}: {self.cart}")

        if not self.cart:
            raise HTTPException(status_code=404,detail=" cart not found.")
    
        if self.cart.status != pmod.UserStatus.active:
            raise HTTPException(status_code=400, detail="User is not active. Cannot add items to cart.")

        item=(self.db.query(models.Item).filter(models.Item.id==item_id).first())
        logging.info(f"Item query result for item_id={item_id}, required_qty={quantity}: {item}")

        if not item:
            raise HTTPException(status_code=404,detail=f"item with id {item_id} not found or out of stock")
    
        if item.quantity < quantity:
            logging.error(f"Insufficient stock for item {item_id} while adding to cart for user {user_id}")
            raise HTTPException(status_code=400, detail=f"Insufficient stock for item {item_id}")
    
        try:
            existing = (
            self.db.query(models.CartItem)
            .filter(models.CartItem.cart_id == self.cart.id, models.CartItem.item_id == item_id).first())
        
            if existing:
                existing.quantity = quantity
                out = existing
            else:
                out =models.CartItem(cart_id=self.cart.id, item_id=item_id, quantity=quantity)
             
        except Exception as e:
            # Log full stack trace to help diagnose the server-side failure
            logging.exception(f"Error checking for existing cart info for user {user_id} and item {item_id}")
       
            self.db.rollback()
        
            raise HTTPException(status_code=500, detail=f"Internal error")
        except KeyError as e:
            logging.error(f"Key error while processing cart item for user {user_id} and item {item_id}: {e}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred while processing cart item {e}")
        self.db.add(out)
        self.db.commit() 
        self.db.refresh(out)
            # convert Decimal price values to float for pydantic and compute total using the cart item's quantity
        return pmod.CartItemsOut(item_id=out.item_id,
                             quantity=out.quantity,
                            name=str(item.name),
                            description=item.description,
                            price=float(item.price),
                            totalprice=float(out.quantity) * float(item.price))

    def get_cart_items(self):
        """retrieves all items in the cart that relate to the user_id and returns a list of models with the item name, description, price and quantity"""
        try:
            cart_items = (self.db.query(models.CartItem.item_id,
                                   models.CartItem.quantity,
                                   models.Item.description,
                                   models.Item.name,models.Item.price)
                                   .join(models.Item, models.CartItem.item_id == models.Item.id)
                                         .filter(models.CartItem.cart_id == self.cart.id).all())
            if not cart_items:
                logging.info(f"Cart {self.cart.id} for user {self.userService.user.id} is empty.")
                # return empty list for an empty cart (200 OK)
                return []
            
            return[
                pmod.CartItemsOut(
                    item_id=items.item_id,
                    quantity=items.quantity,
                    description=items.description,
                    price=items.price,
                    name=items.name,
                    totalprice=items.quantity*items.price
                    )
                for items in cart_items
                ]
        except Exception as e:
            logging.error(f"Error retrieving cart items for cart {self.cart.id}: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while retrieving cart items")


class UserService:
    def __init__(self, db: Session, user_id: int|None = None, email: str|None = None):
        self.db = db
        if user_id is not None and email is not None:
            raise ValueError("Provide either user_id or email, not both.")

        self.user = self.get_user(user_id=user_id, email=email)  # Retrieve the user model during initialization

    def filter_user(self, status: pmod.UserStatus = pmod.UserStatus.active) -> bool:
        """Filter the user by status. Returns True if the user matches the status, otherwise returns False."""
        if not self.user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return self.user.status == status

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
        except HTTPException as err:
            raise HTTPException(status_code=err.status_code, detail=err.detail)
        except Exception as e:
            logging.error(f"Error retrieving user {user_id or email}: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while retrieving the user")

    