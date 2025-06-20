from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import verify_password, create_access_token, get_password_hash as hash_password
from app.core.security import jwt
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    try:
        # Remove the prefix "Bearer " of token
        token = authorization.replace("Bearer ", "")
        
        # Decodify the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
            
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
            )
            
        return user
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    email = user_in.email.strip().lower()
    username = user_in.username.strip().lower()
    print("Recebido:", email, username)
    user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if user:
        raise HTTPException(status_code=400, detail="Usuário ou email já existe.")

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(user_in.password),
        birth_date=user_in.birth_date
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Usuário ou email já existe.")
    return new_user

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
