.PHONY: install dev api web test lint format build

install:
	uv sync --directory apps/api --all-groups
	npm install

dev:
	npm run dev

api:
	uv run --directory apps/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	npm run dev:web

test:
	uv run --directory apps/api pytest
	npm run test:web

lint:
	uv run --directory apps/api ruff check .
	npm run lint:web

format:
	uv run --directory apps/api ruff format .
	npm run format:web

build:
	npm run build:web
