from datetime import date

from sqlalchemy.orm import Mapped, relationship

from app.database import Base


class Medicine(Base):
    name: Mapped[str]
    description: Mapped[str]
    expiration_date: Mapped[date]

    wm = relationship("WarehouseMedicine", back_populates="medicines")
