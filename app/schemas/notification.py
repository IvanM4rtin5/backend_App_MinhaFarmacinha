from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    MEDICATION_REMINDER = "MEDICATION_REMINDER"
    LOW_STOCK_ALERT = "LOW_STOCK_ALERT"
    MEDICATION_EXPIRY = "MEDICATION_EXPIRY"
    REFILL_REMINDER = "REFILL_REMINDER"
    GENERAL = "GENERAL"

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    READ = "READ"
    FAILED = "FAILED"

class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType
    scheduled_for: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    user_id: int
    medication_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[NotificationStatus] = None
    scheduled_for: Optional[datetime] = None

class Notification(NotificationBase):
    id: int
    user_id: int
    medication_id: Optional[int] = None
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: NotificationType
    status: NotificationStatus
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    medication_name: Optional[str] = None

    class Config:
        from_attributes = True 