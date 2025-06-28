# app/schemas/shopping.py
from pydantic import BaseModel

class ShoppingItemBase(BaseModel):
    name: str

class ShoppingItemCreate(ShoppingItemBase):
    pass

class ShoppingItemUpdate(BaseModel):
    checked: bool

class ShoppingItemOut(ShoppingItemBase):
    id: int
    checked: bool

    class Config:
        from_attributes = True