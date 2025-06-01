from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{identifier}", response_model=UserOut)
async def get_user(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tentar buscar por ID primeiro
    try:
        user_id = int(identifier)
        user = db.query(User).filter(User.id == user_id).first()
    except ValueError:

        user = db.query(User).filter(User.username == identifier).first()
      
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado a acessar dados de outro usuário")
    
    return user
