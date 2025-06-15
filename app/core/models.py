from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WriteOffMed(Base):
    medicines_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    reason: Mapped[str]
    write_off_date: Mapped[date]