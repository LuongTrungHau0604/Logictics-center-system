# app/schemas/barcode.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field

# --- SCHEMA ---
# Schema dùng khi tạo mới barcode
class BarcodeCreate(BaseModel):
    barcode_id: str
    code_value: str
    
class ScanActionType(str, Enum):
    PICKUP_CONFIRM = "PICKUP_CONFIRM"       # Shipper lấy hàng từ SME
    WAREHOUSE_IN = "WAREHOUSE_IN"           # Nhập kho (Hub/Vệ tinh)
    WAREHOUSE_OUT = "WAREHOUSE_OUT"         # Xuất kho (Lên xe tải)
    DELIVERY_START = "DELIVERY_START"       # Shipper nhận hàng đi giao khách
    DELIVERY_COMPLETE = "DELIVERY_COMPLETE" # Giao thành công cho khách

# --- REQUEST SCHEMA ---
class BarcodeScanRequest(BaseModel):
    code_value: str = Field(..., description="Mã barcode trên đơn hàng")
    action: ScanActionType = Field(..., description="Hành động quét")
    
    # Optional fields
    warehouse_id: Optional[str] = Field(None, description="Bắt buộc nếu là nhân viên kho quét")
    lat: Optional[float] = None # Tọa độ GPS khi quét
    lng: Optional[float] = None
    note: Optional[str] = None

# --- RESPONSE SCHEMA ---
class BarcodeOut(BaseModel):
    barcode_id: str
    code_value: str
    generated_at: datetime
    image_url: Optional[str] = None # Nếu có

    class Config:
        from_attributes = True

class BarcodeScanResponse(BaseModel):
    success: bool
    message: str
    order_id: str
    order_code: str
    action: str
    current_warehouse: Optional[str] = None
    log_id: Optional[str] = None

# --- THÊM CLASS NÀY VÀO ---
# Schema dùng khi cập nhật barcode (nếu cần)
class BarcodeUpdate(BaseModel):
    code_value: Optional[str] = None

class BarcodeImageResponse(BaseModel):
    order_id: str
    code_value: str
    image: str  # Đây là trường quan trọng chứa Base64
