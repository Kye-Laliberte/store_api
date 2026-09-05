import logging
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models.sqlAmodels as models
from typing import List
from psycopg_models import CartItemsOut,carts,create_cartItem,UserStatus
from services.cart_services import CartService, UserService, newcart, getcart_item, getcart,FindCart
router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcome to the store grab a cart"}


@router.get("/{user_id}/viewcart/{cart_id}",response_model=List[CartItemsOut], status_code=200)
def viewCart(user_id:int,cart_id:int, db: Session=Depends(get_db)):
    """retreves all items in the cart that relar to the user_id and returns a list of models with the item name, description, price and quantity"""
    
    cart=CartService(db,user_id,cart_id).cart
    
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
        # return empty list for an empty cart (200 OK)
        return []
    
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

@router.get("/getallcarts",response_model=List[carts], status_code=200)
def GetCarts(db: Session = Depends(get_db)):
    """retreves all of the carts info and returns a list of cart models"""
    out=db.query(models.Cart).all()
    return out

@router.post("/{user_id}/additem/{cart_id}",response_model=CartItemsOut, status_code=201)
def addtoCart(user_id:int,cart_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    """adds a item to the cart if it is alredy there it updates the quantity to the new quantity, returns a item model with item name, description, price and quantity"""
    
    quantity=item.quantity
    item_id=item.item_id
    
    if quantity<=0:
        raise HTTPException( status_code=400,detail="cant add less than 1 items to a cart")
    
    try:
        if not CartService(db,user_id,cart_id).userService.filter_user(status=UserStatus.active):

            cartitem = CartService(db,user_id,cart_id).add_item(item_id=item_id, quantity=quantity)
        
        return cartitem
    except HTTPException as err:
        # service raises HTTPException for expected client errors (e.g., 404, 400) — propagate them unchanged
        raise err
    except Exception as e:
        logging.exception(f"Unexpected error while adding item {item_id} to cart {cart_id} for user {user_id}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while checking for existing cart item")
    

@router.post("/{user_id}/newcart", response_model=carts, status_code=201)
def newCart(user_id:int, db: Session = Depends(get_db)):
    """creates a new cart for the user if one does not already exist"""
    
    user=CartService(db,user_id).userService.filter_user(status=models.UserStatus.active)
    if not user:
        raise HTTPException(status_code=404, detail="user not found or is inactive")
    
    exists=CartService(db,user_id).get_cart()
    if exists:
         raise HTTPException(status_code=400, detail="Cart already active")
    
    try:
        
        out_cart=newcart(user_id,db=db)

        if not out_cart:
            raise HTTPException(status_code=500, detail="Failed to create new cart")
        
        return out_cart
    
    except Exception as e:
        logging.error(f"Error creating new cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating a new cart")
    
@router.delete("/{cart_id}/{user_id}/removeitem/{item_id}",response_model=create_cartItem, status_code=200)
def leaveitem(item_id:int,cart_id:int,user_id:int,db:Session=Depends(get_db)):
    """delete a cartItem that  relats to carts.id== cartitems.cart_id belongs to carts.user_id
    returns item_id quantity of cartitem"""
    
    cartitem = CartService(db, user_id, cart_id).getcaritem(cart_id=cart_id, item_id=item_id)
    if not cartitem:
        raise HTTPException(status_code=404, detail="Item not in cart.")
    
    try:    
        db.delete(cartitem)
        db.commit()
        item=CartService(db, user_id, cart_id).create_cartItem(item_id=cartitem.item_id, quantity=cartitem.quantity)
        return item
    except Exception as e:
        logging.error(f"Error occurred while querying cart item for cart {cart_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while removing item from cart")
    
@router.delete("/{user_id}/dropCart/{cart_id}",status_code=204)
def dropcart(user_id:int,cart_id:int,db:Session=Depends(get_db)):
    """removes all items from the cartItems tabel pertaning to the user_id and removes the cart from the Cart tebel"""
   
    try:
        
            
        CartService(db,user_id,cart_id).delete_cart(cart_id=cart_id)
        
        
    except Exception as e:
        logging.error(f"Error occurred while dropping the cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while dropping the cart")
        

        
    
               
    

    