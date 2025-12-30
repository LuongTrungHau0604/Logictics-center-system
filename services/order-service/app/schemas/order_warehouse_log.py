# app/schemas/order_warehouse_log.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OrderWarehouseLogBase(BaseModel):
    """Base schema cho warehouse log"""
    order_id: str
    warehouse_id: str
    action: str = Field(..., description="CHECK_IN, CHECK_OUT, PROCESSING, etc.")
    note: Optional[str] = None

class OrderWarehouseLogCreate(OrderWarehouseLogBase):
    """Schema khi tạo log mới (từ barcode scan)"""
    scanned_by: Optional[str] = None

class OrderWarehouseLogOut(OrderWarehouseLogBase):
    """Schema trả về cho client"""
    log_id: str
    scanned_by: Optional[str]
    scanned_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class BarcodeScanRequest(BaseModel):
    """Schema cho request khi scan barcode"""
    code_value: str = Field(..., description="Mã barcode được quét")
    warehouse_id: str = Field(..., description="ID kho hiện tại")
    action: str = Field(default="CHECK_IN", description="Hành động: CHECK_IN, CHECK_OUT, etc.")
    note: Optional[str] = Field(None, description="Ghi chú thêm")

class BarcodeScanResponse(BaseModel):
    """Schema response sau khi scan thành công"""
    success: bool
    message: str
    order_id: str
    order_code: str
    current_warehouse: str
    action: str
    log: OrderWarehouseLogOut
