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
    """create a new user with a hashed pasword and email returning  user_id, email, created_at, hashed_password"""
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
    """testing not a valid use of pasword retreval"""
    email=email.strip().lower()
    user=db.query(models.User).filter(models.User.email==email).first()
    if not user:
        raise HTTPException(status_code=404,detail="Email not found")
    return {"id": user.id,"email": user.email,"created_at": user.created_at}


# READ all users
@router.get("/getAll",response_model=List[users])
def getUsers(db: Session = Depends(get_db)):
    """retreves a list[] of all users and returns there email id and created_at"""
    users = db.query(models.User).all()
    return [{"id": u.id, "email": u.email, "created_at": u.created_at} for u in users]

# READ user by ID
@router.get("/{user_id}",response_model=users)
def readuser(user_id: int, db: Session = Depends(get_db)):
    """find a user by ther ID then returns there email id and created_at"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "email": user.email, "created_at": user.created_at}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"error retreving user {e}")

@router.delete("/{user_id}/delete",response_model=users)
def deleteUser(user_id:int,db:Session=Depends(get_db)):
    """deletes a user if they do not have a active cart"""
    try:
         
        user=db.query(models.User).filter(models.User.id==user_id, ).first()
    
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"id": user.id, "email": user.email, "created_at": user.created_at}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cart still active or f{e}")
    
@router.post("/login", response_model=userOut)
def loginn(log: login, db: Session=Depends(get_db)):
    """returns the user_Id"""
    try:
        email=log.email
        email=email.strip()
        #AND login.pasword==models.password_hash
        user=db.query(models.User).filter(email==models.User.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
    
        cart=db.query(models.Cart).filter(user.id==models.Cart).first()
       
        if cart:
            return {"id": user.id, "email": user.email, "cart_id": cart.id}
        return {"id": user.id, "email": user.email}
        
        return {"id": user.id, "email": user.email, "created_at": user.created_at}
        
    except Exception as e:
        HTTPException(status_code=400, detail=f"{e}")