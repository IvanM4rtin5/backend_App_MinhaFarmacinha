from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate, Medication as MedicationSchema
from app.api.auth import get_current_user
from app.models.user import User
from app.services.medication import (
    create_medication, get_medications, get_medication, 
    update_medication, delete_medication, get_low_stock_medications,
    get_expired_medications, auto_remove_empty_medications
)

router = APIRouter(prefix="/medication", tags=["medication"])

@router.post("/", response_model=MedicationSchema)
def create_medication_endpoint(
    medication: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria um novo medicamento."""
    db_medication = create_medication(db, medication, current_user.id)
    if db_medication is None:
        raise HTTPException(status_code=409, detail="Já existe um medicamento com este nome e dosagem para o usuário.")
    from app.services.medication import calculate_days_until_empty, is_low_stock
    days_until_empty = calculate_days_until_empty(
        db_medication.frequency, 
        db_medication.stock, 
        db_medication.pills_per_box
    )
    db_medication.days_until_empty = days_until_empty
    db_medication.is_low_stock = is_low_stock(
        db_medication.stock, 
        db_medication.pills_per_box, 
        days_until_empty or 0
    )
    
    return db_medication

@router.get("/", response_model=List[MedicationSchema])
def get_medications_endpoint(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista medicamentos do usuário com cálculos de estoque."""
    return get_medications(db, current_user.id, skip, limit, search, category)

@router.get("/{medication_id}", response_model=MedicationSchema)
def get_medication_endpoint(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca um medicamento específico."""
    medication = get_medication(db, medication_id, current_user.id)
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    return medication

@router.put("/{medication_id}", response_model=MedicationSchema)
def update_medication_endpoint(
    medication_id: int,
    medication: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza um medicamento."""
    db_medication = update_medication(db, medication_id, medication, current_user.id)
    
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    return db_medication

@router.delete("/{medication_id}")
def delete_medication_endpoint(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove um medicamento."""
    success = delete_medication(db, medication_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    return {"message": "Medicamento excluído com sucesso"}

@router.get("/low-stock/", response_model=List[MedicationSchema])
def get_low_stock_medications_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista medicamentos com estoque baixo."""
    return get_low_stock_medications(db, current_user.id)

@router.get("/expired/", response_model=List[MedicationSchema])
def get_expired_medications_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista medicamentos que acabaram (estoque = 0)."""
    return get_expired_medications(db, current_user.id)

@router.post("/cleanup/empty", response_model=dict)
def cleanup_empty_medications_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove automaticamente medicamentos com estoque zero."""
    removed_count = auto_remove_empty_medications(db, current_user.id)
    
    return {
        "message": f"{removed_count} medicamento(s) removido(s) automaticamente",
        "removed_count": removed_count
    }

@router.patch("/{medication_id}/stock", response_model=MedicationSchema)
def update_medication_stock(
    medication_id: int,
    new_stock: int = Query(..., ge=0, description="Nova quantidade em estoque"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza apenas o estoque de um medicamento."""
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    medication.stock = new_stock
    db.commit()
    db.refresh(medication)
    
    from app.services.medication import calculate_days_until_empty, is_low_stock
    days_until_empty = calculate_days_until_empty(
        medication.frequency, 
        medication.stock, 
        medication.pills_per_box
    )
    medication.days_until_empty = days_until_empty
    medication.is_low_stock = is_low_stock(
        medication.stock, 
        medication.pills_per_box, 
        days_until_empty or 0
    )
    
    return medication

@router.post("/{medication_id}/consume", response_model=MedicationSchema)
def consume_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simula o consumo de um medicamento baseado na frequência.
    Diminui o estoque automaticamente.
    """
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == current_user.id
    ).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    if medication.stock <= 0:
        raise HTTPException(status_code=400, detail="Medicamento sem estoque")
    
    import re
    match = re.search(r'(\d+)x', medication.frequency.lower())
    if not match:
        raise HTTPException(status_code=400, detail="Frequência inválida")
    
    times_per_day = int(match.group(1))
    pills_to_consume = times_per_day
    
    medication.stock = max(0, medication.stock - pills_to_consume)
    db.commit()
    db.refresh(medication)
    
    from app.services.medication import calculate_days_until_empty, is_low_stock
    days_until_empty = calculate_days_until_empty(
        medication.frequency, 
        medication.stock, 
        medication.pills_per_box
    )
    medication.days_until_empty = days_until_empty
    medication.is_low_stock = is_low_stock(
        medication.stock, 
        medication.pills_per_box, 
        days_until_empty or 0
    )
    
    return medication

@router.post("/daily-consumption", response_model=dict)
def daily_medication_consumption(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simula o consumo diário de todos os medicamentos do usuário.
    Seria chamado automaticamente pelo frontend uma vez por dia.
    """
    medications = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.stock > 0
    ).all()
    
    consumed_medications = []
    empty_medications = []
    
    for medication in medications:
        import re
        match = re.search(r'(\d+)x', medication.frequency.lower())
        if match:
            times_per_day = int(match.group(1))
            pills_to_consume = times_per_day
            
            old_stock = medication.stock
            medication.stock = max(0, medication.stock - pills_to_consume)
            
            consumed_medications.append({
                "id": medication.id,
                "name": medication.name,
                "old_stock": old_stock,
                "new_stock": medication.stock,
                "consumed": min(pills_to_consume, old_stock)
            })
            
            if medication.stock == 0:
                empty_medications.append(medication.name)
    
    db.commit()
    
    return {
        "message": "Consumo diário processado",
        "consumed_medications": consumed_medications,
        "empty_medications": empty_medications,
        "total_medications_processed": len(medications)
    } 