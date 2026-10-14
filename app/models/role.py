
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    department_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("departments.department_id"),
        nullable=False,
        index=True,
    )
    role_title: Mapped[str] = mapped_column(String(150), nullable=False)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(100), nullable=True)

    band_min_annual: Mapped[float | None] = mapped_column(Numeric(12, 2))
    band_mid_annual: Mapped[float | None] = mapped_column(Numeric(12, 2))
    band_max_annual: Mapped[float | None] = mapped_column(Numeric(12, 2))

    overtime_eligible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    band_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    department: Mapped["Department"] = relationship(back_populates="roles")
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="role",
        foreign_keys="Employee.role_id",
    )
