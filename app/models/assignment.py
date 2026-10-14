
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EmployeeAssignment(Base):
    __tablename__ = "employee_assignments"

    __table_args__ = (
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_dates",
        ),
    )

    assignment_id: Mapped[str] = mapped_column(String(20), primary_key=True)

    employee_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True,
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    effective_to: Mapped[datetime | None] = mapped_column(DateTime)

    department_id: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("departments.department_id"),
    )
    role_id: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("roles.role_id"),
    )
    job_level: Mapped[int | None] = mapped_column(Integer)

    manager_id: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("employees.employee_id"),
    )

    change_reason: Mapped[str | None] = mapped_column(String(100))

    employee: Mapped["Employee"] = relationship(
        foreign_keys=[employee_id],
    )
