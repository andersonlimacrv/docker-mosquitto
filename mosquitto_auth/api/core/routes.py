from mosquitto_auth.api.routers import user, ca, certificate, logs, health, monitor, config
from mosquitto_auth.api.core.dependencies import ApiKeyDep, AuthWsDep


def register_routes(app):
  app.include_router(user.router, prefix="/users", dependencies=[ApiKeyDep], tags=["Mosquitto Users 🦟"])
  app.include_router(certificate.router, prefix="/certificate", dependencies=[ApiKeyDep], tags=["Certificate 📑"])
  app.include_router(ca.router, prefix="/ca", dependencies=[ApiKeyDep], tags=["CA 📑"])
  app.include_router(logs.router, prefix="/logs", dependencies=[ApiKeyDep], tags=["Logs 📑"])
  app.include_router(logs.ws_router, prefix="/logs", dependencies=[AuthWsDep], tags=["Logs WebSocket"])
  app.include_router(health.router, prefix="/health", tags=["System Health 🩺"])
  app.include_router(config.router, prefix="/config", dependencies=[ApiKeyDep], tags=["Configurações ⚙️"])
  app.include_router(monitor.router, prefix="/monitor", dependencies=[ApiKeyDep], tags=["Broker Metrics 📊"])
  app.include_router(monitor.ws_router, prefix="/monitor", dependencies=[AuthWsDep], tags=["Broker Metrics WS"])