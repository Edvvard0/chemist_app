from datetime import date

from pydantic import BaseModel, field_validator


class SWarehouseMedicine(BaseModel):
    id: int
    warehouses_id: int
    medicines_id: int
    quantity: int
    delivery_date: date


class SWarehouseMedicineAdd(BaseModel):
    warehouses_id: int
    medicines_id: int
    quantity: int



class TransferCreate(BaseModel):
    medicine_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int

    @field_validator("quantity")
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Количество должно быть больше нуля")
        return v
