from pydantic import BaseModel, validator, Field
from typing import Optional, Annotated 
from enum import Enum
from datetime import datetime

class ItemSchema(BaseModel):
    id: int
    name: str
    description: str | None = "no description"
    quantity: int = Field(..., ge=0)
    price: float = Field(..., gt=0)
    class Config:
        from_attributes = True# allows pydantic to read data from SQLAlchemy models

class item(BaseModel):
    id: int
    name: str
    description: str | None = None
    quantity:int = Field(..., ge=0) 
    price: float = Field(...,gt=0)
    

class createitem(BaseModel):
    name:str
    description: str | None = "no description"
    quantity:int = Field(0,description="amout of items in stock",ge=0) 
    price: float = Field(...,gt=0)

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
class user_in(BaseModel):
     user_id: int 
     status: UserStatus
    
class login(BaseModel):
     #pasword:int
     email:str

class userinfo(BaseModel):
    id: int
    email: str
    password_hash: Optional[str]="private infermaton"
    created_at: datetime
    user_status:UserStatus

class userOut(BaseModel):
      email:str
      cart_id:Optional[int]=None
      id: int
      user_status:UserStatus 


class carts(BaseModel):
    id:int
    user_id:int
    cart_date: Optional[datetime]=datetime.now()
    class Config:
        from_attributes = True#

class createCart(BaseModel):
      user_id:int
      cart_date: Optional[datetime]=datetime.now()

class cart_items(BaseModel):
    item_id:int
    quantity: int = Field(...,gt=0)


class CartItemsOut(BaseModel):
    item_id: int
    name: str
    price: float = Field(...,gt=0)
    quantity: int = Field(...,gt=0)
    description: Optional[str]="no description"
    totalprice: float =Field(0,gt=0)
    class Config:
        from_attributes = True# allows pydantic to read data from SQLAlchemy models


class create_cartItem(BaseModel):
    item_id:int
    quantity: int = Field(...,ge=0)
    

class purchase(BaseModel):
     item_id:int
     amout: Optional[int]=None
    

class purchaseout(BaseModel):
    cart_id: int
    item_id: int
    name: str
    totalprice: float = Field(...,gt=0)
    quantity: int = Field(...,gt=0)  

