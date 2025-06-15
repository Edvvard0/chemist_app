from datetime import date

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy_utils import ChoiceType

from app.database import Base


class MedicineIssuance(Base):
    STATUS_TYPE = {
    "pending": "ожидает",
    "accepted": "принята",
    "rejected": "отклонена",
    }

    wm_id: Mapped[int] = mapped_column(ForeignKey("warehousemedicines.id"))

    quantity: Mapped[int]
    issuance_date: Mapped[date] = mapped_column(server_default=func.current_date(), default=func.current_date())
    status = mapped_column(ChoiceType(STATUS_TYPE))

    wm = relationship("WarehouseMedicine", back_populates="issuance")
