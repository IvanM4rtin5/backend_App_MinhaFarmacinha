from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.medication import Medication
from app.schemas.notification import NotificationCreate, NotificationUpdate
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    
    @staticmethod
    def create_notification(db: Session, notification_data: NotificationCreate) -> Notification:
        """Cria uma nova notificação"""
        db_notification = Notification(
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
            user_id=notification_data.user_id,
            medication_id=notification_data.medication_id,
            scheduled_for=notification_data.scheduled_for,
            medication_name=notification_data.medication_name,
            medication_dosage=notification_data.medication_dosage
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    
    @staticmethod
    def get_user_notifications(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[NotificationStatus] = None
    ) -> List[Notification]:
        """Busca notificações de um usuário"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if status:
            query = query.filter(Notification.status == status)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_notification(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        """Busca uma notificação específica do usuário"""
        return db.query(Notification).filter(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        ).first()
    
    @staticmethod
    def update_notification(
        db: Session, 
        notification_id: int, 
        user_id: int, 
        notification_data: NotificationUpdate
    ) -> Optional[Notification]:
        """Atualiza uma notificação"""
        notification = NotificationService.get_notification(db, notification_id, user_id)
        if not notification:
            return None
        
        update_data = notification_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notification, field, value)
        
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        """Marca uma notificação como lida"""
        notification = NotificationService.get_notification(db, notification_id, user_id)
        if not notification:
            return None
        
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
        """Deleta uma notificação"""
        notification = NotificationService.get_notification(db, notification_id, user_id)
        if not notification:
            return False
        
        db.delete(notification)
        db.commit()
        return True
    
    @staticmethod
    def get_pending_notifications(db: Session) -> List[Notification]:
        """Busca notificações pendentes para envio"""
        return db.query(Notification).filter(
            and_(
                Notification.status == NotificationStatus.PENDING,
                or_(
                    Notification.scheduled_for.is_(None),
                    Notification.scheduled_for <= datetime.utcnow()
                )
            )
        ).all()
    
    @staticmethod
    def create_medication_reminders(db: Session, user_id: int) -> List[Notification]:
        """Cria lembretes de medicamentos baseados nos horários configurados"""
        medications = db.query(Medication).filter(Medication.user_id == user_id).all()
        notifications = []
        
        for medication in medications:
            if medication.stock <= 0:
                continue
            
            print(f"CRIANDO NOTIFICAÇÃO: {medication.name} para user {user_id}")
            notification = NotificationService.create_notification(
                db=db,
                notification_data=NotificationCreate(
                    title=f"Lembrete: {medication.name}",
                    message=f"Horário de tomar {medication.name} - {medication.dosage}mg ({medication.frequency})",
                    notification_type=NotificationType.MEDICATION_REMINDER,
                    user_id=user_id,
                    medication_id=medication.id,
                    medication_name=medication.name,
                    medication_dosage=str(medication.dosage),
                    scheduled_for=datetime.utcnow() + timedelta(minutes=30) 
                )
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def create_low_stock_alerts(db: Session, user_id: int) -> List[Notification]:
        """Cria alertas de estoque baixo"""
        medications = db.query(Medication).filter(
            and_(
                Medication.user_id == user_id,
                Medication.stock <= 7
            )
        ).all()
        
        notifications = []
        for medication in medications:
            print(f"CRIANDO NOTIFICAÇÃO: {medication.name} para user {user_id}")
            notification = NotificationService.create_notification(
                db=db,
                notification_data=NotificationCreate(
                    title=f"Estoque Baixo: {medication.name}",
                    message=f"O medicamento {medication.name} está com estoque baixo ({medication.stock} unidades restantes). Considere fazer reposição.",
                    notification_type=NotificationType.LOW_STOCK_ALERT,
                    user_id=user_id,
                    medication_id=medication.id,
                    medication_name=medication.name,
                    medication_dosage=str(medication.dosage)
                )
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def mark_notification_as_sent(db: Session, notification_id: int) -> bool:
        """Marca uma notificação como enviada"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            return False
        
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Conta notificações não lidas do usuário"""
        return db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.status != NotificationStatus.READ
            )
        ).count() 