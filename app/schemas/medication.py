from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MedicationBase(BaseModel):
    name: str
    dosage: float
    category: str
    frequency: str
    schedules: List[str]
    stock: int = Field(ge=0)
    duration: Optional[int] = None
    notes: Optional[str] = None
    pills_per_box: int = Field(gt=0, description="Quantidade de comprimidos por caixa")

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(MedicationBase):
    pass

class Medication(MedicationBase):
    id: int
    user_id: int
    created_at: datetime
    days_until_empty: Optional[int] = None 
    is_low_stock: Optional[bool] = None 

    class Config:
        from_attributes = True
