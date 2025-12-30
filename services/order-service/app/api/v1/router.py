# api/v1/router.py
from fastapi import APIRouter
from api.v1.endpoints import order, barcode

api_router = APIRouter()
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(barcode.router, prefix="/barcodes", tags=["barcode"])
