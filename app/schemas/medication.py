from pydantic import BaseModel, Field
from typing import List, Optional

class MedicationBase(BaseModel):
    name: str
    dosage: str
    category: str
    frequency: str
    schedules: List[str]
    stock: int = Field(ge=0)
    duration: Optional[int] = None
    notes: Optional[str] = None
    icon: Optional[str] = None

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(MedicationBase):
    pass

class Medication(MedicationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
