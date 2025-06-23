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

docker-logs: ## Ver logs de todos os serviços
	docker-compose logs -f

api-logs: ## Ver logs apenas da API
	docker-compose logs -f api

mosquitto-logs: ## Ver logs apenas do Mosquitto
	docker-compose logs -f mosquitto