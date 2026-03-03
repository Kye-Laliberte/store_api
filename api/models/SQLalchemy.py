from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from  sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

#---------------------------
# Users
# ------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="user", uselist=False)

#-----------------------------
# Items
# ------------------------------
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    quantity_available = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __tableargs__=(
         CheckConstraint('price >= 0', name='price_non_negative'),
    )
    _tableargs__=(
         CheckConstraint('price >= 0', name='quantity_available_not_negative'),
    )

    # Relationships
    cart_items = relationship("CartItem", back_populates="item")
    purchase_items = relationship("PurchaseItem", back_populates="item")

#-------------------------
# Cart
# ------------------------
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="cart")
    cart_items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
#------------------------------
# CartItem (junction table)
# ------------------------------
class CartItem(Base):
    __tablename__ = "cart_items"

    cart_id = Column(Integer, ForeignKey("carts.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="cart_items")
    item = relationship("Item", back_populates="cart_items")
