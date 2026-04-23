.PHONY: bootstrap init db-upgrade db-downgrade lint test run-backend run-frontend

bootstrap:
	python -m pip install --upgrade pip
	pip install -r backend/requirements.txt
	npm --prefix frontend install

init:
	cd backend && PYTHONPATH=. python scripts/init_db.py

db-upgrade:
	cd backend && PYTHONPATH=. alembic upgrade head

db-downgrade:
	cd backend && PYTHONPATH=. alembic downgrade -1

lint:
	ruff check backend
	npm --prefix frontend run lint

test:
	cd backend && rm -f test.db && DATABASE_URL=sqlite:///./test.db pytest tests
	npm --prefix frontend run build

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173
