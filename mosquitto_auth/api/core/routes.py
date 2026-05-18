from mosquitto_auth.api.routers import user, ca, certificate, logs
from mosquitto_auth.api.core.dependencies import ApiKeyDep


def register_routes(app):
  app.include_router(user.router, prefix="/users", dependencies=[ApiKeyDep], tags=["Mosquitto Users 🦟"])
  app.include_router(certificate.router, prefix="/certificate", dependencies=[ApiKeyDep], tags=["Certificate 📑"])
  app.include_router(ca.router, prefix="/ca", dependencies=[ApiKeyDep], tags=["CA 📑"])
  app.include_router(logs.router, prefix="/logs", dependencies=[ApiKeyDep], tags=["Logs 📑"])