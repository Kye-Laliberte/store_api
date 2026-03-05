#venv\Scripts\Activate.ps1
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
#import models
from .import  sqlAmodels as models 
import logging
from .routers.items_route import router  as item_router 
from .routers.carts_route import router as cart_router
from .routers.users_route import router as user_router 
from .database import get_db,engine,LocalSession

models.Base.metadata.create_all(bind=engine) 
app = FastAPI(title="Inventory API")
app.include_router(item_router)
app.include_router(cart_router)
app.include_router(user_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def get_datab():
    bd= LocalSession()
    try:
        yield bd
    finally:
        bd.close()

@app.get("/")
def home():
    return {"message":"Welcome to the shping API its a work in progress."}

#uvicorn api.main:app --reload
