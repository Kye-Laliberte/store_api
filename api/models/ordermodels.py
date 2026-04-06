from symtable import Class

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from  sqlalchemy.orm import relationship, declarative_base,sessionmaker
from api.database import Base
from datetime import datetime 



    
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    total_price = Column(Numeric(10, 2), CheckConstraint('total_price >= 0'), nullable=False)
    user_id =Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint('quantity > 0'),
        CheckConstraint('price_at_order > 0'),
    )
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Numeric(10, 2), nullable=False) 

    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")