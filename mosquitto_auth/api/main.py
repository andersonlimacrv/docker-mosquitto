import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mosquitto_auth.api.routers.user import router as user_router
from .config import settings

app = FastAPI(
    title="Mosquitto Auth API",
    description="API for managing Mosquitto authentication users",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["Mosquitto Users 🦟"])

@app.get("/", tags=["Root 🌱"])
async def root():
    return {
        "message": "Mosquitto Auth API",
        "version": "1.0.0",
        "docs": "/docs"
    }

def start():
    """
    Start the FastAPI application using Uvicorn.
    This function is intended to be called when running the application directly.
    """
    uvicorn.run(
        "mosquitto_auth.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )