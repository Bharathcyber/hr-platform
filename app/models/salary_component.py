
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SalaryComponent(Base):
    __tablename__ = "salary_components"

    component_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    component_name: Mapped[str] = mapped_column(String(100), nullable=False)
    component_type: Mapped[str] = mapped_column(String(30), nullable=False)
    taxable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    calculation_rule: Mapped[str | None] = mapped_column(Text)
    is_fixed: Mapped[bool] = mapped_column(Boolean, nullable=False)
