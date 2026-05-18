#!/bin/bash

PASSWD_FILE="/mosquitto/config/mosquitto.passwd"
CERTS_DIR="/mosquitto/certs"
LOG_DIR="/mosquitto/log"
LOG_FILE="${LOG_DIR}/mosquitto.log"

echo "👁️  Aguardando modificações em:"
echo "  🔐 Arquivo: $PASSWD_FILE"
echo "  📁 Diretório: $CERTS_DIR"

if [ -d "$LOG_DIR" ]; then
  echo "✅ Diretório de log já existe: $LOG_DIR"
else
  echo "📁 Criando diretório de log: $LOG_DIR"
  mkdir -p "$LOG_DIR"
  if [ $? -eq 0 ]; then
    echo "✅ Diretório de log criado com sucesso: $LOG_DIR"
  else
    echo "❌ Falha ao criar diretório de log: $LOG_DIR"
    exit 1
  fi
fi

echo "🔧 Ajustando permissões do arquivo de log..."
chmod 666 "$LOG_FILE"
if [ $? -eq 0 ]; then
  echo "✅ Permissões ajustadas para 666: $LOG_FILE"
else
  echo "⚠️  Falha ao ajustar permissões do arquivo: $LOG_FILE"
fi

echo "📝 Log configurado em: $LOG_FILE"

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
