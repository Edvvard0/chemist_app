from pydantic import BaseModel


class SWriteOff(BaseModel):
    medicine_id: int
    warehouses_id: int
    reason: str

from enum import Enum
from typing import List

class OrderStatus(str, Enum):
    SUFFICIENT = "sufficient"  # Достаточно (≥ 100)
    NEEDS_ORDER = "needs_order"  # Нужно заказать (< 50)
    URGENT = "urgent"  # Срочно заказать (< 20)

class MedicineStock(BaseModel):
    medicine_name: str
    quantity: int
    order_status: OrderStatus

class WarehouseStockReport(BaseModel):
    warehouse_name: str
    warehouse_address: str
    medicines: List[MedicineStock]

class StockReport(BaseModel):
    warehouses: List[WarehouseStockReport]