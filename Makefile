.PHONY: bootstrap init lint test run-backend run-frontend

bootstrap:
	python -m pip install --upgrade pip
	pip install -r backend/requirements.txt
	npm --prefix frontend install

init:
	cd backend && PYTHONPATH=. python scripts/init_db.py

lint:
	ruff check backend
	npm --prefix frontend run lint

test:
	cd backend && pytest tests
	npm --prefix frontend run build

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173
