from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate, Medication as MedicationSchema
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/medication", tags=["medication"])

@router.post("/", response_model=MedicationSchema)
def create_medication(
    medication: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_medication = Medication(**medication.model_dump(), user_id=current_user.id)
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication

@router.get("/", response_model=List[MedicationSchema])
def get_medications(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Medication).filter(Medication.user_id == current_user.id)
    
    if search:
        query = query.filter(Medication.name.ilike(f"%{search}%"))
    
    if category:
        query = query.filter(Medication.category == category)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{medication_id}", response_model=MedicationSchema)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    return medication

@router.put("/{medication_id}", response_model=MedicationSchema)
def update_medication(
    medication_id: int,
    medication: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    for key, value in medication.model_dump().items():
        setattr(db_medication, key, value)
    
    db.commit()
    db.refresh(db_medication)
    return db_medication

@router.delete("/{medication_id}")
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    db.delete(medication)
    db.commit()
    
    return {"message": "Medicamento excluído com sucesso"} 