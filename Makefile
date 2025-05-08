start:
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose restart mosquitto

run-api:
	poetry run uvicorn mosquitto_auth.api.main:app --reload --port 8000
