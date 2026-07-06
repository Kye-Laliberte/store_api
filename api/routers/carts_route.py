import logging
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
from typing import List
from api.psycopg_models import CartItemsOut, cartpacage,carts,create_cartItem,UserStatus
from api.services.cart_services import additemCart, filter_user, getcart, newcart,FindCart,getcaritem,delete_cart
router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcome to the store grab a cart"}


@router.get("/{user_id}/viewcart/{cart_id}",response_model=List[CartItemsOut])
def viewCart(user_id:int,cart_id:int, db: Session=Depends(get_db)):
    """retreves all items in the cart that relar to the user_id and returns a list of models with the item name, description, price and quantity"""
    
    cart=FindCart(user_id,cart_id, db)

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
        raise HTTPException(status_code=200, detail=f"User {user_id} has an empty cart.")
    
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
def addtoCart(user_id:int,cart_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    """adds a item to the cart if it is alredy there it updates the quantity to the new quantity, returns a item model with item name, description, price and quantity"""
    
    quantity=item.quantity
    item_id=item.item_id
    
    if quantity<=0:
        raise HTTPException( status_code=400,detail="cant add less than 1 items to a cart")
    

    
    try:
        
        cartitem=additemCart(item_id=item_id, user=cartpacage(user_id=user_id, cart_id=cart_id), quantity=quantity, db=db)
    
        existing = (
            db.query(models.CartItem)
            .filter(models.CartItem.cart_id == cart_id, models.CartItem.item_id == item_id).first())
        
        if existing:
            existing.quantity = quantity
            out = existing
        else:
            out =models.CartItem(cart_id= cart_id, item_id=item_id, quantity=quantity)
             
           
        db.add(out)
        db.commit()
        db.refresh(out)
        return CartItemsOut(item_id=out.item_id, quantity=out.quantity,name=cartitem.name,
                            description=cartitem.description,price=cartitem.price,
                            totalprice=cartitem.quantity*cartitem.price)
         
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
         raise HTTPException(status_code=200,detail="cart alredy active")
    
    try:
        
        out_cart=newcart(user_id,db=db)

        if not out_cart:
            raise HTTPException(status_code=500, detail="Failed to create new cart")
        
        return out_cart
    
    except Exception as e:
        logging.error(f"Error creating new cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating a new cart")
    
@router.delete("/{cart_id}/{user_id}/removeitem/{item_id}",response_model=create_cartItem)
def leaveitem(item_id:int,cart_id:int,user_id:int,db:Session=Depends(get_db)):
    """delete a cartItem that  relats to carts.id== cartitems.cart_id belongs to carts.user_id
    returns item_id quantity of cartitem"""
    print(f"Received request to remove item {item_id} from cart {cart_id} for user {user_id}")
    cart = FindCart(cart_id=cart_id,user_id=user_id,db=db)
    if not cart.id:# Ensure the cart exists user_id is not needed for this check
        raise HTTPException(status_code=404, detail="Cart not found.")
    
    cartitem = getcaritem(cart_id=cart_id,item_id=item_id,db=db)
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
   
    try:
        cart=FindCart(user_id=user_id,cart_id=cart_id,db=db)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found.")
            
        delete_cart(cart_id=cart_id,db=db)
        
        return carts(id=cart.id,user_id=cart.user_id,cart_date=cart.cart_date)
    except Exception as e:
        logging.error(f"Error occurred while dropping the cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while dropping the cart")
        

        
    
               
    

    