from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import  get_db
import api.models.sqlAmodels as models
from api.psycopg_models import item,createitem 
from typing import List, Optional

router = APIRouter(prefix="/items", tags=["items"])

# READ all items
@router.get("/get_all")
def readAllItems(db: Session = Depends(get_db),response_model =List[item]):
    return db.query(models.Item).all()


@router.post("/add_item",response_model=item)
def create_item(item:createitem, db: Session = Depends(get_db)):
    """add a item to the stores inventory"""
    name=item.name.strip().lower()
    description=item.description.strip()
    if item.price<0:
        raise HTTPException(status_code= 200, detail="can not have a 0 or negative price" )
    if item.quantity<0:
        raise HTTPException(status_code=200, detail="can not have a negative inventory")
    existing = db.query(models.Item).filter(models.Item.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")
    try:
         item = models.Item(name=name, description=description, quantity=item.quantity, price=item.price)
         db.add(item)
         db.commit()
         db.refresh(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating item") from e
    return item

# UPDATE an item
@router.put("/{item_id}/update",response_model=item)
def update_item(item_id: int,description:str=None, quantity: int = None, price: float = None, db: Session = Depends(get_db)):
    """update a items infermation"""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    try:
        if quantity is not None:
            item.quantity = quantity
        if price is not None:
            item.price = price
        if description is not None:    
            item.description=description
        db.commit()
        db.refresh(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating item") from e
    
    return item

#get items details
@router.get("/{item_id}/details",response_model=item)
def getItem(item_id: int, db: Session = Depends(get_db)):
    """gets items infermation"""
    
    item=db.query(models.Item).filter(models.Item.id ==item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# DELETE an item
@router.delete("/{item_id}/delete",response_model=item)
def deleteItem(item_id: int, db: Session = Depends(get_db)):
    """deletes an item from the inventory"""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    try:
       
        db.delete(item)
        db.commit()
        
        return item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting item") from e       
    