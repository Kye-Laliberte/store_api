from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import  get_db
import models.sqlAmodels as models
from psycopg_models import item,createitem, updateitem, ItemSchema
from typing import List
from services.item_s import createItem,ItemService
from core.security import get_current_user
router = APIRouter(prefix="/items", tags=["items"])

# READ all items
@router.get("/get_all",response_model = List[ItemSchema],status_code=200)
def readAllItems(db: Session = Depends(get_db)):
    itemlist= db.query(models.Item).filter(models.Item.quantity > 0).all()
    if not itemlist:
        return []
    return itemlist


@router.post("/add_item",response_model=item, status_code=201)
def create_item(newitems:createitem, db: Session = Depends(get_db)):
    """add a item to the stores inventory"""
    name=newitems.name.strip().lower().strip()
    description=newitems.description.strip() if newitems.description else None
    
    try:
        out = createItem(name,description,
                     newitems.price,newitems.quantity,db)
         
    except HTTPException:
        raise HTTPException(status_code=400, detail="Item already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating item {e}") from e
    return out

# UPDATE an item
@router.put("/{item_id}/update",response_model=ItemSchema, status_code=200)
def update_item(item_id: int,update:updateitem, db: Session = Depends(get_db)):
    """update a items infermation"""
    
    items=ItemService(db,item_id).item
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
@router.get("/{item_id}/details",response_model=item, status_code=200)
def getItem(item_id: int, db: Session = Depends(get_db)):
    """gets items infermation"""
    
    items=ItemService(db,item_id).item
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
        
    out=item(name=items.name, description=items.description, quantity=items.quantity, price=items.price, id=items.id)
    return out
