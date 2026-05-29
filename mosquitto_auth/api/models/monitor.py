from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class BrokerAvailability(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"          # Conectado, mas métricas estão stale
    OFFLINE = "offline"            # Falha TCP/TLS ou auth
    RECONNECTING = "reconnecting"
    AWAITING_CERTS = "awaiting_certs"

class ContainerAvailability(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

class BrokerMetrics(BaseModel):
    version_mosquitto: str = Field(default="unknown", description="Software version of Mosquitto.")
    clients_connected: int = 0
    clients_disconnected: int = 0
    clients_expired: int = 0
    clients_maximum: int = 0
    clients_total: int = 0
    messages_received: int = 0
    messages_sent: int = 0
    bytes_received: int = 0
    bytes_sent: int = 0
    uptime_seconds: int = 0
    active_subscriptions: int = 0
    retained_messages: int = 0
    store_messages_bytes: int = 0
    heap_current_bytes: int = 0
    heap_max_bytes: int = 0
    packets_queue_pending: int = 0
    bytes_queue_pending: int = 0
    
    # 1min Load Metrics
    messages_received_per_min: float = 0.0
    messages_sent_per_min: float = 0.0
    publish_received_per_min: float = 0.0
    publish_sent_per_min: float = 0.0
    publish_dropped_per_min: float = 0.0
    bytes_received_per_min: float = 0.0
    bytes_sent_per_min: float = 0.0
    sockets_connected_per_min: float = 0.0
    connections_per_min: float = 0.0

class BrokerStateResponse(BaseModel):
    broker_status: BrokerAvailability
    container_status: ContainerAvailability
    last_error: str | None = None
    
    # Last seen tracking
    last_connected_at: datetime | None = None
    last_disconnect_at: datetime | None = None
    last_sys_update_at: datetime | None = None
    last_ws_broadcast_at: datetime | None = None
    
    metrics: BrokerMetrics
