from symtable import Class

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from  sqlalchemy.orm import relationship, declarative_base,sessionmaker
from api.database import Base
from datetime import datetime
__table_args__ = (
    CheckConstraint('quantity > 0'),
    CheckConstraint('price > 0'),
    CheckConstraint('quantity_available >= 0'))
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("Cart", back_populates="user", uselist=False)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    quantity= Column(Integer, CheckConstraint('quantity_available  >= 0'), nullable=False, default=0,)
    price = Column(Numeric(10, 2),CheckConstraint('price > 0'), nullable=False)
   
    cart_items = relationship("CartItem", back_populates="item")

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart")
    cart_items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"
    cart_id = Column(Integer, ForeignKey("carts.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    
    item = relationship("Item") 
    cart = relationship("Cart", back_populates="cart_items")
    item = relationship("Item", back_populates="cart_items")
