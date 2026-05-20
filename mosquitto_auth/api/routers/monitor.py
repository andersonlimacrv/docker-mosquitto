from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import asyncio
from mosquitto_auth.api.core.state import broker_state, metrics_dispatcher
from mosquitto_auth.api.models.monitor import BrokerStateResponse

router = APIRouter()
ws_router = APIRouter()

@router.get("/status", response_model=BrokerStateResponse)
def get_broker_status():
    """
    Retorna a saúde geral do broker, o estado do container, erros recentes
    e todas as métricas mapeadas da árvore $SYS/# do Mosquitto.
    """
    return broker_state.to_dict()

@ws_router.websocket("/metrics/stream")
async def metrics_ws(websocket: WebSocket):
    queue = metrics_dispatcher.subscribe()
    try:
        while True:
            metrics_dict = await queue.get()
            await websocket.send_json(metrics_dict)
    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        metrics_dispatcher.unsubscribe(queue)
