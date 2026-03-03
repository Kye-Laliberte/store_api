#venv\Scripts\Activate.ps1
from database import SessionLocal,engine
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import sqlAmodels 
import logging

sqlAmodels.Base.metadata.create_all(bind=engine) 
app = FastAPI(title="Inventory API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def get_datab():
    bd= SessionLocal()
    try:
        yield bd
    finally:
        bd.close()

@app.get("/")
def home():
    return {"message":"Welcome to the shping API its a work in progress."}

#uvicorn api.main:app --reload
@app.post("/items/")
def create_item(name: str, description: str = None, quantity: int = 0, price: float = 0.0, db: Session = Depends(get_db)):
    existing = db.query(models.Item).filter(models.Item.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")
    item = models.Item(name=name, description=description, quantity=quantity, price=price)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item