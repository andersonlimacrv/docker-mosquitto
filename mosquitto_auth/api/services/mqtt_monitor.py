import asyncio
import ssl
from pathlib import Path
from datetime import datetime
import aiomqtt

from mosquitto_auth.api.core.config import settings
from mosquitto_auth.api.core.state import (
    broker_state, 
    metrics_dispatcher, 
    TOPIC_MAP,
    BrokerAvailability, 
    ContainerAvailability
)

async def _process_sys_message(topic: str, payload: bytes):
    try:
        decoded_payload = payload.decode()
        if topic in TOPIC_MAP:
            field_name, cast_fn = TOPIC_MAP[topic]
            try:
                # Trata números no formato "X.XX bytes/sec" ou puramente numerico
                clean_payload = decoded_payload.split()[0] if isinstance(decoded_payload, str) else decoded_payload
                value = cast_fn(clean_payload)
                setattr(broker_state.metrics, field_name, value)
            except ValueError:
                pass # Ignora payload incompatível
        
        broker_state.last_sys_update_at = datetime.utcnow()
        await metrics_dispatcher.broadcast(broker_state.to_dict())
    except Exception as e:
        print(f"[Monitor] Erro processando métrica: {e}")

async def start_mqtt_monitor():
    """Background task resiliente para monitorar a árvore $SYS/#."""
    
    user = settings.USER_MQTT_MONITOR
    cert_dir = settings.certs_dir / "client" / user
    cert_path = cert_dir / f"{user}.crt"
    key_path = cert_dir / f"{user}.key"
    
    delay = 1.0

    while True:
        # Verifica se o container tem os certificados da CA gerados
        if not settings.ca_cert_path.exists():
            broker_state.broker_status = BrokerAvailability.AWAITING_CERTS
            broker_state.last_error = "CA Certificate não encontrado. Broker ainda em provisionamento."
            await asyncio.sleep(5)
            continue

        if not cert_path.exists() or not key_path.exists():
            broker_state.broker_status = BrokerAvailability.AWAITING_CERTS
            broker_state.last_error = "Certificados do monitor não encontrados."
            await asyncio.sleep(5)
            continue

        broker_state.broker_status = BrokerAvailability.RECONNECTING
        
        try:
            tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            tls_context.load_verify_locations(cafile=str(settings.ca_cert_path))
            tls_context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
            tls_context.verify_mode = ssl.CERT_REQUIRED
            
            async with aiomqtt.Client(
                hostname=settings.BROKER_CN,
                port=settings.BROKER_PORT,
                username=settings.USER_MQTT_MONITOR,
                password=settings.PASSWD_MQTT_MONITOR,
                tls_context=tls_context,
                timeout=10.0,
                keepalive=60,
                identifier=f"brk_{settings.USER_MQTT_MONITOR}"
            ) as client:
                
                print(f"[Monitor] Conectado ao Broker MQTT com sucesso.")
                broker_state.broker_status = BrokerAvailability.ONLINE
                broker_state.last_error = None
                broker_state.last_connected_at = datetime.utcnow()
                delay = 1.0 # Reseta o backoff
                
                await client.subscribe("$SYS/#")
                
                async for message in client.messages:
                    await _process_sys_message(message.topic.value, message.payload)
                    
                    # Stale detection loop interno ou baseado em timeout de mensagem
                    # Uma abordagem melhor é ter uma task paralela de stale detection, 
                    # mas aqui só processamos as mensagens conforme chegam.

        except aiomqtt.MqttError as e:
            broker_state.broker_status = BrokerAvailability.OFFLINE
            broker_state.last_error = f"MqttError: {e}"
            broker_state.last_disconnect_at = datetime.utcnow()
            print(f"[Monitor] Conexão perdida: {e}. Tentando reconectar...")
        except Exception as e:
            broker_state.broker_status = BrokerAvailability.OFFLINE
            broker_state.last_error = f"Erro Inesperado: {e}"
            broker_state.last_disconnect_at = datetime.utcnow()
            print(f"[Monitor] Erro fatal no monitor loop: {e}")

        # Backoff Exponencial
        delay = min(delay * 2, 60.0) 
        await asyncio.sleep(delay)
