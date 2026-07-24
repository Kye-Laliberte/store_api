from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import  get_db
import models.sqlAmodels as models
from psycopg_models import item,createitem, updateitem, ItemSchema
from typing import List
from services.item_s import get_items,get_active_items,createItem
router = APIRouter(prefix="/items", tags=["items"])

# READ all items
@router.get("/get_all",response_model = List[ItemSchema])
def readAllItems(db: Session = Depends(get_db)):
    itemlist= db.query(models.Item).filter(models.Item.quantity > 0).all()
    if not itemlist:
        return []
    return itemlist


@router.post("/add_item",response_model=item)
def create_item(newitems:createitem, db: Session = Depends(get_db)):
    """add a item to the stores inventory"""
    name=newitems.name.strip().lower().strip()
    description=newitems.description.strip()

    
    try:
        out = createItem(name,description,
                     newitems.price,newitems.quantity,db)
         
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating item {e}") from e
    return out

# UPDATE an item
@router.put("/{item_id}/update",response_model=ItemSchema)
def update_item(item_id: int,update:updateitem, db: Session = Depends(get_db)):
    """update a items infermation"""
    
    items=get_items(item_id,db)
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
    
    items=get_active_items(item_id,db)
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
        
    out=item(name=items.name, description=items.description, quantity=items.quantity, price=items.price, id=items.id)
    return out
