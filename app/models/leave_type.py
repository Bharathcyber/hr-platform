
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LeaveType(Base):
    __tablename__ = "leave_types"

    leave_type_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    leave_type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pay_type: Mapped[str] = mapped_column(String(30), nullable=False)
    annual_quota_days: Mapped[int] = mapped_column(Integer, nullable=False)
    prorated_for_joiners: Mapped[bool] = mapped_column(Boolean, nullable=False)
    carry_forward_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    max_carry_forward_days: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_note: Mapped[str | None] = mapped_column(Text)
