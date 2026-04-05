#venv\Scripts\Activate.ps1
from unittest import result

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
#import models
import  sqlAmodels as models
import  models.ordermodels as Omodels 
import logging
from routers.items_route import router  as item_router 
from routers.carts_route import router as cart_router
from routers.users_route import router as user_router 
from database import get_db,engine,LocalSession
from sqlalchemy import text
models.Base.metadata.create_all(bind=engine)
Omodels.Base.metadata.create_all(bind=engine)

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

def testConnection():
    """Test the database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 "))
            print("Database connection test result:", result.fetchone())
            logging.info("Database connection test successful.", extra={"result": result.fetchone()})
    except Exception as e:
        logging.error("Database connection test failed.", exc_info=True)
        print("Database connection test failed:", e)

def test_sqlalchemy():
    """Test SQLAlchemy session."""
    try:
        with LocalSession() as session:
            result = session.execute(text("SELECT 1"))
            print("SQLAlchemy session test result:", result.fetchone())
            logging.info("SQLAlchemy session test successful.", extra={"result": result.fetchone()})
    except Exception as e:
        logging.error("SQLAlchemy session test failed.", exc_info=True)
        print("SQLAlchemy session test failed:", e)

if __name__ == "__main__":
    testConnection()     
    test_sqlalchemy()
    
    
#uvicorn api.main:app --reload
