# Makefile for Django + React (Vite) project

# Python/Django
PYTHON=python
DJANGO_MANAGE=$(PYTHON) manage.py

# Frontend
FRONTEND_DIR=quiz-spa

.PHONY: help runserver migrate createsuperuser lint lint-backend lint-frontend lint-fix start-frontend

help:
	@echo "Common commands:"
	@echo "  make runserver        # Run Django server on localhost:8000"
	@echo "  make migrate          # Run migrations"
	@echo "  make createsuperuser  # Create Django admin superuser"
	@echo "  make lint             # Run all linters (backend + frontend)"
	@echo "  make lint-backend     # Run flake8/black/mypy on backend"
	@echo "  make lint-frontend    # Run eslint/prettier on frontend"
	@echo "  make lint-fix         # Auto-fix JS/TS code style"
	@echo "  make start-frontend   # Run React dev server"

# ---------------------------
# Backend (Django / Python)
# ---------------------------
runserver:
	$(DJANGO_MANAGE) runserver 0.0.0.0:8000

migrate:
	$(DJANGO_MANAGE) makemigrations
	$(DJANGO_MANAGE) migrate

createsuperuser:
	$(DJANGO_MANAGE) createsuperuser

lint-backend:
	@echo "Linting backend..."
	flake8 .
	black --check .
	mypy .

# ---------------------------
# Frontend (React / TypeScript)
# ---------------------------
start-frontend:
	cd $(FRONTEND_DIR) && npm run dev

lint-frontend:
	@echo "Linting frontend..."
	cd $(FRONTEND_DIR) && npm run lint

lint-fix:
	cd $(FRONTEND_DIR) && npm run lint -- --fix && npm run prettier -- --write .

# ---------------------------
# Combined
# ---------------------------
lint: lint-backend lint-frontend

lint-fix-backend:
	@echo "Auto-fixing Python with black + isort..."
	black .
	isort .

lint-fix-frontend:
	cd $(FRONTEND_DIR) && npm run lint -- --fix && npm run prettier -- --write .

lint-fix: lint-fix-backend lint-fix-frontend
