build-nc:
	docker-compose build --no-cache

build:
	docker-compose build

start:
	docker-compose up -d

deploy:
	docker-compose down && docker-compose up -d --build

stop:
	docker-compose down

restart:
	docker-compose restart mosquitto

run-api-dev:
	poetry run uvicorn mosquitto_auth.api.main:app --reload --port 8000

logs: 
	docker-compose logs -f

api-logs: 
	docker-compose logs -f api

mosquitto-logs: 
	docker-compose logs -f mosquitto 

reborn:
	docker-compose down &&
	docker-compose build --no-cache &&
	docker-compose up -d