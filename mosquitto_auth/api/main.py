import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mosquitto_auth.api.routers.user import router as user_router
from .config import settings

app = FastAPI(
    title="Mosquitto Auth API",
    description="API para gerenciamento de usuários e certificados do Mosquitto MQTT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["Users"])

@app.get("/")
async def root():
    return {
        "message": "Mosquitto Auth API",
        "version": "1.0.0",
        "docs": "/docs"
    }

def start():
    """
    Função para iniciar o servidor da API
    """
    uvicorn.run(
        "mosquitto_auth.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )