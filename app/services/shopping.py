# app/services/shopping.py
from sqlalchemy.orm import Session
from app.models.shopping import ShoppingItem
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate

def create_shopping_item(db: Session, item: ShoppingItemCreate, user_id: int):
    db_item = ShoppingItem(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_shopping_list(db: Session, user_id: int):
    return db.query(ShoppingItem).filter(ShoppingItem.user_id == user_id).all()

def delete_shopping_item(db: Session, item_id: int, user_id: int):
    item = db.query(ShoppingItem).filter_by(id=item_id, user_id=user_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item

def update_shopping_item(db: Session, item_id: int, user_id: int, checked: bool):
    item = db.query(ShoppingItem).filter_by(id=item_id, user_id=user_id).first()
    if item:
        item.checked = checked
        db.commit()
        db.refresh(item)
    return item