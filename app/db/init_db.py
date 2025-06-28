from app.db.base_class import Base
from app.db.session import engine
from app.models import user, medication, shopping, notification

def init_db():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
    
    
if __name__ == "__main__":
    init_db()