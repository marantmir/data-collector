.PHONY: install db migrate seed test api worker deploy clean

install:
	pip install -e ".[dev]"

db:
	docker compose up -d postgres redis

migrate:
	alembic upgrade head

seed:
	python scripts/seed_from_api.py $(CNPJS)

test:
	python -m pytest tests/ -v

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A scheduler.tasks worker -B --loglevel=info

monitoring:
	docker compose up -d prometheus grafana

deploy: install db migrate test
	@echo "Deploy concluído! Execute 'make api' para iniciar"

clean:
	rm -rf __pycache__ .pytest_cache *.egg-info build dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
