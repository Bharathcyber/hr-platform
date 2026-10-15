
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import psycopg
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.services import employees as employee_service
from app.services.employees import DEMO_TODAY


router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


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
    prior_experience_years: Decimal = Field(default=Decimal("0"), ge=0)
    career_gap_months: int = Field(default=0, ge=0)
    commute_distance_km: Optional[Decimal] = None
    pf_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    esi_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    notice_period_days: Optional[int] = Field(default=None, ge=0)
    resignation_date: Optional[date] = None
    exit_type: Optional[str] = None
    exit_reason: Optional[str] = None

    @field_validator("first_name", "last_name", "full_name", "employment_status")
    @classmethod
    def reject_blank_text(cls, value):
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value.strip()

    @field_validator("hire_date", "exit_date")
    @classmethod
    def validate_dates(cls, value):
        return value


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
    prior_experience_years: Optional[Decimal] = Field(default=None, ge=0)
    career_gap_months: Optional[int] = Field(default=None, ge=0)
    commute_distance_km: Optional[Decimal] = None
    pf_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    esi_applicable: Optional[str] = Field(default=None, pattern="^[YN]$")
    notice_period_days: Optional[int] = Field(default=None, ge=0)
    resignation_date: Optional[date] = None
    exit_type: Optional[str] = None
    exit_reason: Optional[str] = None

    @field_validator("first_name", "last_name", "full_name", "employment_status")
    @classmethod
    def reject_blank_text(cls, value):
        if value is not None and not value.strip():
            raise ValueError("This field cannot be blank.")
        return value.strip() if value is not None else value


def serialize_employee(row):
    result = dict(row)

    for key, value in result.items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)

    return result


def get_connection():
    from app.core.config import settings

    database_url = settings.database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
    return psycopg.connect(database_url)


@router.get("")
def list_employees(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
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
    return employee_service.list_employees(
        limit=limit,
        offset=offset,
        department_id=department_id,
        role_id=role_id,
        employment_status=employment_status,
        work_location=work_location,
        work_mode=work_mode,
        manager_id=manager_id,
        hire_date_from=hire_date_from,
        hire_date_to=hire_date_to,
        q=q,
    )


@router.get("/team/{manager_id}")
def get_team(manager_id: str):
    return employee_service.get_direct_reports(manager_id)


@router.get("/{employee_id}")
def get_employee(employee_id: str):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM employees
                    WHERE employee_id = %s AND is_active = TRUE
                    """,
                    (employee_id,),
                )
                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Active employee not found.",
                    )

                columns = [item.name for item in cursor.description]

        return serialize_employee(dict(zip(columns, row)))

    except HTTPException:
        raise
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve employee.",
        ) from exc


@router.post("", status_code=201)
def create_employee(employee: EmployeeCreate):
    employee_service.validate_employee_dates(
        employee.hire_date,
        employee.exit_date,
    )

    data = employee.model_dump(mode="json")
    columns = list(data)

    query = (
        f"INSERT INTO employees ({', '.join(columns)}) "
        f"VALUES ({', '.join(['%s'] * len(columns))}) RETURNING *"
    )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, [data[column] for column in columns])
                row = cursor.fetchone()
                result = dict(
                    zip([item.name for item in cursor.description], row)
                )

        return serialize_employee(result)

    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Employee ID or work email already exists.",
        ) from exc
    except psycopg.errors.ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=422,
            detail="Department, role, or manager reference does not exist.",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to create employee.",
        ) from exc


@router.put("/{employee_id}")
def update_employee(employee_id: str, employee: EmployeeUpdate):
    updates = employee.model_dump(exclude_unset=True, mode="json")

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update.",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT hire_date, exit_date
                    FROM employees
                    WHERE employee_id = %s AND is_active = TRUE
                    """,
                    (employee_id,),
                )
                existing = cursor.fetchone()

                if existing is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Active employee not found.",
                    )

                hire_date = updates.get("hire_date", existing[0])
                exit_date = updates.get("exit_date", existing[1])

                if isinstance(hire_date, str):
                    hire_date = date.fromisoformat(hire_date)
                if isinstance(exit_date, str):
                    exit_date = date.fromisoformat(exit_date)

                employee_service.validate_employee_dates(
                    hire_date,
                    exit_date,
                )

                set_clause = ", ".join(
                    f"{column} = %s" for column in updates
                )

                cursor.execute(
                    f"""
                    UPDATE employees
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE employee_id = %s AND is_active = TRUE
                    RETURNING *
                    """,
                    [*updates.values(), employee_id],
                )

                row = cursor.fetchone()
                result = dict(
                    zip([item.name for item in cursor.description], row)
                )

        return serialize_employee(result)

    except HTTPException:
        raise
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Work email already belongs to another employee.",
        ) from exc
    except psycopg.errors.ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=422,
            detail="Department, role, or manager reference does not exist.",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to update employee.",
        ) from exc


@router.delete("/{employee_id}")
def delete_employee(employee_id: str):
    return employee_service.soft_delete_employee(employee_id)