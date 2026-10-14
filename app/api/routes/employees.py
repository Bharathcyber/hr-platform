from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import psycopg
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings

router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


def get_connection():
    database_url = settings.database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
    return psycopg.connect(database_url)


class EmployeeCreate(BaseModel):
    employee_id: str = Field(min_length=1, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    full_name: str = Field(min_length=1, max_length=201)
    work_email: EmailStr
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: Optional[date] = None
    exit_date: Optional[date] = None
    employment_status: str = Field(min_length=1, max_length=30)
    employment_type: Optional[str] = None
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    manager_id: Optional[str] = None
    work_location: Optional[str] = None
    work_mode: Optional[str] = None
    highest_education: Optional[str] = None
    prior_experience_years: int = Field(default=0, ge=0)
    career_gap_months: int = Field(default=0, ge=0)
    commute_distance_km: Optional[Decimal] = None
    pf_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    esi_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    notice_period_days: Optional[int] = Field(default=None, ge=0)
    resignation_date: Optional[date] = None
    exit_type: Optional[str] = None
    exit_reason: Optional[str] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=201)
    work_email: Optional[EmailStr] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: Optional[date] = None
    exit_date: Optional[date] = None
    employment_status: Optional[str] = None
    employment_type: Optional[str] = None
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    manager_id: Optional[str] = None
    work_location: Optional[str] = None
    work_mode: Optional[str] = None
    highest_education: Optional[str] = None
    prior_experience_years: Optional[int] = Field(default=None, ge=0)
    career_gap_months: Optional[int] = Field(default=None, ge=0)
    commute_distance_km: Optional[Decimal] = None
    pf_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    esi_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    notice_period_days: Optional[int] = Field(default=None, ge=0)
    resignation_date: Optional[date] = None
    exit_type: Optional[str] = None
    exit_reason: Optional[str] = None


def serialize_employee(row):
    result = dict(row)
    for key, value in result.items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)
    return result


@router.get("")
def list_employees(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM employees
                    ORDER BY employee_id
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                rows = cursor.fetchall()
                columns = [item.name for item in cursor.description]

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

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve employees from the database.",
        )


@router.get("/{employee_id}")
def get_employee(employee_id: str):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM employees WHERE employee_id = %s",
                    (employee_id,),
                )
                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Employee not found.",
                    )

                columns = [item.name for item in cursor.description]
                employee = dict(zip(columns, row))

        return serialize_employee(employee)

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve employee from the database.",
        )


@router.post("", status_code=201)
def create_employee(employee: EmployeeCreate):
    data = employee.model_dump(mode="json")
    columns = list(data.keys())
    column_sql = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = (
        f"INSERT INTO employees ({column_sql}) "
        f"VALUES ({placeholders}) "
        "RETURNING *"
    )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    [data[column] for column in columns],
                )
                row = cursor.fetchone()
                result_columns = [
                    item.name for item in cursor.description
                ]
                result = dict(zip(result_columns, row))

        return serialize_employee(result)

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Employee ID or work email already exists.",
        )
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to create employee in the database.",
        )


@router.put("/{employee_id}")
def update_employee(employee_id: str, employee: EmployeeUpdate):
    updates = employee.model_dump(
        exclude_unset=True,
        mode="json",
    )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update.",
        )

    set_clause = ", ".join(
        f"{column} = %s" for column in updates
    )

    query = (
        f"UPDATE employees SET {set_clause} "
        "WHERE employee_id = %s "
        "RETURNING *"
    )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    [*updates.values(), employee_id],
                )
                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Employee not found.",
                    )

                columns = [item.name for item in cursor.description]
                result = dict(zip(columns, row))

        return serialize_employee(result)

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Work email already belongs to another employee.",
        )
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to update employee in the database.",
        )


@router.delete("/{employee_id}")
def delete_employee(employee_id: str):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM employees
                    WHERE employee_id = %s
                    RETURNING employee_id
                    """,
                    (employee_id,),
                )
                deleted = cursor.fetchone()

                if deleted is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Employee not found.",
                    )

        return {
            "message": "Employee deleted successfully.",
            "employee_id": deleted[0],
        }

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to delete employee from the database.",
        )