from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from datetime import datetime, timezone

from mosquitto_auth.api.services.mqtt_monitor import start_mqtt_monitor
from mosquitto_auth.api.core.state import broker_state, BrokerAvailability
from mosquitto_auth.api.core.config import settings

monitor_task = None
stale_detection_task = None

async def stale_detection_loop():
    """Detecta se o Mosquitto parou de publicar no $SYS mesmo estando conectado no socket TCP."""
    while True:
        try:
            if broker_state.broker_status == BrokerAvailability.ONLINE:
                if broker_state.last_sys_update_at:
                    delta = (datetime.now(timezone.utc) - broker_state.last_sys_update_at).total_seconds()
                    # Se não receber atualização em 2 * SYS_INTERVAL, considerar DEGRADED
                    if delta > (2 * settings.SYS_INTERVAL_ACL):
                        broker_state.broker_status = BrokerAvailability.DEGRADED
                        broker_state.last_error = f"Stale metrics: Última mensagem recebida há {int(delta)} segundos."
        except Exception:
            pass
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global monitor_task, stale_detection_task
    
    # Startup Events
    monitor_task = asyncio.create_task(start_mqtt_monitor())
    stale_detection_task = asyncio.create_task(stale_detection_loop())
    
    yield
    
    # Shutdown Events (Graceful)
    if stale_detection_task:
        stale_detection_task.cancel()
    if monitor_task:
        monitor_task.cancel()
        try:
            # Aguarda um pequeno momento para a task cancelar corretamente
            await asyncio.wait_for(monitor_task, timeout=2.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
