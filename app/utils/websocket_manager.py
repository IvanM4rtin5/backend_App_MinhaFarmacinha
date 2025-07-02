"""
Gerenciador de WebSockets para notificações em tempo real
Sistema gratuito e eficiente para notificações
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Gerencia conexões WebSocket para notificações em tempo real
    """
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.all_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Conecta um usuário ao WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.all_connections.add(websocket)
        
        logger.info(f"Usuário {user_id} conectado. Total de conexões: {len(self.all_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Desconecta um usuário do WebSocket"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Remove lista vazia
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        if websocket in self.all_connections:
            self.all_connections.remove(websocket)
        
        logger.info(f"Usuário {user_id} desconectado. Total de conexões: {len(self.all_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Envia mensagem para um usuário específico"""
        if user_id in self.active_connections:
            disconnected_websockets = []
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Erro ao enviar mensagem para usuário {user_id}: {str(e)}")
                    disconnected_websockets.append(websocket)
            
            # Remove conexões que falharam
            for websocket in disconnected_websockets:
                self.disconnect(websocket, user_id)
    
    async def send_notification(self, user_id: int, notification_data: dict):
        """Envia notificação para um usuário específico"""
        message = {
            "type": "notification",
            "data": notification_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(message, user_id)
    
    async def send_medication_reminder(self, user_id: int, medication_name: str, dosage: str, time: str):
        """Envia lembrete de medicamento"""
        message = {
            "type": "medication_reminder",
            "data": {
                "medication_name": medication_name,
                "dosage": dosage,
                "time": time,
                "message": f"Horário de tomar {medication_name} - {dosage} às {time}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(message, user_id)
    
    async def send_low_stock_alert(self, user_id: int, medication_name: str, stock_count: int):
        """Envia alerta de estoque baixo"""
        message = {
            "type": "low_stock_alert",
            "data": {
                "medication_name": medication_name,
                "stock_count": stock_count,
                "message": f"O medicamento {medication_name} está com estoque baixo ({stock_count} unidades restantes)"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(message, user_id)
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os usuários conectados"""
        disconnected_websockets = []
        
        for websocket in self.all_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Erro ao enviar broadcast: {str(e)}")
                disconnected_websockets.append(websocket)
        
        for websocket in disconnected_websockets:
            for user_id, connections in self.active_connections.items():
                if websocket in connections:
                    self.disconnect(websocket, user_id)
                    break
    
    def get_connection_count(self) -> int:
        """Retorna o número total de conexões ativas"""
        return len(self.all_connections)
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Retorna o número de conexões de um usuário específico"""
        if user_id in self.active_connections:
            return len(self.active_connections[user_id])
        return 0

# Instância global do gerenciador
manager = ConnectionManager() 