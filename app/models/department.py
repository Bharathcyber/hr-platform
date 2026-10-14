
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(
        String(10), primary_key=True
    )
    department_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    cost_center: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department",
        foreign_keys="Employee.department_id",
    )
    roles: Mapped[list["Role"]] = relationship(
        back_populates="department"
    )
