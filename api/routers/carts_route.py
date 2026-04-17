import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
from typing import List, Optional
from api.psycopg_models import CartItemsOut,carts,create_cartItem,createCart,purchase,purchaseout
from datetime import datetime
router = APIRouter(prefix="/carts", tags=["carts"])

#add item to cart

@router.get("/")
def carthome():
    return {"message":"welcome to the store grab a cart"}


@router.get("/{user_id}/viewcart",response_model=List[CartItemsOut])
def viewCart(user_id:int,db: Session=Depends(get_db)):
    """retreves all items in the cart that relar to the user_id and returns a list of models with the item name, description, price and quantity"""
    try:
        cart= db.query(models.Cart.id).join(models.User, models.Cart.user_id == models.User.id).filter(models.Cart.user_id==user_id).first()
    except Exception as e:
        logging.error(f"Error retrieving cart for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the cart")
    
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
        logging.info(f"Cart {cart_id} for user {user_id} is empty.")
        raise HTTPException(status_code=404, detail="Cart is empty")
        
    return cartItems
@router.get("/getallcarts",response_model=List[carts])
def GetCarts(db: Session = Depends(get_db)):
    """retreves all of the carts info and returns a list of cart models"""
    return db.query(models.Cart).all()


@router.post("/{user_id}/additem",response_model=CartItemsOut)
def additem(user_id:int, item:create_cartItem,db:Session=Depends(get_db)):
    """adds a item to the cart if it is alredy there it updates the quantity to the new quantity, returns a item model with item name, description, price and quantity"""
    
    quantity=item.quantity
    item_id=item.item_id
    
    if quantity<=0:
        raise HTTPException( status_code=400,detail="cant add less than 1 items to a cart")
    
    try:
        cart=(db.query(models.Cart).filter(models.Cart.user_id==user_id).first())
        Item=(db.query(models.Item).filter(models.Item.id==item_id).first())
    except Exception as e:
        logging.error(f"Error retrieving information for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving information from the database")
    
    if not cart:
            raise HTTPException(status_code=404,detail=" cart not found.")
    if not Item:
            raise HTTPException(status_code=404,detail=f"item with id {item_id} not found")
    
    if Item.quantity < quantity:
            logging.error(f"Insufficient stock for item {item_id} while adding to cart for user {user_id}")
            raise HTTPException(status_code=400, detail=f"Insufficient stock for item {item_id}")
    
    try:
        existing = (
            db.query(models.CartItem)
            .filter(models.CartItem.cart_id == cart.id,models.CartItem.item_id == item_id).first())
        
        if existing:
            existing.quantity = quantity
            out = existing
        else:
            out =models.CartItem(cart_id=cart.id, item_id=item_id, quantity=quantity)
        
        print(Item.quantity, out.quantity)
        
           
        db.add(out)
        db.commit()
        db.refresh(out)

        return {"item_id": out.item_id, "quantity": out.quantity, "name": Item.name, "description": Item.description, "price": Item.price}

    except Exception as e:
        logging.error(f"Error checking for existing cart info for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while checking for existing cart item")
    except KeyError as e:
        logging.error(f"Key error while processing cart item for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while processing cart item")



@router.post("/{user_id}/newcart", response_model=carts)
def newCart(cart:createCart,user_id:int, db: Session = Depends(get_db)):
    """creates a new cart for the user if one does not already exist"""
    
    exists=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    if exists:
        #raise HTTPException(status_code=200,detail="cart alredy active")
         return carts(id=exists.id,user_id=user_id,purchase_date=exists.purchase_date)
        
    try:
        newcart = models.Cart(user_id=user_id, purchase_date=cart.purchase_date)
        db.add(newcart)
        db.commit()
        db.refresh(newcart)
        return newcart       
    except Exception as e:
        logging.error(f"Error creating new cart for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating a new cart")
    
@router.delete("/{user_id}/removeitem",response_model=create_cartItem)
def leaveitem(user_id:int,item_id:int,db:Session=Depends(get_db)):
    """removes a cartItem from the cart if in the cart and returns a item model with the item name, description, price and quantity"""
    cart=db.query(models.Cart).filter(models.Cart.user_id==user_id).first()
    if not cart:
        raise HTTPException(status_code=404,detail=" Cart not found")
    
    cartitem=(db.query(models.CartItem)
              .filter(cart.id==models.CartItem.cart_id,item_id==models.CartItem.item_id).first())
    if not cartitem:
        raise HTTPException(status_code=404, detail="Item not in cart.")
    
    try:    
        db.delete(cartitem)
        db.commit()
        return cartitem
    except Exception as e:
        logging.error(f"Error occurred while querying cart item for user {user_id} and item {item_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while removing item from cart")
    
    
    
@router.delete("/{user_id}/dropCart",response_model=carts)
def dropcart(user_id:int,db:Session=Depends(get_db)):
    """removes all items from the cartItems tabel pertaning to the user_id and removes the cart from the Cart tebel"""
    cart=(db.query(models.Cart)
          .filter(models.Cart.user_id==user_id).first()
          )
    if not cart:
        raise HTTPException(status_code=404,detail="no cart active or found")
    
    db.query(models.CartItem).filter(models.CartItem.cart_id==cart.id).delete()
    
    db.delete(cart)
    db.commit()

    return cart
    
"""
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
"""    
        
    
               
    

    