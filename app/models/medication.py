from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    category = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    schedules = Column(ARRAY(String), nullable=False)
    stock = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    
    # Relacionamento com o usuário
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="medications")
