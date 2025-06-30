from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db, SessionLocal
from app.dependencies.auth import get_current_user, get_user_from_token
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate, 
    NotificationUpdate, 
    Notification, 
    NotificationResponse,
    NotificationStatus
)
from app.services.notification import NotificationService
from app.utils.websocket_manager import manager
import asyncio


router = APIRouter(prefix="/notification", tags=["notification"])

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    print("CHEGOU NO HANDLER! user_id:", user_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@router.post("/", response_model=Notification)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria uma nova notificação"""
    if notification_data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado a criar notificação para outro usuário")
    
    notification = NotificationService.create_notification(db, notification_data)

    notification_dict = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": str(notification.notification_type), 
        "status": str(notification.status),
        "scheduled_for": notification.scheduled_for.isoformat() if notification.scheduled_for else None,
        "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "medication_name": notification.medication.name if notification.medication else None
    }

    await manager.send_personal_message(
        {"type": "new_notification", "notification": notification_dict},
        notification.user_id
    )

    return notification

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[NotificationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista notificações do usuário"""
    notifications = NotificationService.get_user_notifications(
        db, current_user.id, skip, limit, status
    )
    
    result = []
    for notification in notifications:
        notification_dict = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "status": notification.status,
            "scheduled_for": notification.scheduled_for.isoformat() if notification.scheduled_for else None,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "medication_name": None
        }
        
        if notification.medication:
            notification_dict["medication_name"] = notification.medication.name
        
        result.append(NotificationResponse(**notification_dict))
    
    return result

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca uma notificação específica"""
    notification = NotificationService.get_notification(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    notification_dict = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "status": notification.status,
        "scheduled_for": notification.scheduled_for.isoformat() if notification.scheduled_for else None,
        "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "medication_name": notification.medication.name if notification.medication else None
    }
    
    return NotificationResponse(**notification_dict)

@router.put("/{notification_id}", response_model=Notification)
def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza uma notificação"""
    notification = NotificationService.update_notification(
        db, notification_id, current_user.id, notification_data
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return notification

@router.patch("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marca uma notificação como lida"""
    notification = NotificationService.mark_as_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return notification

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta uma notificação"""
    success = NotificationService.delete_notification(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return {"message": "Notificação deletada com sucesso"}

@router.get("/unread/count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Conta notificações não lidas"""
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}

@router.post("/medication-reminders")
def create_medication_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria lembretes de medicamentos baseados nos horários configurados"""
    notifications = NotificationService.create_medication_reminders(db, current_user.id)
    return {
        "message": f"Criados {len(notifications)} lembretes de medicamentos",
        "notifications_created": len(notifications)
    }

@router.post("/low-stock-alerts")
def create_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria alertas de estoque baixo"""
    notifications = NotificationService.create_low_stock_alerts(db, current_user.id)
    return {
        "message": f"Criados {len(notifications)} alertas de estoque baixo",
        "notifications_created": len(notifications)
    }

@router.post("/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marca todas as notificações do usuário como lidas"""
    notifications = NotificationService.get_user_notifications(
        db, current_user.id, status=NotificationStatus.SENT
    )
    
    count = 0
    for notification in notifications:
        if NotificationService.mark_as_read(db, notification.id, current_user.id):
            count += 1
    
    return {
        "message": f"Marcadas {count} notificações como lidas",
        "notifications_marked": count
    }

@router.get("/websocket/status")
def get_websocket_status():
    """Retorna status das conexões WebSocket"""
    return {
        "total_connections": manager.get_connection_count(),
        "active_users": len(manager.active_connections)
    } 