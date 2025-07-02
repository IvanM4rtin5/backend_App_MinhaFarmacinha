from sqlalchemy.orm import Session
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate
from typing import List, Optional
import re
from datetime import datetime, timedelta

def calculate_days_until_empty(frequency: str, stock: int, pills_per_box: int) -> Optional[int]:
    """
    Calcula quantos dias o medicamento vai durar baseado na frequência de uso.
    
    Args:
        frequency: Frequência de uso (ex: "1x ao dia", "2x ao dia", "3x ao dia")
        stock: Quantidade atual em estoque
        pills_per_box: Quantidade de comprimidos por caixa
    
    Returns:
        Número de dias até o medicamento acabar, ou None se não for possível calcular
    """

    match = re.search(r'(\d+)x', frequency.lower())
    if not match:
        return None
    
    times_per_day = int(match.group(1))
    
    pills_per_day = times_per_day
    
    if stock <= 0:
        return 0
    
    days_until_empty = stock // pills_per_day
    
    return days_until_empty

def is_low_stock(stock: int, pills_per_box: int, days_until_empty: int) -> bool:
    """
    Determina se o medicamento está com estoque baixo.
    
    Args:
        stock: Quantidade atual em estoque
        pills_per_box: Quantidade de comprimidos por caixa
        days_until_empty: Dias até o medicamento acabar
    
    Returns:
        True se o estoque está baixo (menos de 7 dias ou menos de 1 caixa)
    """
    return days_until_empty <= 7 or stock <= pills_per_box

def create_medication(db: Session, medication: MedicationCreate, user_id: int) -> Medication:
    """Cria um novo medicamento, impedindo duplicidade de nome e dosagem para o mesmo usuário."""
    # Check if it already exists
    existing = db.query(Medication).filter(
        Medication.user_id == user_id,
        Medication.name.ilike(medication.name),
        Medication.dosage == medication.dosage
    ).first()
    if existing:
        return None
    db_medication = Medication(**medication.model_dump(), user_id=user_id)
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication

def get_medications(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None
) -> List[Medication]:
    """Busca medicamentos do usuário com cálculos de estoque."""
    query = db.query(Medication).filter(Medication.user_id == user_id)
    
    if search:
        query = query.filter(Medication.name.ilike(f"%{search}%"))
    
    if category:
        query = query.filter(Medication.category == category)
    
    medications = query.offset(skip).limit(limit).all()

    for medication in medications:
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
    
    return medications

def get_medication(db: Session, medication_id: int, user_id: int) -> Optional[Medication]:
    """Busca um medicamento específico com cálculos de estoque."""
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == user_id
    ).first()
    
    if medication:
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

def update_medication(
    db: Session, 
    medication_id: int, 
    medication: MedicationUpdate, 
    user_id: int
) -> Optional[Medication]:
    """Atualiza um medicamento."""
    db_medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == user_id
    ).first()
    
    if not db_medication:
        return None
    
    for key, value in medication.model_dump().items():
        setattr(db_medication, key, value)
    
    db.commit()
    db.refresh(db_medication)
    
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

def delete_medication(db: Session, medication_id: int, user_id: int) -> bool:
    """Remove um medicamento."""
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == user_id
    ).first()
    
    if not medication:
        return False
    
    db.delete(medication)
    db.commit()
    return True

def get_low_stock_medications(db: Session, user_id: int) -> List[Medication]:
    """Busca medicamentos com estoque baixo."""
    medications = get_medications(db, user_id, limit=1000) 
    return [med for med in medications if med.is_low_stock]

def get_expired_medications(db: Session, user_id: int) -> List[Medication]:
    """Busca medicamentos que acabaram (estoque = 0)."""
    medications = get_medications(db, user_id, limit=1000)
    return [med for med in medications if med.stock <= 0]

def auto_remove_empty_medications(db: Session, user_id: int) -> int:
    """
    Remove automaticamente medicamentos com estoque zero.
    Retorna o número de medicamentos removidos.
    """
    empty_medications = db.query(Medication).filter(
        Medication.user_id == user_id,
        Medication.stock <= 0
    ).all()
    
    count = len(empty_medications)
    for medication in empty_medications:
        db.delete(medication)
    
    db.commit()
    return count 