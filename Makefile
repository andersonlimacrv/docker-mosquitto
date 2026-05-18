DOCKER_COMPOSE=docker compose

build-nc:
	$(DOCKER_COMPOSE) build --no-cache

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

deploy:
	$(DOCKER_COMPOSE) down && $(DOCKER_COMPOSE) up -d --build

down:
	$(DOCKER_COMPOSE) down

remake start:
	$(DOCKER_COMPOSE) restart mosquitto

run-api-dev:
	poetry run uvicorn mosquitto_auth.api.main:app --reload --port 8000

logs: 
	$(DOCKER_COMPOSE) logs -f

api-logs: 
	$(DOCKER_COMPOSE) logs -f api

mosquitto-logs: 
	$(DOCKER_COMPOSE) logs -f mosquitto 

reborn:
	$(DOCKER_COMPOSE) down && $(DOCKER_COMPOSE) build --no-cache && $(DOCKER_COMPOSE) up -d