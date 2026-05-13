from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import  get_db
import api.models.sqlAmodels as models
from api.psycopg_models import item,createitem, updateitem, ItemSchema
from typing import List, Optional
from sqlalchemy import text
from api.services.item_s import Serviceitems
router = APIRouter(prefix="/items", tags=["items"])

# READ all items
@router.get("/get_all",response_model = List[ItemSchema])
def readAllItems(db: Session = Depends(get_db)):
    itemlist= db.query(models.Item).filter(models.Item.quantity > 0).all()

    return itemlist


@router.post("/add_item",response_model=item)
def create_item(newitems:createitem, db: Session = Depends(get_db)):
    """add a item to the stores inventory"""
    name=newitems.name.strip().lower().strip()
    description=newitems.description.strip()

    existing = db.query(models.Item).filter(models.Item.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")
    try:
         out = models.Item(name=name, description=description, quantity=newitems.quantity, price=newitems.price)
         db.add(out)
         db.commit()
         
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating item {e}") from e
    return out

# UPDATE an item
@router.put("/{item_id}/update",response_model=ItemSchema)
def update_item(item_id: int,update:updateitem, db: Session = Depends(get_db)):
    """update a items infermation"""
    service = Serviceitems(db=db)
    items=service.get_items(item_id)
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    try:
        if update.quantity != None:
            items.quantity = update.quantity
        if update.price:
            items.price = update.price
        if update.description:    
            items.description=update.description
        db.commit()
        db.refresh(items)
        
        return ItemSchema(id=items.id,name=items.name, description=items.description, quantity=items.quantity, price=items.price)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating item {e}") from e
    

#get items details
@router.get("/{item_id}/details",response_model=item)
def getItem(item_id: int, db: Session = Depends(get_db)):
    """gets items infermation"""
    service = Serviceitems(db=db)
    items=service.get_active_items(item_id)
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    #if items.quantity == 0: this is now handled by the get_active_items function
    #    raise HTTPException(status_code=404, detail="Item is out of stock")
    out=item(name=items.name, description=items.description, quantity=items.quantity, price=items.price, id=items.id)
    return out



# DELETE an item
"""@router.delete("/{item_id}/delete",response_model=item)
def deleteItem(item_id: int, db: Session = Depends(get_db)):
    deletes an item from the inventory
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
"""    