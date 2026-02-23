.PHONY: help setup venv install db-up db-down db-reset migrate migrate-create run test clean docker-build docker-up docker-down docker-status docker-logs docker-migrate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────
#  Full Setup (run this first)
# ──────────────────────────────────────
setup: venv install db-up migrate ## Full project setup (venv + deps + db + migrations)
	@echo "\n✅  GoalPilot is ready! Run 'make run' to start the server.\n"

# ──────────────────────────────────────
#  Python Environment
# ──────────────────────────────────────
venv: ## Create Python virtual environment
	@test -d venv || python3 -m venv venv
	@echo "✅  venv created"

install: venv ## Install Python dependencies
	venv/bin/pip install -r requirements.txt --quiet
	@echo "✅  Dependencies installed"

# ──────────────────────────────────────
#  Database (Docker Postgres)
# ──────────────────────────────────────
db-up: ## Start PostgreSQL container
	docker compose up -d
	@echo "⏳  Waiting for Postgres to be ready..."
	@until docker exec goalpilot_db pg_isready -U goalpilot -d goalpilot_db > /dev/null 2>&1; do sleep 1; done
	@echo "✅  PostgreSQL is running on port 5434"

db-down: ## Stop PostgreSQL container
	docker compose down
	@echo "✅  PostgreSQL stopped"

db-reset: db-down ## Reset database (destroy data + restart + re-migrate)
	docker volume rm goalproject_goalpilot_pgdata 2>/dev/null || true
	$(MAKE) db-up migrate
	@echo "✅  Database reset complete"

# ──────────────────────────────────────
#  Migrations (Alembic)
# ──────────────────────────────────────
migrate: ## Run all pending migrations
	venv/bin/alembic upgrade head
	@echo "✅  Migrations applied"

migrate-create: ## Create a new migration (usage: make migrate-create msg="add_xyz")
	venv/bin/alembic revision --autogenerate -m "$(msg)"
	@echo "✅  Migration created"

# ──────────────────────────────────────
#  Run
# ──────────────────────────────────────
run: ## Start FastAPI dev server (with hot reload)
	venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Start FastAPI production server
	venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# ──────────────────────────────────────
#  Docker
# ──────────────────────────────────────
docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start all services in Docker
	docker compose up -d
	@echo "✅  GoalPilot is running in Docker at http://localhost:8000"

docker-down: ## Stop and remove all Docker containers
	docker compose down

docker-status: ## Show status of Docker containers
	docker compose ps

docker-logs: ## Show logs from Docker containers
	docker compose logs -f

docker-migrate: ## Run migrations inside the app container
	docker compose exec app alembic upgrade head
	@echo "✅  Migrations applied in Docker"

# ──────────────────────────────────────
#  Testing
# ──────────────────────────────────────
test: ## Run tests
	venv/bin/pytest tests/ -v

# ──────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────
clean: ## Remove venv and cached files
	rm -rf venv __pycache__ .pytest_cache
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@echo "✅  Cleaned"
