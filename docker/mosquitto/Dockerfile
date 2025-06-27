FROM eclipse-mosquitto:2.0.21-openssl

USER root

RUN apk add --no-cache bash coreutils

COPY docker/mosquitto/watch.sh /usr/local/bin/watch.sh
COPY docker/mosquitto/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/watch.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
