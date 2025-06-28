from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemOut, ShoppingItemUpdate
from app.services.shopping import (
    create_shopping_item, get_shopping_list, delete_shopping_item, update_shopping_item
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/shopping", tags=["shopping"])

@router.post("/", response_model=ShoppingItemOut)
def add_item(
    item: ShoppingItemCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return create_shopping_item(db, item, user.id)

@router.get("/", response_model=list[ShoppingItemOut])
def list_items(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_shopping_list(db, user.id)

@router.delete("/{item_id}", response_model=ShoppingItemOut)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = delete_shopping_item(db, item_id, user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@router.patch("/{item_id}", response_model=ShoppingItemOut)
def check_item(
    item_id: int,
    update: ShoppingItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = update_shopping_item(db, item_id, user.id, update.checked)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item