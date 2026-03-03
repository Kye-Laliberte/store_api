#venv\Scripts\Activate.ps1
from fastapi import FastAPI
import logging

app = FastAPI(title="Inventory API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
@app.get("/")
def home():
    return {"message":"Welcome to the shping API its a work in progress."}

#uvicorn api.main:app --reload