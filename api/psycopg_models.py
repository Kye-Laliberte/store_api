from pydantic import BaseModel, validator, Field,  conint,confloat
from typing import Optional
from enum import Enum
from datetime import datetime

class item(BaseModel):
    id: int
    name: str
    description: Optional[str]="no description"
    quantity:int = conint(ge=0) 
    price: float = confloat(gt=0)
    
class Config:
        orm_mode = True

class createitem(BaseModel):
    name:str
    description: Optional[str]="no description"
    quantity:int = conint(ge=0) 
    price: float = confloat(gt=0)


class users(BaseModel):
    id: int
    email: str
    password_hash: Optional[str]="private infermaton"
    created_at: datetime


class userOut(BaseModel):
      email:str
      created_at: datetime


class carts(BaseModel):
    id:int
    user_id:int
    purchase_date: Optional[datetime]=datetime.now()


class createCart(BaseModel):
      user_id:int
      purchase_date: Optional[datetime]=datetime.now()

class cart_items(BaseModel):
    item_id:int
    quantity: int = conint(ge=0)


class CartItemsOut(BaseModel):
    item_id: int
    name: str
    price: float
    quantity: int = conint(ge=0)
    description: Optional[str]="no description"

    class Config:
        orm_mode = True


class create_cartItem(BaseModel):
    cart_id:int
    item_id:int
    quantity: int = conint(ge=0)
    

class purchase(BaseModel):
     item_id:int
     amout: Optional[int]=None
    #for changing if ther is to many of few items

class purchaseout(BaseModel):
    cart_id: int
    item_id: int
    name: str
    totalprice: float
    quantity: int    

