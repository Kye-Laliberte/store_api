from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from ..import sqlAmodels as models
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE a new user
@router.post("/")
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(password)
    user = models.User(email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "created_at": user.created_at}

# READ all users
@router.get("/getAll")
def read_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "email": u.email, "created_at": u.created_at} for u in users]

# READ user by ID
@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "created_at": user.created_at}