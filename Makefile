build:
	docker-compose build --no-cache

start:
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose restart mosquitto

run-api:
	poetry run uvicorn mosquitto_auth.api.main:app --reload --port 8000

docker-logs: 
	docker-compose logs -f

api-logs: 
	docker-compose logs -f api

mosquitto-logs: 
	docker-compose logs -f mosquitto 

reborn:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d