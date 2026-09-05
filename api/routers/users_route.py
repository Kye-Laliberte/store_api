from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models.sqlAmodels as models
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from typing import List
from psycopg_models import users,userOut, login, loginResponse,userinfo
from services.cart_services import UserService, getcart,new_user
from core.security import create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE a new user
@router.post("/addUser",response_model=users, status_code=201)
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    """create a new user with a hashed pasword and email returning  user_id, email, created_at, hashed_password"""
    
    email=email.lower().strip()
    password=password.strip()

    user=new_user(email,password,db)
    
    return users( id= user.id, email= user.email, created_at= user.created_at)


@router.get("/{email}/RetrievebyEmail",response_model=users, status_code=200)
def getUser(email:str,db:Session=Depends(get_db)):
    """testing not a valid use of pasword retreval"""
    email=email.strip()
    user=UserService(db,email=email).user

    return users(id= user.id,email= user.email,created_at= user.created_at)


# this is a test route to get all users in the database, for testing purposes only
@router.get("/getAll",response_model=List[userinfo])
def getUsers(db: Session = Depends(get_db)):
    """retreves a list[] of all users and returns there email id and created_at"""
    out = db.query(models.User).all()
    return [userinfo(id= u.id, email= u.email, created_at= u.created_at,user_status=u.status) 
            for u in out]

# READ user by ID
@router.get("/{user_id}",response_model=userOut, status_code=200)
def readuser(user_id: int, db: Session = Depends(get_db)):
    """find a user by ther ID then returns there email id and created_at"""

    user=UserService(db,user_id=user_id).user
    cart=getcart(user_id=user.id,db=db)       

    if cart:
        return userOut(id= user.id, email= user.email, cart_id= cart.id, user_status=user.status)
    return userOut(id = user.id, email= user.email, user_status=user.status)
    

@router.put("/{user_id}/status",response_model=userOut, status_code=200)
def updateStatus(user_id:int,status:models.UserStatus,db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot change another user's status")
    
    user=UserService(db,user_id=user_id).user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.status=status
    db.commit()
    db.refresh(user)
    return userOut(id= user.id, email= user.email, user_status=user.status)
    
@router.post("/login", response_model=loginResponse, status_code=200)
def loginn(log: login, db: Session=Depends(get_db)):
    """Verify credentials and return a bearer token for the active user."""
    
    user=UserService(db,email=log.email).user
    
    try:
        password_matches = user is not None and pwd_context.verify(log.password, user.password_hash)
    except (UnknownHashError, ValueError):
        password_matches = False

    if not password_matches:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if user.status != models.UserStatus.active:
        raise HTTPException(status_code=403, detail="User is not active")
    
    cart=getcart(user_id=user.id,db=db)       
    return loginResponse(
        id=user.id,
        email=user.email,
        cart_id=cart.id if cart else None,
        user_status=user.status,
        access_token=create_access_token(user.id),
    )
        
    
    