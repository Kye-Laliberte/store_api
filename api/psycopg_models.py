from pydantic import BaseModel, validator, Field
from typing import Optional, Annotated 
from enum import Enum
from datetime import datetime


class item(BaseModel):
    name: str
    description: str | None = "no description"
    quantity:int = Field(0, ge=0) 
    price: float = Field(...,gt=0)

class itemout(item):
    id: int
    class Config:
        from_attributes = True
    

class updateitem(BaseModel):
    description: str | None = None
    quantity: Optional[int] = Field(None,ge=0)
    price: Optional[float] = Field(None,gt=0)

class users(BaseModel):
    id: int
    email: str
    created_at: datetime

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class userOut(users):
    user_status: UserStatus 
    cart_id: Optional[int] = None
    class Config:
        from_attributes = True# allows pydantic to read data from SQLAlchemy models
    
class login(BaseModel):
    email: str
    password: str

class loginResponse(userOut):
    access_token: str
    token_type: str = "bearer"



class carts(BaseModel):
    user_id:int
    cart_date: Optional[datetime]=datetime.now()
    

class cartout(carts):
    id:int
    class Config:
        from_attributes = True


class cartitems(BaseModel):
    item_id: int
    name:str
    price:  float = Field(...,gt=0)
    quantity: int = Field(...,gt=0)
    description: Optional[str]="no description"
    

class CartItemsOut(cartitems):
    totalprice: float =Field(0,gt=0)
    class Config:
        from_attributes = True# allows pydantic to read data from SQLAlchemy models

class create_cartItem(BaseModel):
    item_id:int
    quantity: int = Field(...,ge=0)
    

