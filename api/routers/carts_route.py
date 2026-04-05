from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import sqlAmodels as models
from typing import List, Optional
from psycopg_models import CartItemsOut,carts,create_cartItem,createCart,purchase,purchaseout
from datetime import datetime
router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcome to the store grab a cart"}


@router.get("/{user_id}/viewcart",response_model=List[CartItemsOut])
def viewCart(user_id:int,db: Session=Depends(get_db)):
    cart= db.query(models.Cart.id).filter(models.Cart.user_id==user_id).first()
    
    if not cart:
        raise HTTPException(status_code=404,detail=f"no cart found or active for {user_id}")
    cart_id=cart.id
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
    cart=(db.query(models.Cart.id)
          .filter(models.Cart.user_id==user_id).first()
    )
    if not cart:
        raise HTTPException(status_code=404,detail=" cart not found.")
    
    cart_id=cart.id
    
    existing = (db.query(models.CartItem).filter(
    models.CartItem.cart_id == cart_id,models.CartItem.item_id == item_id).first())
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
    exists=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    if exists:
        #raise HTTPException(status_code=200,detail="cart alredy active")
        return {"id":exists.id,"user_id":user_id,"purchase_date":exists.purchase_date}
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
    
    
@router.post("/{user_id}/PurchaseItems",response_model=purchaseout)
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
        
    item.quantity -= quantity 
    toalprice=quantity*item.price 
    outitem=({"cart_id":cart_id,"item_id":cartitem.item_id,"name":item.name,
              "quantity":cartitem.quantity,"totalprice":toalprice})
    
   
    db.delete(cartitem)
    
    try:   
        db.commit()
        return outitem
    except:
        db.rollback()

@router.post("/{user_id}/PurchaseCart",response_model=List[purchaseout])
def buyCart(user_id:int,db:Session=Depends(get_db)):
    """removes all items from the cartItems tabel pertaning to the user_id and removse them from the Item tebel"""
    
    cart=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    print("cart:", cart)
    if not cart:
       raise HTTPException(status_code=404,detail=" Cart not found")

    cart_id=cart.id
    cartItems=(db.query(models.CartItem, models.Item)
               .join(models.Item,models.CartItem.item_id==models.Item.id)
               .filter(models.CartItem.cart_id==cart_id).all()
    )
    if  not cartItems:
        raise HTTPException(status_code=400,detail="cart is empty")
    
    purchase=[]
    
    for cart_items, item in cartItems:
        
        if  not item:
            raise HTTPException(status_code=404,detail=f"Item not found {cartItems.item_id}")
        
        if item.quantity<cart_items.quantity:
            raise HTTPException(status_code=400,detail=f"Not enough in stock {item.id}")
    totalprice=0
    for cart_item, items in cartItems:
        totalprice=cart_item.quantity*items.price
        items.quantity -= cart_item.quantity
        val={"cart_id":cart_item.cart_id,"item_id":items.id,"name": items.name,"totalprice": totalprice,"quantity":cart_item.quantity}
        purchase.append(val)
        db.delete(cart_item)
    
    
    try:
        db.commit()
        return purchase
    except:
        db.rollback
    
        
    
               
    

    