from pydantic import BaseModel, validator, Field,  conint,confloat
from typing import Optional
from enum import Enum
from datetime import datetime



class orders(BaseModel):
    id: int
    total_price: float = Field(gt=0)
    user_id: int
    created_at: datetime

class orderItems(BaseModel):
    order_id: int
    item_id: int
    quantity: int = Field(gt=0)
    price_at_order: float = Field(gt=0)