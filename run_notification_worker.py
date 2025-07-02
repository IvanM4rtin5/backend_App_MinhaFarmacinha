#!/usr/bin/env python3
"""
Script para executar o worker de notificações em background
"""

import asyncio
import logging
import signal
import sys
from app.utils.notification_worker import start_notification_worker, stop_notification_worker

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification_worker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handler para sinais de interrupção"""
    logger.info("Recebido sinal de interrupção. Parando worker...")
    stop_notification_worker()
    sys.exit(0)

def main():
    """Função principal"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Iniciando Notification Worker...")
    
    try:
        # Inicia o worker
        start_notification_worker()
    except KeyboardInterrupt:
        logger.info("Worker interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no worker: {str(e)}")
    finally:
        stop_notification_worker()
        logger.info("Notification Worker finalizado")

if __name__ == "__main__":
    main() 