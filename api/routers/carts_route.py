from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..import sqlAmodels as models
from typing import List, Optional
from ..psycopg_models import CartItemsOut,carts,create_cartItem,createCart,purchase
from datetime import datetime
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
                           .join(models.Item, models.CartItem.item_id == models.Item.id)
                                 .filter(models.CartItem.cart_id == cart_id).all()
)
    
    if not cartItems:
        raise HTTPException(status_code=404, detail="Cart is empty")
        
    return cartItems
@router.get("/getallcarts")
def GetCarts(db: Session = Depends(get_db)):
    return db.query(models.Cart).all()

@router.post("/{user_id}/additem",response_model=CartItemsOut)
def additem(user_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    quantity=item.quantity
    item_id=item.item_id
    if quantity<=0:
        raise HTTPException( status_code=400,detail="cant add less than 1 items to a cart")
    cart=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    
    if not cart:
        raise HTTPException(status_code=404,detail=" cart not found.")
    
    cart_id=cart.id
    
    existing = (db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_id,
        models.CartItem.item_id == item_id
    ).first()
    )
    if existing:
        existing.quantity = item.quantity
        db.commit()
        
        
    if not existing:
        cart_item = models.CartItem(cart_id=cart_id, item_id=item_id, quantity=quantity)
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    
    cartItem= (
        db.query(models.CartItem,
                        models.CartItem.quantity,
                        models.CartItem.item_id,
                        models.Item.description,
                        models.Item.name,
                        models.Item.price).join(models.Item,models.CartItem.item_id==models.Item.id).filter(models.Item.id==models.Item.id)
                        .filter(models.CartItem.cart_id==cart_id).filter(models.Item.id == item.item_id).first()
    )
    if not cartItem:
        raise HTTPException(status_code=404, detail="faled to join")
    return cartItem


@router.post("{user_id}/newcart", response_model=carts)
def newCart(cart:createCart,user_id:int, db: Session = Depends(get_db)):
    
    purchase_date=cart.purchase_date
    newcart = models.Cart(user_id=user_id,purchase_date=cart.purchase_date)
    
    db.add(newcart)
    db.commit()
    db.refresh(newcart)
    
    return {"id":models.Cart.id,"user_id":user_id,"purchase_date":purchase_date}


@router.delete("/{user_id}/removeitem",response_model=create_cartItem)
def leaveitem(user_id:int,item_id:int,db:Session=Depends(get_db)):
   
    cart=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    if not cart:
       raise HTTPException(status_code=404,detail=" Cart not found")
    
    cartitem=(db.query(models.CartItem)
              .filter(cart.id==models.CartItem.cart_id,item_id==models.CartItem.item_id).first()
    )
    if not cartitem:
        raise HTTPException(status_code=404, detail="Item not in cart.")
    
    db.delete(cartitem)
    db.commit()
    return cartitem


@router.delete("/{user_id}/dropCart",response_model=carts)
def dropcart(user_id:int,db:Session=Depends(get_db)):
    cart=(db.query(models.Cart)
          .filter(models.Cart.user_id==user_id).first()
          )
    if not cart:
        raise HTTPException(status_code=404,detail="no cart active or found")
    
    db.query(models.CartItem).filter(models.CartItem.cart_id==cart.id).delete()
           
    db.delete(cart)
    db.commit()

    return cart
    
    
@router.post("/{user_id}/PurchaseItems",response_model=CartItemsOut)
def purchaseItem(user_id:int,input:purchase,db:Session=Depends(get_db)):
    

    cart =db.query(models.Cart).filter(models.Cart.user_id == user_id).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    item_id=input.item_id
    cart_id=cart.id
    cartitem=(db.query(models.CartItem)
              .filter(models.CartItem.cart_id==cart_id,models.CartItem.item_id==item_id).first()
    )
    if not cartitem:
        raise HTTPException(status_code=404,detail="item not in cart")
    
    item=(db.query(models.Item).filter(models.Item.id==item_id).first())
    
    if not item: 
        raise HTTPException(status_code=404)
    
    quantity=cartitem.quantity
    itemquantity=item.quantity

    if quantity>itemquantity:
      raise HTTPException(status_code=400,detail=f"to few items in stock only {quantity} avalibal")
    itemquantity=itemquantity-quantity
    
    item.quantity=itemquantity

    db.delete(cartitem)
    db.commit()
    

@router.post("/{user_id}/PurchaseCart",response_model=List[CartItemsOut])
def buyCart(user_id:int,db:Session=Depends(get_db)):
    """removes all items from the cartItems tabel pertaning to the user_id and removse them from the Item tebel"""
    
    cart=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    print("cart:", cart)
    if not cart:
       raise HTTPException(status_code=404,detail=" Cart not found")

    cart_id=cart.id
    cartItems=(db.query(models.CartItem).filter(models.CartItem.cart_id==cart_id).all()
    )
    if  not cartItems:
        raise HTTPException(status_code=200,detail="cart is empty")

    for cart_items in cartItems:
        db.delete(cart_items)
        
        items=(db.query(models.Item).filter(models.Item.id==cart_items.item_id).first())
        if  not items:
            raise HTTPException(status_code=404,detail=f"Item not found {items.item_id}")
        
        if items.quantity<cart_items.quantity:
            raise HTTPException(status_code=400,detail=f"Not enough in stock {items.id}")
        
        items.quantity -= cart_items.quantity

    db.commit()

    return cartItems
        
    
               
    

    