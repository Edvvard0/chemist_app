from datetime import date

from pydantic import BaseModel


class SMedicine(BaseModel):
    id: int
    name: str
    description: str
    expiration_date: date


class SMedicineAdd(BaseModel):
    name: str
    description: str
    expiration_date: date
