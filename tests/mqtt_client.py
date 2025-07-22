import paho.mqtt.client as mqtt
import sys
import ssl
from pathlib import Path
from mosquitto_auth.api.core.config import settings

BASE_DIR = Path(__file__).parent.parent

RC_MESSAGES = {
    0: "✅ Connection established successfully (valid TLS and authentication)",
    1: "🚫 RC 1: Connection refused - Incorrect MQTT protocol version",
    2: "🚫 RC 2: Connection refused - Invalid client identifier",
    3: "🚫 RC 3: Connection refused - MQTT broker unavailable",
    4: "🚫 RC 4: Connection refused - Invalid username or password",
    5: "🚫 RC 5: Connection refused - Unauthorized access (ACL)",
    6: "🚫 RC 6: Error - Unauthorized connection (other reasons)",
}

MAX_ATTEMPTS = 5
attempt_count = 0

def on_connect(client, userdata, flags, rc):
    """Callback for MQTT connection events"""
    global attempt_count
    attempt_count += 1
    
    print("\n🎯 Connection result:")
    print("═" * 80)

    message = RC_MESSAGES.get(rc, "❗ Unknown error (reserved code)")
    print(f"🔢 Return code: {rc}")
    print(f"📈 Status: {message}")
    print(f"🔁 Attempt: {attempt_count}/{MAX_ATTEMPTS}")

    if rc == 1:
        print("💡 Tip: Check the MQTT protocol version set in both the broker and the client.")
    elif rc == 4:
        print("💡 Tip: Verify credentials in the `.env` file and `mosquitto.passwd`.")
    elif rc == 5:
        print("💡 Tip: Review ACL definitions in `mosquitto.conf`.")

    if rc == 0:
        try:
            print("📡 Publishing test message to 'test/connection' topic...")
            client.publish("test/connection", payload="MQTT secure test successful!", qos=1)
        except Exception as e:
            print(f"❌ Failed to publish test message: {e}")
    
    elif attempt_count >= MAX_ATTEMPTS:
        print(f"❌ Maximum connection attempts ({MAX_ATTEMPTS}) reached. Stopping.")
        client.disconnect()
        client.loop_stop()

    print("═" * 80)


def on_publish(client, userdata, mid):
    """Callback when a message is published"""
    print("✅ Test message published successfully!")
    print("═" * 80)
    client.disconnect()
    client.loop_stop()


def test_mqtt_connection():
    global attempt_count
    attempt_count = 0  
    
    if len(sys.argv) < 4:
        print("❗ Usage: poetry run test-mqtt <username> <password> <CN_CLIENT>")
        return

    username = sys.argv[1]
    password = sys.argv[2]
    cn_client = sys.argv[3]

    print("\n🚀 Starting secure MQTT connection test")
    print("🔐 Authentication and TLS enabled")
    print(f"👤 Username: {username}")
    print(f"📄 Certificate CN: {cn_client}")
    print(f"♻️ Max connection attempts: {MAX_ATTEMPTS}")

    host = settings.BROKER_CN or "localhost"
    port = settings.BROKER_PORT

    client = mqtt.Client(protocol=mqtt.MQTTv311, client_id=username)

    client.reconnect_delay_set(min_delay=1, max_delay=3)

    try:
        client_cert_dir = BASE_DIR / f"certs/client/{cn_client}"

        client.tls_set(
            ca_certs=str(BASE_DIR / "certs/ca.crt"),
            certfile=str(client_cert_dir / f"{cn_client}.crt"),
            keyfile=str(client_cert_dir / f"{cn_client}.key"),
            tls_version=ssl.PROTOCOL_TLSv1_2,
            cert_reqs=ssl.CERT_REQUIRED
        )
        print("📁 Certificates loaded successfully")
    except Exception as e:
        print(f"\n❌ TLS configuration error: {e}")
        print("🔎 Check the certificate file paths:")
        print(f"   📄 CA:    {BASE_DIR / 'certs/ca.crt'}")
        print(f"   📄 Cert:  {client_cert_dir / f'{cn_client}.crt'}")
        print(f"   🔑 Key:   {client_cert_dir / f'{cn_client}.key'}")
        return

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        print(f"\n🌐 Connecting to {host}:{port} ...")
        client.connect(host, port, keepalive=10)
        print("🔄 TLS handshake in progress...")
        client.loop_forever()
    except ssl.SSLError as e:
        print(f"\n❌ TLS Error: {e}")
        print("🛠 Possible causes:")
        print("- Invalid, corrupted, or expired certificates")
        print("- TLS version mismatch between client and broker")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("\n📡 Disconnecting...")
        client.loop_stop()


if __name__ == "__main__":
    test_mqtt_connection()