.PHONY: dev migrate seed test lint format clean

dev:
	docker-compose up -d
	@echo "Services démarrés. API disponible sur http://localhost:8000"
	@echo "Adminer disponible sur http://localhost:8080"

migrate:
	docker-compose exec api alembic upgrade head

migrate-create:
	docker-compose exec api alembic revision --autogenerate -m "$(MESSAGE)"

seed:
	docker-compose exec api python scripts/seed.py

test:
	docker-compose exec api pytest tests/ -v

lint:
	docker-compose exec api flake8 app/ tests/ --max-line-length=100 --ignore=E501
	docker-compose exec api mypy app/ --ignore-missing-imports

format:
	docker-compose exec api black app/ tests/ --line-length=100
	docker-compose exec api isort app/ tests/

clean:
	docker-compose down -v
	@echo "Conteneurs et volumes supprimés"

logs:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

shell:
	docker-compose exec api bash

shell-db:
	docker-compose exec postgres psql -U arbitrage_user -d arbitrage_db

stop:
	docker-compose stop

start:
	docker-compose start

restart:
	docker-compose restart

