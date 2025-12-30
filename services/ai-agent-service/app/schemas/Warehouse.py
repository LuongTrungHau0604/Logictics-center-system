from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
from decimal import Decimal

# Enum cho loại kho
class WarehouseType(str, Enum):
    HUB = "HUB"
    SATELLITE = "SATELLITE"
    LOCAL_DEPOT = "LOCAL_DEPOT"

# Enum cho trạng thái kho
class WarehouseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

# Schema cơ sở (các trường chung)
class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    address: Optional[str] = None
    type: Optional[WarehouseType] = WarehouseType.HUB
    capacity_limit: int = Field(..., gt=0)
    current_load: Optional[int] = 0
    area_id: Optional[str] = None
    status: Optional[WarehouseStatus] = WarehouseStatus.ACTIVE
    contact_phone: Optional[str] = None
    
    # ✅ Đảm bảo 2 trường này tồn tại trong Base
    # Dùng float hoặc Decimal tùy cấu hình DB, ở đây dùng float cho đơn giản với Pydantic
    latitude: Optional[float] = None 
    longitude: Optional[float] = None

# Schema dùng khi tạo mới
class WarehouseCreate(WarehouseBase):
    """
    Schema dùng cho việc tạo mới Warehouse.
    Kế thừa toàn bộ các trường từ WarehouseBase.
    """
    pass

# Schema dùng khi cập nhật
class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    type: Optional[WarehouseType] = None
    capacity_limit: Optional[int] = None
    current_load: Optional[int] = None
    area_id: Optional[str] = None
    status: Optional[WarehouseStatus] = None
    contact_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# Schema trả về cho Client (Output)
class Warehouse(WarehouseBase): # Đổi tên từ WarehouseOut thành Warehouse để khớp với code khác nếu cần
    warehouse_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alias WarehouseOut để tương thích ngược nếu code cũ đang dùng

    
class WarehouseInfo(BaseModel):
    """
    Schema Pydantic chuyên biệt để trả về thông tin kho hàng
    từ Logistics Agent.
    """
    warehouse_id: str
    name: str
    address: str
    
    # Cũng cần sửa ở đây để đồng bộ
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    type: str 
    status: str 
    
    capacity_limit: int
    current_load: int
    available_capacity: int
    
    distance_km: float

    class Config:
        json_schema_extra = {
            "example": {
                "warehouse_id": "wh-001",
                "name": "Kho Trung Tâm Q1",
                "address": "123 Đường ABC, Phường X, Quận 1, TPHCM",
                "latitude": 10.7769,
                "longitude": 106.7009,
                "type": "HUB",
                "status": "ACTIVE",
                "capacity_limit": 1000,
                "current_load": 400,
                "available_capacity": 600,
                "distance_km": 3.45
            }
        }
        
WarehouseOut = Warehouse