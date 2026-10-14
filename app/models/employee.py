from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Employee(Base):
    __tablename__ = "employees"

    __table_args__ = (
        Index("idx_employees_manager_id", "manager_id"),
        Index("idx_employees_full_name", "full_name"),
        CheckConstraint(
            "prior_experience_years >= 0",
            name="prior_experience",
        ),
        CheckConstraint(
            "career_gap_months >= 0",
            name="career_gap",
        ),
        CheckConstraint(
            "notice_period_days IS NULL OR notice_period_days >= 0",
            name="notice_period",
        ),
        CheckConstraint(
            "pf_applicable IS NULL OR pf_applicable IN ('Y', 'N')",
            name="pf_applicable",
        ),
        CheckConstraint(
            "esi_applicable IS NULL OR esi_applicable IN ('Y', 'N')",
            name="esi_applicable",
        ),
        CheckConstraint(
            "exit_date IS NULL OR hire_date IS NULL OR exit_date >= hire_date",
            name="exit_date_after_hire_date",
        ),
        Index("idx_employees_department_id", "department_id"),
        Index("idx_employees_employment_status", "employment_status"),
    )

    employee_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(201), nullable=False)
    work_email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )

    gender: Mapped[str | None] = mapped_column(String(30))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    hire_date: Mapped[date | None] = mapped_column(Date)
    exit_date: Mapped[date | None] = mapped_column(Date)
    employment_status: Mapped[str] = mapped_column(String(30), nullable=False)
    employment_type: Mapped[str | None] = mapped_column(String(30))

    # Foreign keys will be introduced after master data and manager
    # references have been validated in the existing database.
    department_id: Mapped[str | None] = mapped_column(String(20))
    role_id: Mapped[str | None] = mapped_column(String(20))
    manager_id: Mapped[str | None] = mapped_column(String(20))

    work_location: Mapped[str | None] = mapped_column(String(100))
    work_mode: Mapped[str | None] = mapped_column(String(30))
    highest_education: Mapped[str | None] = mapped_column(String(150))

    prior_experience_years: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    career_gap_months: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    commute_distance_km: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    pf_applicable: Mapped[str | None] = mapped_column(CHAR(1))
    esi_applicable: Mapped[str | None] = mapped_column(CHAR(1))
    notice_period_days: Mapped[int | None] = mapped_column(Integer)
    resignation_date: Mapped[date | None] = mapped_column(Date)
    exit_type: Mapped[str | None] = mapped_column(String(50))
    exit_reason: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        server_default=text("TRUE"),
    )

    department: Mapped["Department | None"] = relationship(
        back_populates="employees",
        foreign_keys="Employee.department_id",
        primaryjoin="Employee.department_id == Department.department_id",
        viewonly=True,
    )
    role: Mapped["Role | None"] = relationship(
        back_populates="employees",
        foreign_keys="Employee.role_id",
        primaryjoin="Employee.role_id == Role.role_id",
        viewonly=True,
    )
    manager: Mapped["Employee | None"] = relationship(
        remote_side="Employee.employee_id",
        back_populates="direct_reports",
        foreign_keys="Employee.manager_id",
        primaryjoin="Employee.manager_id == Employee.employee_id",
        viewonly=True,
    )
    direct_reports: Mapped[list["Employee"]] = relationship(
        back_populates="manager",
        foreign_keys="Employee.manager_id",
        primaryjoin="Employee.employee_id == Employee.manager_id",
        viewonly=True,
    )
