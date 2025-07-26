#!/bin/bash

PASSWD_FILE="/mosquitto/config/mosquitto.passwd"
CERTS_DIR="/mosquitto/certs"

echo "👁️  Aguardando modificações em:"
echo "  🔐 Arquivo: $PASSWD_FILE"
echo "  📁 Diretório: $CERTS_DIR"

if [ ! -f "$PASSWD_FILE" ]; then
  echo "❌ Arquivo não encontrado: $PASSWD_FILE"
  exit 1
fi

if [ ! -d "$CERTS_DIR" ]; then
  echo "❌ Diretório não encontrado: $CERTS_DIR"
  exit 1
fi

generate_cert_checksum() {
  find "$CERTS_DIR" -type f -exec md5sum {} \; | sort | md5sum
}

LAST_PASSWD_MODIFIED=$(stat -c %Y "$PASSWD_FILE")
LAST_CERTS_CHECKSUM=$(generate_cert_checksum)

while true; do
  CURRENT_PASSWD_MODIFIED=$(stat -c %Y "$PASSWD_FILE")
  CURRENT_CERTS_CHECKSUM=$(generate_cert_checksum)

  if [ "$CURRENT_PASSWD_MODIFIED" != "$LAST_PASSWD_MODIFIED" ] || [ "$CURRENT_CERTS_CHECKSUM" != "$LAST_CERTS_CHECKSUM" ]; then
    echo "🔄 Alteração detectada (senha ou certificado). Recarregando Mosquitto..."

    MOSQUITTO_PID=$(pidof mosquitto)
    if [ -z "$MOSQUITTO_PID" ]; then
      echo "⚠️  PID do Mosquitto não encontrado com 'pidof'. Usando PID=1 como padrão."
      MOSQUITTO_PID=1
    fi

    kill -HUP "$MOSQUITTO_PID" && echo "✅ Sinal SIGHUP enviado para PID $MOSQUITTO_PID"

    LAST_PASSWD_MODIFIED=$CURRENT_PASSWD_MODIFIED
    LAST_CERTS_CHECKSUM=$CURRENT_CERTS_CHECKSUM
  fi

  sleep 5
done
