from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    
    # Relacionamento com medicamentos
    medications = relationship("Medication", back_populates="user")
