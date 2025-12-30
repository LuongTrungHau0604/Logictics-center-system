# app/schemas/scan.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ScanRequest(BaseModel):
    code_value: str          # Mã barcode quét được
    scanner_lat: Optional[Decimal] = None # Tọa độ người quét
    scanner_long: Optional[Decimal] = None
    current_warehouse_id: Optional[str] = None # Nếu là nhân viên kho quét