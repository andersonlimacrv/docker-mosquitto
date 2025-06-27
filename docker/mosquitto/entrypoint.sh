#!/bin/bash

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf &
MOSQUITTO_PID=$!

/usr/local/bin/watch.sh &

wait $MOSQUITTO_PID
