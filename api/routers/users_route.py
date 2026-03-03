from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])