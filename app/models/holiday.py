
from datetime import date

from sqlalchemy import Boolean, Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Holiday(Base):
    __tablename__ = "holidays"

    holiday_date: Mapped[date] = mapped_column(Date, primary_key=True)
    holiday_name: Mapped[str] = mapped_column(String(150), nullable=False)
    holiday_type: Mapped[str | None] = mapped_column(String(50))
    weekday: Mapped[str | None] = mapped_column(String(15))
    falls_on_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    calendar_note: Mapped[str | None] = mapped_column(Text)
