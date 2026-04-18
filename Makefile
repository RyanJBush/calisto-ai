SHELL := /bin/bash

.PHONY: bootstrap lint test run-backend run-frontend up down

bootstrap:
	python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements-dev.txt
	cd frontend && npm install

lint:
	source .venv/bin/activate && cd backend && ruff check .
	cd frontend && npm run lint && npm run format:check

test:
	source .venv/bin/activate && cd backend && pytest -q

run-backend:
	source .venv/bin/activate && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

up:
	docker compose up --build

down:
	docker compose down -v
