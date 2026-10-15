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
- Versioned health check: http://localhost:8000/api/v1/health
- Interactive API documentation: http://localhost:8000/docs

## Database and migrations

The database model includes:

- Departments
- Roles
- Employees
- Employee assignment history
- User and HR reference models

SQLAlchemy models are maintained in `app/models/`. Alembic migration scripts are maintained in `migrations/`.

Useful commands:

```cmd
python -m alembic heads
python -m alembic current
python -m alembic upgrade head
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

The seed script loads and validates workbook data and supports a dry-run mode before writing to the database.

Preview the seed operation:

```cmd
python -m scripts.seed --dry-run
```

Run the seed operation:

```cmd
python -m scripts.seed
```

The seed process covers the configured department, role, employee, employee assignment, user, salary component, holiday, and leave-type data. Review the seed output and database counts after running it. Do not reset or delete existing database records merely to match workbook counts.

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

The export script preserves the workbook's column order. The verified output counts are 745, 12,295, and 150,155 data rows, respectively.

## Run tests locally

```cmd
python -m pytest -v
```

For the focused employee and health test suites:

```cmd
python -m pytest tests\test_employees.py tests\test_health.py -q
```

Run tests after changes to models, migrations, routes, or services. Record the actual test result for the version being handed off.

## Project structure

- `app/api/routes/` — HTTP endpoints
- `app/core/` — settings and shared configuration
- `app/services/` — business logic
- `app/models/` — SQLAlchemy models
- `migrations/` — Alembic migration history
- `scripts/seed.py` — workbook validation and database seeding
- `scripts/extra_fake.py` — reproducible synthetic employee generation
- `scripts/export_csv.py` — CSV exports from the workbook
- `scripts/sample_employees.json` — 10 sample employee records for handoff
- `tests/` — automated tests
- `docs/employee-data-model.md` — employee data model diagram
- `docs/api-contract.md` — API contract
- `data/` — generated synthetic employee data
- `exports/` — generated CSV exports

## Handoff package

The Phase 1 handoff files are available here:

- [API contract](docs/api-contract.md) — documents implemented endpoints and distinguishes planned functionality.
- [Sample employee data](scripts/sample_employees.json) — valid JSON containing 10 sample employee records.

### Handoff verification

Before releasing a handoff:

1. Verify the Alembic current revision matches the migration head.
2. Verify the health endpoint and API documentation.
3. Run the automated tests and record the results.
4. Confirm the expected CSV row counts.
5. Review Git changes and exclude secrets, local datasets, and backup files.
6. Confirm the handoff tag points to the intended commit and publish it only after the required checks pass.

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