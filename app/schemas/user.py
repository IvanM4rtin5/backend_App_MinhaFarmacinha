from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    birth_date: date | None = None 

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    birth_date: date | None = None

    class Config:
        from_attributes = True
