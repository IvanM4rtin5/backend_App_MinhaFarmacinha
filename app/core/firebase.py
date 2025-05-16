import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings

# Inicializa o Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

def verify_firebase_token(token: str) -> dict:
    """
    Verifica o token do Firebase e retorna as informações do usuário
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Token inválido: {str(e)}") 