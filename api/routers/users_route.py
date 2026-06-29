from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
import api.models.sqlAmodels as models
from passlib.context import CryptContext
from typing import List, Optional
from api.psycopg_models import users,userOut, login,user_in,userinfo
from passlib.hash import bcrypt
from api.services.cart_services import get_user, getcart, get_user_Email,new_user

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE a new user
@router.post("/addUser",response_model=users)
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    """create a new user with a hashed pasword and email returning  user_id, email, created_at, hashed_password"""
    
    email=email.lower().strip()
    password=password.strip()

    user=new_user(email,password,db)
    
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
    

@router.put("{user_id}/status",response_model=user_in)
def updateStatus(user_id:int,status:models.UserStatus,db:Session=Depends(get_db)):    
    
    user=get_user(user_id,db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.status=status
    db.commit()
    db.refresh(user)
    return user_in(user_id=user.id,status=user.status)
    
@router.post("/login", response_model=userOut)
def loginn(log: login, db: Session=Depends(get_db)):
    """returns the user_Id, and email and cart_id if the user has one active"""
    
    user=get_user_Email(email=log.email,db=db)
    
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    if user is False:
        raise HTTPException(status_code=400, detail="user is not active")
    
    cart=getcart(user_id=user.id,db=db)       
    if cart:
        return userOut(id= user.id, email= user.email, cart_id= cart.id, user_status=user.status)
    return userOut(id = user.id, email= user.email, user_status= user.status)
        
    
    