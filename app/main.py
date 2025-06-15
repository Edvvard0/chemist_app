import logging

import uvicorn
from fastapi import FastAPI

from app.config import settings
from app.users.router import router as user_router
from app.pages.router import router as pages_router
from app.warehouses.router import router as warehouses_router
from app.medicines.router import router as medicine_router
from app.warehouse_medicine.router import router as wm_router
from app.core.router import router as core_router
from app.medicine_issuance.router import router as med_issuance_router


app = FastAPI()
app.include_router(user_router)
app.include_router(pages_router)
app.include_router(warehouses_router)
app.include_router(medicine_router)
app.include_router(wm_router)
app.include_router(core_router)
app.include_router(med_issuance_router)

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT)

