
from pydantic import BaseModel, validator, Field,  conint,confloat
from typing import Optional
from enum import Enum
from datetime import datetime



class orders(BaseModel):
    id: int
    total_price: float = confloat(gt=0)
    user_id: int
    order_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    number_of_items: int = conint(gt=0)
class orderItems(BaseModel):
    id: int
    item_id: int
    quantity: int = conint(gt=0)
    price_at_order: float = confloat(gt=0)

class orderInfo(BaseModel):
    id: int
    order_date: datetime
    item_id: int
    quantity: int = conint(gt=0)
    price_at_order: float = confloat(gt=0)
    name: str
    description:str= Optional[str] == "no description"
