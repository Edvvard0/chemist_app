from datetime import date

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class WarehouseMedicine(Base):
    warehouses_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    medicines_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"))
    quantity: Mapped[int]
    delivery_date: Mapped[date] = mapped_column(server_default=func.current_date(), default=func.current_date())

    warehouses = relationship("Warehouse", back_populates="wm")
    medicines = relationship("Medicine", back_populates="wm")

    issuance = relationship("MedicineIssuance", back_populates="wm")