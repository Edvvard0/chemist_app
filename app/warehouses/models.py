from datetime import date

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Warehouse(Base):
    name: Mapped[str]
    address: Mapped[str]

    wm = relationship("WarehouseMedicine", back_populates="warehouses")
