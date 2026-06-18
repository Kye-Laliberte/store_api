from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
from passlib.context import CryptContext
from typing import List, Optional
from api.psycopg_models import users,userOut, login,user_in,userinfo
from passlib.hash import bcrypt
from api.services.cart_services import get_user, getcart, get_user_Email

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE a new user
@router.post("/addUser",response_model=users)
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
    return users( id= user.id, email= user.email, created_at= user.created_at)


@router.get("/{email}/RetrievebyEmail",response_model=users)
def getUser(email:str,db:Session=Depends(get_db)):
    """testing not a valid use of pasword retreval"""
    email=email.strip()
    user=get_user_Email(email=email,db=db)
    if  user is None:
        raise HTTPException(status_code=404,detail="Email not found")
    if user is False:
            raise HTTPException(status_code=203, detail="User not active")
    return users(id= user.id,email= user.email,created_at= user.created_at)


# READ all users
@router.get("/getAll",response_model=List[userinfo])
def getUsers(db: Session = Depends(get_db)):
    """retreves a list[] of all users and returns there email id and created_at"""
    out = db.query(models.User).all()
    return [userinfo(id= u.id, email= u.email, created_at= u.created_at,user_status=u.status) 
            for u in out]

# READ user by ID
@router.get("/{user_id}",response_model=userOut)
def readuser(user_id: int, db: Session = Depends(get_db)):
    """find a user by ther ID then returns there email id and created_at"""
    try:
        user=get_user(user_id=user_id,db=db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"error retreving user {e}")
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart=getcart(user_id=user.id,db=db)       
    if cart:
        return userOut(id= user.id, email= user.email, cart_id= cart.id, user_status=user.status)
    return userOut(id = user.id, email= user.email, user_status=user.status)
    

@router.put("/status",response_model=user_in)
def updateStatus(input:user_in,db:Session=Depends(get_db)):    
    user=db.query(models.User).filter(models.User.id==input.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status=input.status
    db.commit()
    db.refresh(user)
    return user_in(user_id=user.id,status=user.status)
    

@router.post("/login", response_model=userOut)
def loginn(log: login, db: Session=Depends(get_db)):
    """returns the user_Id, and email and cart_id if the user has one active"""
    try:
        user=get_user_Email(email=log.email,db=db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
        
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    if not user.status:
        raise HTTPException(status_code=400, detail=f"User is not curently active")
    cart=getcart(user_id=user.id,db=db)       
    if cart:
        return userOut(id= user.id, email= user.email, cart_id= cart.id, user_status=user.status)
    return userOut(id = user.id, email= user.email, user_status= user.status)
        
    
    