# app/models/shopping.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.base_class import Base

class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    checked = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)