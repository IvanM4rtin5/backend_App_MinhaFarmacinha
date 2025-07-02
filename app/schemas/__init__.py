"""
Pydantic Schemas
"""
from app.schemas.user import UserCreate, UserOut
from app.schemas.medication import Medication, MedicationCreate, MedicationUpdate
from app.schemas.notification import (
    Notification, 
    NotificationCreate, 
    NotificationUpdate, 
    NotificationResponse,
    NotificationType,
    NotificationStatus
)
from app.schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemOut 