# app/schemas/order.py

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

# --- Schema cơ sở ---
# Chứa các trường chung mà client cung cấp
class OrderBase(BaseModel):
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    weight: float  # kg
    dimensions: Optional[str] = None  # "20x15x10 cm"
    note: Optional[str] = None  # Combined package type + special instructions

    @validator('receiver_name')
    def validate_receiver_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Receiver name is required')
        if len(v.strip()) < 2:
            raise ValueError('Receiver name must be at least 2 characters')
        return v.strip()
    
    @validator('receiver_phone')
    def validate_receiver_phone(cls, v):
        if not v or not v.strip():
            raise ValueError('Receiver phone is required')
        # Basic phone validation
        cleaned_phone = ''.join(c for c in v if c.isdigit() or c in '+()-')
        if len(cleaned_phone) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v.strip()
    
    @validator('receiver_address')
    def validate_receiver_address(cls, v):
        if not v or not v.strip():
            raise ValueError('Receiver address is required')
        if len(v.strip()) < 10:
            raise ValueError('Address must be at least 10 characters')
        return v.strip()
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is None or v <= 0:
            raise ValueError('Weight must be positive')
        if v > 1000:
            raise ValueError('Weight cannot exceed 1000kg')
        return round(v, 2)
    
    class Config:
        schema_extra = {
            "example": {
                "receiver_name": "Nguyen Van A",
                "receiver_phone": "0123456789",
                "receiver_address": "123 Nguyen Hue, District 1, Ho Chi Minh City",
                "weight": 2.5,
                "dimensions": "30x20x15 cm",
                "note": "Package Type: Electronics; Instructions: Handle with care, call before delivery"
            }
        }

# --- Schema Input (Đầu vào) ---

# Dữ liệu client GỬI LÊN để tạo đơn hàng
class OrderCreate(OrderBase):
    """
    Schema này chỉ chứa thông tin client cần cung cấp.
    - 'sme_id' sẽ được lấy từ 'current_user' trong service.
    - 'lat/long' sẽ được geocode từ 'receiver_address' trong service.
    - 'order_id', 'order_code', 'barcode_id', 'status' sẽ được tạo tự động.
    """
    pass
    
# Dữ liệu client GỬI LÊN để cập nhật đơn hàng
class OrderUpdate(BaseModel):
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    weight: Optional[float] = None
    note: Optional[str] = None
    dimensions: Optional[str] = None
# --- Schema Output (Đầu ra) ---

# Dữ liệu API TRẢ VỀ cho client (an toàn, đầy đủ)
class OrderOut(OrderBase):
    order_id: str
    order_code: str
    sme_id: str
    barcode_id: str
    
    # Thêm các trường đã được geocode
    receiver_latitude: float
    receiver_longitude: float
    receiver_name: str
    # Thêm các trường trạng thái
    status: str # Pydantic sẽ tự chuyển Enum thành string
    area_id: Optional[str] = None
    active_leg_id: Optional[int] = None
    
    # Thêm dấu thời gian
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True # (hoặc orm_mode = True cho Pydantic v1)
        schema_extra = {
            "example": {
                "order_id": "550e8400-e29b-41d4-a716-446655440000",
                "order_code": "ORDER-A1B2C3D4",
                "sme_id": "SME_12345",
                "barcode_id": "BC-E5F6G7H8I9J0",
                "receiver_name": "Nguyen Van A",
                "receiver_phone": "0123456789",
                "receiver_address": "123 Nguyen Hue, District 1, Ho Chi Minh City",
                "receiver_latitude": 10.7769,
                "receiver_longitude": 106.7009,
                "weight": 2.5,
                "dimensions": "30x20x15 cm",
                "note": "Package Type: Electronics; Handle with care",
                "status": "PENDING",
                "area_id": None,
                "active_leg_id": None,
                "created_at": "2024-12-11T10:30:00Z",
                "updated_at": "2024-12-11T10:30:00Z"
            }
        }