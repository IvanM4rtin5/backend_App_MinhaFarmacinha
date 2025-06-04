from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return { "Bem-vindo à API da Minha Farmacinha. Por Ivan Martins"} 