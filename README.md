# GoalPilot Backend

GoalPilot is a robust FastAPI-based backend for goal tracking and management. It features a complete implementation of goals, milestones, tasks, analytics, and notifications.

## Features

- **Authentication**: JWT-based secure authentication.
- **Goal Management**: Track goals, milestones, and tasks.
- **Analytics**: Auto-calculated progress and performance metrics.
- **Notifications**: Real-time updates and alerts.
- **Database**: PostgreSQL with Alembic migrations.
- **Dockerized**: Easy setup with Docker and Docker Compose.

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Make (optional, but recommended)

## Setup Guidelines

### 1. Environment Configuration

Copy the example environment file and update the values if necessary:

```bash
cp .env.example .env
```

### 2. Docker Setup (Recommended)

The easiest way to get started is using Docker. This will spin up both the FastAPI application and the PostgreSQL database.

```bash
# Build and start services
make docker-up

# Run migrations (first time only)
make docker-migrate
```

The API will be available at `http://localhost:8000`.
Swagger documentation (interactive UI) is at `http://localhost:8000/docs`.

### 3. Local Setup (Development)

If you prefer to run the application locally (e.g., for hot-reloading during development):

```bash
# Initialize virtual environment and install dependencies
make setup

# Start the database container only
make db-up

# Run migrations
make migrate

# Start the FastAPI server
make run
```

## Useful Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Full project setup (venv + deps + db + migrations) |
| `make run` | Start FastAPI dev server with hot reload |
| `make test` | Run pytest suite |
| `make docker-up` | Start all services in Docker |
| `make docker-down` | Stop and remove all Docker containers |
| `make docker-migrate`| Run migrations inside the app container |
| `make db-reset` | Reset database (destroy data + restart + re-migrate) |

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
