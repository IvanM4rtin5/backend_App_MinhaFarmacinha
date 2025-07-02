import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.session import SessionLocal
from app.services.notification import NotificationService
from app.models.notification import NotificationStatus, Notification
from app.models.medication import Medication
from app.schemas.notification import NotificationCreate, NotificationType
from app.utils.websocket_manager import manager

logger = logging.getLogger(__name__)

class NotificationWorker:
    """
    Worker para processar notificações automaticamente
    Sistema interno com WebSockets para notificações em tempo real
    """
    
    def __init__(self):
        self.running = False
    
    def get_db(self) -> Session:
        """Obtém uma sessão do banco de dados"""
        db = SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise e
    
    async def process_pending_notifications(self):
        """Processa notificações pendentes"""
        db = self.get_db()
        try:
            pending_notifications = NotificationService.get_pending_notifications(db)
            
            for notification in pending_notifications:
                try:
                    # Marca como enviada no banco
                    success = NotificationService.mark_notification_as_sent(db, notification.id)
                    
                    if success:
                        # Envia via WebSocket se o usuário estiver conectado
                        notification_data = {
                            "id": notification.id,
                            "title": notification.title,
                            "message": notification.message,
                            "type": notification.notification_type.value,
                            "medication_id": notification.medication_id,
                            "created_at": notification.created_at.isoformat()
                        }
                        
                        await manager.send_notification(notification.user_id, notification_data)
                        logger.info(f"Notificação {notification.id} enviada via WebSocket: {notification.title}")
                    else:
                        logger.error(f"Erro ao processar notificação {notification.id}")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar notificação {notification.id}: {str(e)}")
                    # Marca como falha
                    notification.status = NotificationStatus.FAILED
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Erro ao processar notificações pendentes: {str(e)}")
        finally:
            db.close()
    
    async def check_medication_schedules(self):
        """Verifica horários de medicamentos e cria lembretes"""
        db = self.get_db()
        try:
            # Busca todos os medicamentos ativos
            medications = db.query(Medication).filter(Medication.stock > 0).all()
            
            current_time = datetime.utcnow()
            
            for medication in medications:
                # Verifica se já existe notificação para este horário hoje
                for schedule in medication.schedules:
                    # Verifica se já foi criada notificação para este horário hoje
                    existing_notification = db.query(Notification).filter(
                        and_(
                            Notification.medication_id == medication.id,
                            Notification.notification_type == NotificationType.MEDICATION_REMINDER,
                            Notification.created_at >= current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                        )
                    ).first()
                    
                    if not existing_notification:
                        # Cria nova notificação
                        notification_data = NotificationCreate(
                            title=f"Lembrete: {medication.name}",
                            message=f"Horário de tomar {medication.name} - {medication.dosage}mg às {schedule}",
                            notification_type=NotificationType.MEDICATION_REMINDER,
                            user_id=medication.user_id,
                            medication_id=medication.id,
                            scheduled_for=current_time + timedelta(minutes=5)  # 5 min no futuro
                        )
                        
                        notification = NotificationService.create_notification(db, notification_data)
                        
                        # Envia lembrete via WebSocket se o usuário estiver conectado
                        await manager.send_medication_reminder(
                            medication.user_id, 
                            medication.name, 
                            f"{medication.dosage}mg", 
                            schedule
                        )
                        
                        logger.info(f"Criado e enviado lembrete para {medication.name} às {schedule}")
                        
        except Exception as e:
            logger.error(f"Erro ao verificar horários de medicamentos: {str(e)}")
        finally:
            db.close()
    
    async def check_low_stock(self):
        """Verifica estoque baixo e cria alertas"""
        db = self.get_db()
        try:
            # Busca medicamentos com estoque baixo
            low_stock_medications = db.query(Medication).filter(Medication.stock <= 5).all()
            
            for medication in low_stock_medications:
                # Verifica se já existe alerta recente (últimas 24h)
                existing_alert = db.query(Notification).filter(
                    and_(
                        Notification.medication_id == medication.id,
                        Notification.notification_type == NotificationType.LOW_STOCK_ALERT,
                        Notification.created_at >= datetime.utcnow() - timedelta(days=1)
                    )
                ).first()
                
                if not existing_alert:
                    notification_data = NotificationCreate(
                        title=f"Estoque Baixo: {medication.name}",
                        message=f"O medicamento {medication.name} está com estoque baixo ({medication.stock} unidades restantes). Considere fazer reposição.",
                        notification_type=NotificationType.LOW_STOCK_ALERT,
                        user_id=medication.user_id,
                        medication_id=medication.id
                    )
                    
                    notification = NotificationService.create_notification(db, notification_data)
                    
                    # Envia alerta via WebSocket se o usuário estiver conectado
                    await manager.send_low_stock_alert(
                        medication.user_id, 
                        medication.name, 
                        medication.stock
                    )
                    
                    logger.info(f"Criado e enviado alerta de estoque baixo para {medication.name}")
                    
        except Exception as e:
            logger.error(f"Erro ao verificar estoque baixo: {str(e)}")
        finally:
            db.close()
    
    async def run_worker(self, interval_seconds: int = 60):
        """Executa o worker em loop"""
        self.running = True
        logger.info("Notification Worker iniciado (com WebSockets)")
        
        while self.running:
            try:
                # Processa notificações pendentes
                await self.process_pending_notifications()
                
                # Verifica horários de medicamentos (a cada 5 minutos)
                if datetime.utcnow().minute % 5 == 0:
                    await self.check_medication_schedules()
                
                # Verifica estoque baixo (a cada hora)
                if datetime.utcnow().minute == 0:
                    await self.check_low_stock()
                
                # Aguarda próximo ciclo
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Erro no worker: {str(e)}")
                await asyncio.sleep(interval_seconds)
    
    def stop_worker(self):
        """Para o worker"""
        self.running = False
        logger.info("Notification Worker parado")

# Instância global do worker
notification_worker = NotificationWorker()

def start_notification_worker():
    """Função para iniciar o worker"""
    asyncio.run(notification_worker.run_worker())

def stop_notification_worker():
    """Função para parar o worker"""
    notification_worker.stop_worker() 