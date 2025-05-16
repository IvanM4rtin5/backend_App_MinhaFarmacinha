"""
API Routes
""" 

from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .medication import router as medication_router
from .inventory import router as inventory_router
from .shopping import router as shopping_router
from .notification import router as notification_router
from .chat import router as chat_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(medication_router)
router.include_router(inventory_router)
router.include_router(shopping_router)
router.include_router(notification_router)
router.include_router(chat_router)
