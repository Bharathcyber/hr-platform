
import json
import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "scripts" / "sample_employees.json"


def main():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        employees = json.load(file)

    columns = [
        "employee_id",
        "first_name",
        "last_name",
        "full_name",
        "work_email",
        "gender",
        "date_of_birth",
        "hire_date",
        "exit_date",
        "employment_status",
        "employment_type",
        "department_id",
        "role_id",
        "manager_id",
        "work_location",
        "work_mode",
        "highest_education",
        "prior_experience_years",
        "career_gap_months",
        "commute_distance_km",
        "pf_applicable",
        "esi_applicable",
        "notice_period_days",
        "resignation_date",
        "exit_type",
        "exit_reason",
        "created_at",
    ]

    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(columns)

    insert_sql = (
        f"INSERT INTO employees ({column_sql}) "
        f"VALUES ({placeholders}) "
        "ON CONFLICT (employee_id) DO NOTHING"
    )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            for employee in employees:
                values = [employee.get(column) for column in columns]
                cursor.execute(insert_sql, values)

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM employees")
            total = cursor.fetchone()[0]

    print(f"Sample records in file: {len(employees)}")
    print(f"Total employees in database: {total}")


if __name__ == "__main__":
    main()
