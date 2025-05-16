from app.db.base_class import Base
from sqlalchemy import inspect
from app.db.session import engine
from app.models import user  # Importa o modelo para registrar no Base

def init_db():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
