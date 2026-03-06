from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..import sqlAmodels as models
from passlib.context import CryptContext
from typing import List, Optional
from ..psycopg_models import users
router = APIRouter(prefix="/users", tags=["users"])
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE a new user
@router.post("/addUser")
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == email).first()
    email=email.lower().strip()
    password=password.strip()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    #if len(password.encode('utf-8')) > 72:
    #    raise HTTPException(status_code=400, detail="Password too long (max 72 bytes).")

    #hashed_password = pwd_context.hash(password)
   #pwd_context becam corupted as a file so im teporaraly leaving it out
    #AttributeError: module 'bcrypt' has no attribute '__about__'
    if(len(password) >5 or (password<15)):
        raise HTTPException(status_code=400, detail="Password too long (max 72 bytes).")
    
    user = models.User(email=email, password_hash=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@router.get("/{email}/RetrievePasword",response_model=users)
def getUser(email:str,db:Session=Depends(get_db)):
    email=email.strip().lower()
    user=db.query(models.User).filter(models.User.email==email).first()
    if not user:
        HTTPException(status_code=404,detail="Email not found")
    return user


# READ all users
@router.get("/getAll",response_model=List[users])
def read_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "email": u.email, "created_at": u.created_at} for u in users]

# READ user by ID
@router.get("/{user_id}",response_model=users)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "created_at": user.created_at}