#!/bin/bash

FILE="/mosquitto/config/mosquitto.passwd"
echo "👁️  Aguardando modificações em $FILE..."

if [ ! -f "$FILE" ]; then
  echo "❌ Arquivo não encontrado: $FILE"
  exit 1
fi

LAST_MODIFIED=$(stat -c %Y "$FILE")

while true; do
  CURRENT_MODIFIED=$(stat -c %Y "$FILE")
  if [ "$CURRENT_MODIFIED" != "$LAST_MODIFIED" ]; then
    echo "🔄 O arquivo 'mosquitto.passwd' foi modificado. Recarregando Mosquitto..."

   
    MOSQUITTO_PID=$(pidof mosquitto)
    if [ -z "$MOSQUITTO_PID" ]; then
      echo "⚠️  PID do Mosquitto não encontrado com 'pidof'. Usando PID=1 como padrão."
      MOSQUITTO_PID=1
    fi

    kill -HUP "$MOSQUITTO_PID" && echo "✅ Sinal SIGHUP enviado para PID $MOSQUITTO_PID"

    LAST_MODIFIED=$CURRENT_MODIFIED
  fi
  sleep 5
done
