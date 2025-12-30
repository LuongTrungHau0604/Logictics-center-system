from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
from decimal import Decimal

# Enum cho loại xe
class VehicleType(str, Enum):
    MOTORBIKE = "MOTORBIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"
    BICYCLE = "BICYCLE"

# Enum cho trạng thái hoạt động
class ShipperStatus(str, Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    DELIVERING = "DELIVERING"

# Schema cơ sở
class ShipperBase(BaseModel):
    vehicle_type: Optional[VehicleType] = VehicleType.MOTORBIKE
    status: Optional[ShipperStatus] = ShipperStatus.ONLINE
    area_id: Optional[str] = None
    rating: Optional[float] = Field(5.0, ge=0, le=5)

# Schema dùng khi tạo mới (thường được gọi từ EmployeeService)
class ShipperCreate(ShipperBase):
    shipper_id: str
    employee_id: str

# Schema dùng khi cập nhật (VD: đổi trạng thái, đổi xe)
class ShipperUpdate(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    status: Optional[ShipperStatus] = None
    area_id: Optional[str] = None
    rating: Optional[float] = None

class ShipperOut(ShipperBase):
    shipper_id: str
    employee_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Có thể join thêm thông tin Employee để hiển thị tên
    full_name: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


    
class ShipperLocationUpdate(BaseModel):
    current_lat: float
    current_lon: float

# Schema cập nhật Token
class ShipperTokenUpdate(BaseModel):
    fcm_token: str

# Schema Output cho Profile (đã có, nhắc lại để đảm bảo đủ field)
class ShipperProfileOut(BaseModel):
    shipper_id: str
    employee_id: str
    vehicle_type: str
    status: str
    area_id: Optional[str] = None
    rating: float
    full_name: Optional[str] = None # Lấy từ bảng Employee -> User
    phone: Optional[str] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    
    class Config:
        from_attributes = True # Pydantic v2 dùng from_attributes thay vì orm_mode