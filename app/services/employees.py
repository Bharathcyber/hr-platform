
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import psycopg
from fastapi import HTTPException

from app.core.config import settings


DEMO_TODAY = date(2026, 9, 30)


def get_connection():
    database_url = settings.database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
    return psycopg.connect(database_url)


def serialize_employee(row):
    result = dict(row)

    for key, value in result.items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)

    return result


def validate_hire_date(hire_date):
    if hire_date is not None and hire_date > DEMO_TODAY:
        raise HTTPException(
            status_code=422,
            detail="Hire date cannot be after DEMO_TODAY.",
        )


def validate_employee_dates(hire_date, exit_date):
    validate_hire_date(hire_date)

    if (
        hire_date is not None
        and exit_date is not None
        and exit_date < hire_date
    ):
        raise HTTPException(
            status_code=422,
            detail="Exit date cannot be before hire date.",
        )


def validate_hire_date_range(hire_date_from, hire_date_to):
    if (
        hire_date_from is not None
        and hire_date_to is not None
        and hire_date_from > hire_date_to
    ):
        raise HTTPException(
            status_code=422,
            detail="hire_date_from cannot be after hire_date_to.",
        )


def list_employees(
    limit: int = 100,
    offset: int = 0,
    department_id: Optional[str] = None,
    role_id: Optional[str] = None,
    employment_status: Optional[str] = None,
    work_location: Optional[str] = None,
    work_mode: Optional[str] = None,
    manager_id: Optional[str] = None,
    hire_date_from: Optional[date] = None,
    hire_date_to: Optional[date] = None,
    q: Optional[str] = None,
):
    validate_hire_date_range(hire_date_from, hire_date_to)

    conditions = ["is_active = TRUE"]
    values = []

    filters = {
        "department_id": department_id,
        "role_id": role_id,
        "employment_status": employment_status,
        "work_location": work_location,
        "work_mode": work_mode,
        "manager_id": manager_id,
    }

    for column, value in filters.items():
        if value is not None:
            conditions.append(f"{column} = %s")
            values.append(value)

    if hire_date_from is not None:
        conditions.append("hire_date >= %s")
        values.append(hire_date_from)

    if hire_date_to is not None:
        conditions.append("hire_date <= %s")
        values.append(hire_date_to)

    if q and q.strip():
        conditions.append(
            "(full_name ILIKE %s OR work_email ILIKE %s "
            "OR employee_id ILIKE %s)"
        )
        search = f"%{q.strip()}%"
        values.extend([search, search, search])

    query = f"""
        SELECT *
        FROM employees
        WHERE {" AND ".join(conditions)}
        ORDER BY employee_id
        LIMIT %s OFFSET %s
    """

    values.extend([limit, offset])

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                rows = cursor.fetchall()
                columns = [
                    item.name for item in cursor.description
                ]

        employees = [
            serialize_employee(dict(zip(columns, row)))
            for row in rows
        ]

        return {
            "count": len(employees),
            "limit": limit,
            "offset": offset,
            "employees": employees,
        }

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve employees from the database.",
        ) from exc


def get_direct_reports(manager_id: str):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM employees
                    WHERE manager_id = %s
                      AND is_active = TRUE
                    ORDER BY employee_id
                    """,
                    (manager_id,),
                )

                rows = cursor.fetchall()
                columns = [
                    item.name for item in cursor.description
                ]

        return [
            serialize_employee(dict(zip(columns, row)))
            for row in rows
        ]

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve direct reports from the database.",
        ) from exc


def soft_delete_employee(employee_id: str):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE employees
                    SET is_active = FALSE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE employee_id = %s
                      AND is_active = TRUE
                    RETURNING employee_id
                    """,
                    (employee_id,),
                )

                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Active employee not found.",
                    )

        return {
            "message": "Employee deactivated successfully.",
            "employee_id": row[0],
        }

    except HTTPException:
        raise

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to deactivate employee in the database.",
        ) from exc
