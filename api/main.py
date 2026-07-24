from fastapi import FastAPI
import logging
from routers.items_route import router  as item_router 
from routers.carts_route import router as cart_router
from routers.users_route import router as user_router
from routers.order_route import router as order_router 
from database import LocalSession
import uvicorn
#models.Base.metadata.create_all(bind=engine)
#Omodels.Base.metadata.create_all(bind=engine)

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


    
#uvicorn api.main:app --reload
