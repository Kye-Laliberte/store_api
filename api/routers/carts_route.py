from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..import sqlAmodels as models
from typing import List, Optional
from ..psycopg_models import CartItemsOut,carts,create_cartItem,createCart

router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcom to the store grab a cart"}

@router.get("/{cart_id}/viewcart",response_model=List[CartItemsOut])
def viewCart(cart_id:int,db: Session=Depends(get_db)):

    cartItems = (db.query(models.CartItem.item_id,
                           models.CartItem.quantity,
                           models.Item.description,
                           models.Item.name,
                           models.Item.price)
                           .join(models.Item, models
                                 .CartItem.item_id == models.Item.id)
                                 .filter(models.CartItem.cart_id == cart_id).all()
)
    
    if not cartItems:
        raise HTTPException(status_code=404, detail="Cart is empty")
        
    return cartItems
    

@router.post("{user_id}/newcart", response_model=carts)
def new_cart(cart:createCart,user_id:int, db: Session = Depends(get_db)):
    
    newcart = models.Cart(user_id=user_id,purchase_date=cart.purchase_date)
    
    db.add(newcart)
    db.commit()
    db.refresh(newcart)
    return newcart


"""
@router.post("/{user_id}/additem",response_model="cart_items")
def additem(user_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    cart_item = models.CartItem(user_id=user_id, item_id=item.item_id, quantity=item.quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item
   

@router.delete("/{user_id}/removeitem",response_model="cart_items")
def leaveitem(user_id:int,db:Session=Depends(get_db)):
    cart=db.query(models.CartItem).filter(models.CartItem.user_id==user_id,models.CartItem.item_id==item_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(cart)
    db.commit()

router.put("/{user_id}/purchaseItems",response_model=List[cartItemsout])
def purchaseItems(user_id:int,db:Session=Depends(get_db)):
     items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
     if not items:
        raise HTTPException(status_code=404, detail="Cart is empty")
        work out purchis logic 

#purchies items""" 