from datetime import date
from typing import Literal

from pydantic import BaseModel, Field



class SMedicineIssuance(BaseModel):
    wm_id: int
    quantity: int
    issuance_date: date
    status: Literal["pending", "accepted", "rejected"] = Field(default="pending")


class SMedicineIssuanceStatus(BaseModel):
    med_issuance_id: int
    status: Literal["pending", "accepted", "rejected"]