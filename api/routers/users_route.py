from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
from passlib.context import CryptContext
from typing import List, Optional
from api.psycopg_models import users,userOut, login
from passlib.hash import bcrypt

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE a new user
@router.post("/addUser")
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    exist = db.query(models.User).filter(models.User.email == email).first()
    email=email.lower().strip()
    password=password.strip()

    if exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if len(password.encode('utf-8')) < 9:
        raise HTTPException(status_code=400, detail="Password too shot.")

    hashed_password = pwd_context.hash(password)
     
    if(len(hashed_password)>72):
        raise HTTPException(status_code=400, detail=f"{len(hashed_password)}Password too long (max 72 bytes).")
    
    user = models.User(email=email, password_hash=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "created_at": user.created_at, "password_hash":hashed_password}


@router.get("/{email}/RetrievebyEmail",response_model=users)
def getUser(email:str,db:Session=Depends(get_db)):
    email=email.strip().lower()
    user=db.query(models.User).filter(models.User.email==email).first()
    if not user:
        raise HTTPException(status_code=404,detail="Email not found")
    return {"id": user.id,"email": user.email,"created_at": user.created_at}


# READ all users
@router.get("/getAll",response_model=List[users])
def getUsers(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "email": u.email, "created_at": u.created_at} for u in users]

# READ user by ID
@router.get("/{user_id}",response_model=users)
def readuser(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "created_at": user.created_at}

@router.delete("/{user_id}/delete",response_model=users)
def deleteUser(user_id:int,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"id": user.id, "email": user.email, "created_at": user.created_at}

@router.post("/login")
def loginn(log: login, db: Session=Depends(get_db)):
    
    email=log.email
    email=email.strip()
    
        #AND login.pasword==models.password_hash
    user=db.query(models.User).filter(email==models.User.email).first()
    if not user.id:
        raise HTTPException(status_code=404, detail="user not found")
    return {"id": user.id}
    