# HR Platform

A layered FastAPI backend with PostgreSQL, Docker Compose, environment-based configuration, and automated tests.

## Prerequisites

- Git
- Docker Desktop with the Linux engine running
- Python 3.12 (for running tests locally)

## Setup

1. Clone the repository or open the project folder.
2. Copy `.env.example` to `.env`.
3. Update the local development credentials in `.env` if necessary. Keep `.env` private.

## Start the API and database

```bash
docker compose up --build
```

Open these URLs:

- API root: http://localhost:8000/
- Health check: http://localhost:8000/health
- Interactive API documentation: http://localhost:8000/docs

## Run tests locally

Create a virtual environment with Python 3.12, activate it, and install dependencies:

```bash
python -m venv .venv
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Useful commands

Stop the services:

```bash
docker compose down
```

Stop services and remove the development database volume:

```bash
docker compose down -v
```

**Warning:** `docker compose down -v` deletes the database's persisted development data.

View logs:

```bash
docker compose logs -f api
docker compose logs -f db
```

## Project structure

- `app/api/routes/`: HTTP endpoints
- `app/core/`: settings and shared configuration
- `app/services/`: business logic
- `app/models/`: database models
- `tests/`: automated tests
- `contracts/`: draft API contract
- `sample_data/`: synthetic employee data

## Security

- `.env` is excluded from Git.
- `.env.example` documents required settings without real secrets.
- Development credentials must be replaced before production use.

## Current scope

Task 1 provides the application skeleton, health endpoint, container configuration, initial test, API contract, and sample employee data. Database models and employee CRUD endpoints are planned for subsequent tasks.