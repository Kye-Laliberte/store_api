#venv\Scripts\Activate.ps1

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import  api.models.sqlAmodels as models
import  api.models.ordermodels as Omodels 
import logging
from api.routers.items_route import router  as item_router 
from api.routers.carts_route import router as cart_router
from api.routers.users_route import router as user_router
from api.routers.order_route import router as order_router 
from api.database import get_db,engine,LocalSession
from sqlalchemy import text
models.Base.metadata.create_all(bind=engine)
Omodels.Base.metadata.create_all(bind=engine)
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Inventory API")
app.include_router(item_router)
app.include_router(cart_router)
app.include_router(user_router)
app.include_router(order_router)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
# Set up CORS middleware to allow requests from the frontend
app.add_middleware( CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"]
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
