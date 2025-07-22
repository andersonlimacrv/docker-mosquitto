from mosquitto_auth.api.routers import user
from mosquitto_auth.api.core.dependencies import ApiKeyDep


def register_routes(app):
  app.include_router(user.router, prefix="/users", dependencies=[ApiKeyDep], tags=["Mosquitto Users 🦟"])