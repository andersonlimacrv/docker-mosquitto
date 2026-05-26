import asyncio
from datetime import datetime
from mosquitto_auth.api.models.monitor import BrokerAvailability, ContainerAvailability, BrokerMetrics

class Dispatcher:
    def __init__(self):
        self._queues: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=100)
        self._queues.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self._queues:
            self._queues.remove(queue)

    async def broadcast(self, data: dict):
        for queue in self._queues:
            try:
                queue.put_nowait(data)
            except asyncio.QueueFull:
                pass # Se o cliente não estiver lendo rápido o suficiente, ignora o tick para não travar o loop

class BrokerStateTracker:
    def __init__(self):
        self.broker_status: BrokerAvailability = BrokerAvailability.OFFLINE
        self.container_status: ContainerAvailability = ContainerAvailability.UNKNOWN
        self.last_error: str | None = None
        
        self.last_connected_at: datetime | None = None
        self.last_disconnect_at: datetime | None = None
        self.last_sys_update_at: datetime | None = None
        self.last_ws_broadcast_at: datetime | None = None
        
        self.metrics: BrokerMetrics = BrokerMetrics()
        
    def to_dict(self):
        return {
            "broker_status": self.broker_status.value,
            "container_status": self.container_status.value,
            "last_error": self.last_error,
            "last_connected_at": self.last_connected_at.isoformat() if self.last_connected_at else None,
            "last_disconnect_at": self.last_disconnect_at.isoformat() if self.last_disconnect_at else None,
            "last_sys_update_at": self.last_sys_update_at.isoformat() if self.last_sys_update_at else None,
            "last_ws_broadcast_at": self.last_ws_broadcast_at.isoformat() if self.last_ws_broadcast_at else None,
            "metrics": self.metrics.model_dump()
        }

# Global Singleton Instances
broker_state = BrokerStateTracker()
metrics_dispatcher = Dispatcher()

# Map Mosquitto $SYS topics to BrokerMetrics properties and casting functions
TOPIC_MAP = {
    "$SYS/broker/clients/connected": ("clients_connected", int),
    "$SYS/broker/clients/maximum": ("clients_maximum", int),
    "$SYS/broker/clients/total": ("clients_total", int),
    "$SYS/broker/messages/received": ("messages_received", int),
    "$SYS/broker/messages/sent": ("messages_sent", int),
    "$SYS/broker/bytes/received": ("bytes_received", int),
    "$SYS/broker/bytes/sent": ("bytes_sent", int),
    "$SYS/broker/uptime": ("uptime_seconds", int),
    "$SYS/broker/subscriptions/count": ("active_subscriptions", int),
    "$SYS/broker/retained messages/count": ("retained_messages", int),
    "$SYS/broker/load/messages/received/1min": ("messages_received_per_min", float),
    "$SYS/broker/load/messages/sent/1min": ("messages_sent_per_min", float),
    "$SYS/broker/load/publish/received/1min": ("publish_received_per_min", float),
    "$SYS/broker/load/publish/sent/1min": ("publish_sent_per_min", float),
    "$SYS/broker/load/bytes/received/1min": ("bytes_received_per_min", float),
    "$SYS/broker/load/bytes/sent/1min": ("bytes_sent_per_min", float),
    "$SYS/broker/load/sockets/1min": ("sockets_connected_per_min", float),
    "$SYS/broker/load/connections/1min": ("connections_per_min", float),
}
