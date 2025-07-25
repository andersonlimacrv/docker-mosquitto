from mosquitto_auth.api.routers import user
from mosquitto_auth.api.routers import certificate
from mosquitto_auth.api.core.dependencies import ApiKeyDep


def register_routes(app):
  app.include_router(user.router, prefix="/users", dependencies=[ApiKeyDep], tags=["Mosquitto Users 🦟"])
  app.include_router(certificate.router, prefix="/certificate", dependencies=[ApiKeyDep], tags=["Certificate 📑"])