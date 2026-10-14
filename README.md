# LedgerForge HR Platform

A layered FastAPI backend for HR data management using PostgreSQL, SQLAlchemy, Alembic migrations, Docker Compose, environment-based configuration, and automated tests.

## Prerequisites

- Git
- Docker Desktop with the Linux engine running
- Python 3.12
- A Python virtual environment

## Setup

1. Clone the repository or open the project folder.
2. Copy `.env.example` to `.env`.
3. Update the local development credentials in `.env` if necessary.
4. Keep `.env` private and never commit secrets.

Install dependencies:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Start the API and database

```bash
docker compose up --build
```

Available endpoints:

- API root: http://localhost:8000/
- Health check: http://localhost:8000/health
- Interactive API documentation: http://localhost:8000/docs

## Database and migrations

The database model includes:

- Departments
- Roles
- Employees
- Employee assignment history

SQLAlchemy models are maintained in `app/models/`. Alembic migration scripts are maintained in `migrations/`.

Useful commands:

```cmd
alembic heads
alembic current
alembic upgrade head
```

Apply migrations before running the application against a newly initialized database.

## Master dataset

The source workbook is:

`01_LedgerForge_Python_Master_Dataset.xlsx`

The workbook contains the HR master data and related business datasets. The verified source row counts for the core and export sheets are:

| Sheet | Data rows, excluding header |
|---|---:|
| departments | 11 |
| roles | 58 |
| employees | 745 |
| employee_assignments | 1,606 |
| salary_structures | 12,295 |
| attendance | 150,155 |

## Seed master data

The seed script loads departments and roles from the workbook and uses PostgreSQL upserts so repeated runs update existing master records instead of inserting duplicates.

```cmd
python -m scripts.seed
```

The current seed script seeds **departments and roles only**. It does not load every workbook sheet into PostgreSQL.

## Generate additional synthetic employees

The additional employee generator uses Faker with a fixed seed of `2026` to create 50 synthetic employee records.

```cmd
python -m scripts.extra_fake
```

Output:

`data/extra_fake_employees.csv`

These records are separate from the master workbook and are not automatically inserted into PostgreSQL.

## Export CSV files

Export the workbook's employee, salary structure, and attendance sheets:

```cmd
python -m scripts.export_csv
```

Output files:

- `exports/employees.csv`
- `exports/salary_structures.csv`
- `exports/attendance.csv`

The export script preserves the workbook's column order and writes the sheet data to CSV. The verified output counts are 745, 12,295, and 150,155 data rows, respectively.

## Run tests locally

```cmd
python -m pytest -v
```

Run tests after changes to models, migrations, routes, or services. The full test suite has previously passed in this development environment.

## Project structure

- `app/api/routes/` — HTTP endpoints
- `app/core/` — settings and shared configuration
- `app/services/` — business logic
- `app/models/` — SQLAlchemy models
- `migrations/` — Alembic migration history
- `scripts/seed.py` — department and role seeding
- `scripts/extra_fake.py` — reproducible synthetic employee generation
- `scripts/export_csv.py` — CSV exports from the workbook
- `tests/` — automated tests
- `docs/employee-data-model.md` — employee data model diagram
- `docs/api-contract.md` — API contract
- `data/` — generated synthetic employee data
- `exports/` — generated CSV exports

## Security

- `.env` is excluded from Git.
- `.env.example` documents required settings without real secrets.
- Development credentials must be replaced before production use.
- Never commit passwords, API keys, or production secrets.

## Important database warning

To stop services without deleting persisted database data:

```bash
docker compose down
```

**Warning:** `docker compose down -v` removes the development database volume and deletes its persisted data. Do not run it unless you intentionally want to remove that data.

## Handoff verification

Before handoff:

1. Verify the Alembic migration head and current database revision.
2. Check the health endpoint and API documentation.
3. Run the automated tests.
4. Confirm that the generated CSV files contain the expected row counts.
5. Review `git status` and ensure no secrets or unwanted generated files are included.

Create a handoff Git tag only after the required files, endpoints, and tests have been verified.