from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import  get_db
from ..import sqlAmodels as models
from ..psycopg_models import item,createitem 
from typing import List, Optional

router = APIRouter(prefix="/items", tags=["items"])

# READ all items
@router.get("/get_all")
def readAllItems(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

# CREATE an item
@router.post("/add_item",response_model=List[item])
def create_item(item:createitem, db: Session = Depends(get_db)):
    name=item.name.strip().lower()
    description=item.description.strip()
    if item.price<0:
        raise HTTPException(status_code= 200, detail="can not have a 0 or negative price" )
    if item.quantity<0:
        raise HTTPException(status_code=200, detail="can not have a negative inventory")
    existing = db.query(models.Item).filter(models.Item.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")
    item = models.Item(name=item.name, description=description, quantity=item.quantity, price=item.price)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# UPDATE an item
@router.put("/{item_id}/update",response_model=item)
def update_item(item_id: int, quantity: int = None, price: float = None, db: Session = Depends(get_db)):

    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if quantity is not None:
        item.quantity = quantity
    if price is not None:
        item.price = price
    db.commit()
    db.refresh(item)
    return item

#get items detales
@router.get("/{item_id}/detals",response_model=item)
def getItem(item_id: int, db: Session = Depends(get_db)):
    item=db.query(models.Item).filter(models.Item.id ==item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item

# DELETE an item
@router.delete("/{item_id}/delete",response_model=item)
def deleteItem(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return item