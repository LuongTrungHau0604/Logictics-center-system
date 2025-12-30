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
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

# Schema dùng khi tạo mới
class WarehouseCreate(WarehouseBase):
    # warehouse_id có thể được sinh tự động hoặc truyền vào
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
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

# Schema trả về cho Client (Output)
class WarehouseOut(WarehouseBase):
    warehouse_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True