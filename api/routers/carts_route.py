from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..import sqlAmodels as models
from typing import List, Optional
from psycopg_models import cartItemsout,carts,createCart,create_cartItem

router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcom to the store grab a cart"}

@router.get("{cart_id}/viewcart",List[cartItemsout])
def viewCart(user_id:int,db: Session=Depends(get_db)):
    cartitems = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    if not cartitems:
        raise HTTPException(status_code=404, detail="Cart is empty")
    return cartitems

@router.post("/newcart", response_model=carts)
def new_cart(user_id: int, db: Session = Depends(get_db)):
    cart = models.Cart(user_id=user_id)
    
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

@router.post("/{user_id}/additem",response_model="cart_items")
def additem(user_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    cart_item = models.CartItem(user_id=user_id, item_id=item.item_id, quantity=item.quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item
    

@router.delete("/{user_id}/leaveCart")
def leaveCart():
    print()

@router.delete("/{user_id}/removeitem",response_model="cart_items")
def leaveitem(user_id:int,db:Session=Depends(get_db)):
    cart=db.query(models.CartItem).filter(models.CartItem.user_id==user_id,models.CartItem.item_id==item_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(cart)
    db.commit()
router.put("/purchaseItems",List[cartItemsout])
def purchaseItems():
    print()

#purchies items