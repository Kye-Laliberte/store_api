from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from  sqlalchemy.orm import relationship
from api.database import Base
from datetime import datetime
from api.psycopg_models import UserStatus
from sqlalchemy import Enum



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(UserStatus),default=UserStatus.active,nullable=False)
    orders = relationship("Order", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="no description")
    quantity= Column(Integer, CheckConstraint('quantity_available  >= 0'), nullable=False, default=0,)
    price = Column(Numeric(10, 2),CheckConstraint('price > 0'), nullable=False)
    order_items = relationship("OrderItem", back_populates="item")
    cart_items = relationship("CartItem", back_populates="item")

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    cart_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart")
    cart_items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
   
class CartItem(Base):
    __tablename__ = "cart_items"
    cart_id = Column(Integer, ForeignKey("carts.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), nullable=False)
    
    item = relationship("Item") 
    cart = relationship("Cart", back_populates="cart_items")
    item = relationship("Item", back_populates="cart_items")
