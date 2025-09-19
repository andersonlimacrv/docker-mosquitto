import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mosquitto_auth.api.core.cors import setup_cors
from mosquitto_auth.api.core.routes import register_routes
from .core.config import settings

from mosquitto_auth.ca.generate_ca import create_initial_cert_paths


if not create_initial_cert_paths():
  print("Error creating initial certificate paths")
else:
  print(f"✅ Initial certificate paths already created: /{settings.certs_dir}")

app = FastAPI(
    title="Mosquitto Auth API",
    description="API for managing Mosquitto authentication users",
    version="1.0.0",
    default_response_class=JSONResponse
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
        reload=False,
        log_level=settings.log_level.lower(),
        workers=2
    )

if __name__ == "__main__":
    start()