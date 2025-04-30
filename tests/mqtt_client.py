import paho.mqtt.client as mqtt
import sys
import ssl
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

RC_MESSAGES = {
    0: "✓ - RC 0: Conexão estabelecida com sucesso (TLS e autenticação válidos)",
    1: "✗ - RC 1: Conexão recusada: Versão inválida do protocolo MQTT",
    2: "✗ - RC 2: Conexão recusada: Identificador de cliente inválido",
    3: "✗ - RC 3: Conexão recusada: Broker MQTT indisponível",
    4: "✗ - RC 4: Conexão recusada: Usuário ou senha inválidos",
    5: "✗ - RC 5: Conexão recusada: Acesso não autorizado (ACL)",
    6: "✗ - RC 6: Erro: Conexão não autorizada (outros motivos)",
    # Códigos 7-255 usam a mesma mensagem
}

def on_connect(client, userdata, flags, rc):
    """Callback para eventos de conexão MQTT"""
    message = RC_MESSAGES.get(rc, "✗ Erro desconhecido (código reservado)")
    
    print("\n" + "="*50)
    print(message)
    
    if rc == 1:
        print("Solução: Verifique a versão do protocolo no cliente e broker")
    elif rc == 4:
        print("Solução: Verifique usuário/senha no arquivo mosquitto.passwd")
    elif rc == 5:
        print("Solução: Verifique as ACLs no mosquitto.conf")
    
    print("="*50)
    client.disconnect()

def test_mqtt_connection():
    if len(sys.argv) < 3:
        print("Uso: poetry run test-mqtt <usuário> <senha>")
        return
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"\n### TESTE MQTT (usuário: {username}) ###")

    host = 'localhost' 
    port = 8883

    client = mqtt.Client(protocol=mqtt.MQTTv311, client_id=username)
    
    try:
        client.tls_set(
            ca_certs=str(BASE_DIR / "certs/ca.crt"),
            certfile=str(BASE_DIR / "certs/client/client.crt"),
            keyfile=str(BASE_DIR / "certs/client/client.key"),
            tls_version=ssl.PROTOCOL_TLSv1_2,
            cert_reqs=ssl.CERT_REQUIRED
        )
    except Exception as e:
        print(f"Erro ao configurar TLS: {str(e)}")
        print("Verifique os caminhos dos certificados:")
        print(f"- CA: {BASE_DIR / 'certs/ca.crt'}")
        print(f"- Cert: {BASE_DIR / 'certs/client/client.crt'}")
        print(f"- Key: {BASE_DIR / 'certs/client/client.key'}")
        return

    client.username_pw_set(username, password)
    client.on_connect = on_connect

    try:
        print(f"Conectando a {host}:{port}...")
        client.connect(host, port, 10)
        print("Negociação TLS iniciada...")
        client.loop_forever()
    except ssl.SSLError as e:
        print(f"Erro TLS: {str(e)}")
        print("Possíveis causas:")
        print("- Certificados inválidos/expirados")
        print("- Versão TLS incompatível")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
    finally:
        client.loop_stop()

if __name__ == "__main__":
    test_mqtt_connection()