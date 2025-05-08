from fastapi import FastAPI
from mosquitto_auth.api.create_user import router as user_router
from mosquitto_auth.api.deploy import router as deploy_router

app = FastAPI(title="Mosquitto Admin API")

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(deploy_router, prefix="/webhook", tags=["Deploy"])
