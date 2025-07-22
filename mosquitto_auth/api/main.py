import uvicorn
from fastapi import FastAPI
from mosquitto_auth.api.core.cors import setup_cors
from mosquitto_auth.api.core.routes import register_routes
from .core.config import settings

app = FastAPI(
    title="Mosquitto Auth API",
    description="API for managing Mosquitto authentication users",
    version="1.0.0",
)

setup_cors(app)
register_routes(app)


@app.get("/", tags=["Root 🌱"])
async def root():
    return {
        "message": "Mosquitto Auth API",
        "docs": f"http://localhost:{settings.API_PORT}/docs"
    }

def start():
    uvicorn.run(
        "mosquitto_auth.api.main:app",
        host=settings.api_host,
        port=settings.API_PORT,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    start()