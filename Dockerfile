FROM python:3.12-slim

ENV POETRY_VERSION=1.8.2
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    mosquitto \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-root

COPY mosquitto_auth ./mosquitto_auth

CMD ["poetry", "run", "start"]
