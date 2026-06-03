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
                pass

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
            "last_connected_at": self.last_connected_at,
            "last_disconnect_at": self.last_disconnect_at,
            "last_sys_update_at": self.last_sys_update_at,
            "last_ws_broadcast_at": self.last_ws_broadcast_at,
            "metrics": self.metrics.model_dump()
        }

broker_state = BrokerStateTracker()
metrics_dispatcher = Dispatcher()

TOPIC_MAP = {
    "$SYS/broker/version": ("version_mosquitto", str), # (( STRING )) - Versão do software do Mosquitto. (Tópico estático, enviado apenas na inscrição.)
    "$SYS/broker/clients/connected": ("clients_connected", int), #  (( CLIENTS )) - Número de clientes atualmente conectados.
    "$SYS/broker/clients/expired": ("clients_expired", int), #  (( CLIENTS )) - Clientes persistentes desconectados que foram expirados/removidos (pela opção persistent_client_expiration).
    "$SYS/broker/clients/disconnected": ("clients_disconnected", int), #  (( CLIENTS )) - Clientes persistentes (sessões duráveis) registrados, mas atualmente desconectados.
    "$SYS/broker/clients/maximum": ("clients_maximum", int), # (( CLIENTS )) - Máximo de clientes conectados simultaneamente observado.
    "$SYS/broker/clients/total": ("clients_total", int), #(( SESSIONS )) -  Total de sessões registradas no broker (clientes conectados + desconectados).
    "$SYS/broker/messages/received": ("messages_received", int),  # (( MESSAGES )) Total de mensagens de qualquer tipo recebidas pelo broker desde o início.
    "$SYS/broker/messages/sent": ("messages_sent", int), # (( MESSAGES )) - Total de mensagens de qualquer tipo enviadas pelo broker desde o início.
    "$SYS/broker/bytes/received": ("bytes_received", int), # (( BYTES  )) - Total de bytes recebidos pelo broker desde seu início.
    "$SYS/broker/bytes/sent": ("bytes_sent", int), # (( BYTES  )) - Total de bytes enviados pelo broker desde seu início.
    "$SYS/broker/uptime": ("uptime_seconds", int), # (( SECONDS )) - Tempo de execução do broker em segundos.
    "$SYS/broker/subscriptions/count": ("active_subscriptions", int), # (( SUBSCRIPTIONS )) - Número total de subscrições ativas (individual e shared) no broker.
    "$SYS/broker/retained messages/count": ("retained_messages", int), # (( MESSAGES )) - Número de mensagens retidas ativas no broker.
    "$SYS/broker/store/messages/bytes": ("store_messages_bytes", int), # (( BYTES )) - Total de bytes das mensagens atualmente no armazenamento.
  
    # Carga Média (load) do Broker -  médias móveis de várias métricas em janelas de 1, 5 e 15 minutos. A unidade indicada é por minuto. 
    "$SYS/broker/load/connections/1min": ("connections_per_min", float), # (( CONNECTIONS / MIN )) - Taxa média de pacotes CONNECT recebidos por minuto (1,5,15min).
    "$SYS/broker/load/messages/received/1min": ("messages_received_per_min", float), # (( MSGs / MIN )) - Taxa média de mensagens recebidas por minuto (1,5,15min).
    "$SYS/broker/load/messages/sent/1min": ("messages_sent_per_min", float), # (( MSGs / MIN )) - Taxa média de mensagens enviadas por minuto (1,5,15min).
    "$SYS/broker/load/publish/received/1min": ("publish_received_per_min", float), # (( MSGs / MIN )) - Taxa média de mensagens PUBLISH recebidas por minuto (1,5,15min).
    "$SYS/broker/load/publish/sent/1min": ("publish_sent_per_min", float), # (( MSGs / MIN )) - Taxa média de mensagens enviadas por minuto (1,5,15min).
    "$SYS/broker/load/publish/dropped/1min": ("publish_dropped_per_min", float), # (( MSGs / MIN )) - Taxa média de mensagens PUBLISH descartadas por minuto (1,5,15min). 
    "$SYS/broker/load/bytes/received/1min": ("bytes_received_per_min", float), # (( BYTES / MIN )) - Taxa média de bytes recebidos por minuto (1,5,15min).
    "$SYS/broker/load/bytes/sent/1min": ("bytes_sent_per_min", float), # (( BYTES / MIN )) - Taxa média de bytes enviados por minuto (1,5,15min).
    "$SYS/broker/load/sockets/1min": ("sockets_connected_per_min", float), # (( SOCKETS / MIN )) - Taxa média de soquetes conectados por minuto (1,5,15min).
    "$SYS/broker/heap/current": ("heap_current_bytes", int), # (( BYTES )) - Quantidade atual de memória heap usada pelo Mosquitto.
    "$SYS/broker/heap/maximum": ("heap_maximum_bytes", int), # (( BYTES )) - Pico (valor máximo) de memória heap usada pelo Mosquitto.
    "$SYS/broker/packet/out/count": ("packets_queue_pending", int), # (( PACKETS )) - Número atual de pacotes pendentes na fila de saída (todos os clientes).
    "$SYS/broker/packet/out/bytes": ("bytes_queue_pending", int), # (( BYTES )) - Total de bytes nos pacotes pendentes na fila de saída.
}
