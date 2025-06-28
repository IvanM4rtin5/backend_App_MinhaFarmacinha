from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY, Text, DateTime,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dosage = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    schedules = Column(ARRAY(String), nullable=False)
    stock = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    pills_per_box = Column(Integer, nullable=False, default=1) 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="medications")
