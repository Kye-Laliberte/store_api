from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import  get_db
from ..import sqlAmodels as models

router = APIRouter(prefix="/items", tags=["items"])

# READ all items
@router.get("/")
def read_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

# CREATE an item
@router.post("/add_item")
def create_item(name: str, description: str = None, quantity: int = 0, price: float = 0.0, db: Session = Depends(get_db)):
    existing = db.query(models.Item).filter(models.Item.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")
    item = models.Item(name=name, description=description, quantity=quantity, price=price)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# UPDATE an item
@router.put("/{item_id}/update")
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
@router.get("/{item_id}/detals")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item=db.query(models.Items).filter(models.Item.id ==item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item
# DELETE an item
@router.delete("/{item_id}/delete")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Item deleted"}