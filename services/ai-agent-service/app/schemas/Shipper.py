from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.schemas.Area import Area
from pydantic import BaseModel, Field, ConfigDict
from app.models import VehicleType, ShipperStatus

class ShipperBase(BaseModel):
    name: str
    phone: str = Field(..., pattern=r"^\+?\d{9,15}$") # Regex SĐT đơn giản
    employee_id: Optional[str] = None
    vehicle_type: VehicleType = VehicleType.MOTORBIKE
    status: ShipperStatus = ShipperStatus.OFFLINE
    area_id: Optional[str] = None
    rating: Optional[float] = Field(default=5.0, ge=0, le=5)

class ShipperCreate(ShipperBase):
    shipper_id: str

class ShipperUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?\d{9,15}$")
    employee_id: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    status: Optional[ShipperStatus] = None
    area_id: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)

class Shipper(ShipperBase):
    model_config = ConfigDict(from_attributes=True)
    
    shipper_id: str
    created_at: datetime
    updated_at: datetime
    
    # Tự động đọc từ 'column_property'
    latitude: float
    longitude: float
    
    # Quan hệ
    area: Optional[Area] = None
    # employee: Optional[Employee] = None # (Tùy chọn)
    

class ShipperProfileOut(BaseModel):
    # From Employees Table
    full_name: str
    email: str
    phone: str
    warehouse_id: Optional[str] = None
    
    # From Shippers Table
    shipper_id: str
    vehicle_type: str
    status: str
    rating: float
    area_id: Optional[str] = None
    
    # Calculated (Optional placeholder for now)
    total_deliveries: int = 0 
    success_rate: float = 0.0