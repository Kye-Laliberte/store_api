from pydantic import BaseModel, validator, Field,  conint,confloat
from typing import Optional
from enum import Enum
from datetime import datetime



class item(BaseModel):
    id: int
    name: str
    description: Optional[str]="no description"
    quantity:int = conint(ge=0) 
    price: float = confloat(ge=0)
class Config:
        orm_mode = True

class createitem(BaseModel):
    name:str
    description: Optional[str]="no description"
    quantity:int = conint(ge=0) 
    price: float = confloat(ge=0)


class users(BaseModel):
    id: int
    email: str
    password_hash: Optional[str]="private infermaton"
    created_at: datetime
class Config:
        orm_mode = True

class userOut(BaseModel):
      email:str
      created_at: datetime
class Config:
        orm_mode = True


class carts(BaseModel):
    id:int
    user_id:int
    purchase_date: Optional[datetime]=datetime.now()
class Config:
        orm_mode = True

class cart_items(BaseModel):
    item_id: int
    quantity: float = confloat(ge=0)
class Config:
        orm_mode = True





