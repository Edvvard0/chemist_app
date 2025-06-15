from pydantic import BaseModel


class SWarehouse(BaseModel):
    id: int
    name: str
    address: str


class SWarehouseAdd(BaseModel):
    name: str
    address: str
