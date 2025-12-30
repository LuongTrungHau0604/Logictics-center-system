# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import ConfigDict
import enum
class WarehouseType(str, enum.Enum):
    HUB = "HUB"
    SATELLITE = "SATELLITE"
    LOCAL_DEPOT = "LOCAL_DEPOT"

class WarehouseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

class AreaType(str, enum.Enum):
    CITY = "CITY"
    DISTRICT = "DISTRICT"
    REGION = "REGION"
    CUSTOM = "CUSTOM"

class AreaStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Area schemas
class AreaBase(BaseModel):
    # SỬA LỖI TẠI ĐÂY: Đổi 'area_name' thành 'name'
    name: str 
    description: Optional[str] = None
    type: Optional[AreaType] = AreaType.CUSTOM
    status: AreaStatus = AreaStatus.ACTIVE
    radius_km: Optional[Decimal] = None
    
    # Thêm các trường tọa độ tâm mới (khớp với model mới của bạn)
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None

class AreaCreate(AreaBase):
    area_id: str

class AreaUpdate(AreaBase):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AreaType] = None
    status: Optional[AreaStatus] = None
    radius_km: Optional[Decimal] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None

class Area(AreaBase):
    model_config = ConfigDict(from_attributes=True)
    
    area_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# SME schemas
class SMEBase(BaseModel):
    business_name: str
    tax_code: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: str = "active"


class SMECreate(SMEBase):
    sme_id: str
    user_id: str


class SMEUpdate(BaseModel):
    business_name: Optional[str] = None
    tax_code: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: Optional[str] = None


class SMEUpdateCoordinates(BaseModel):
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class SME(SMEBase):
    sme_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True



# --- Warehouse Schemas ---

class WarehouseBase(BaseModel):
    name: str
    address: str
    type: Optional[WarehouseType] = None
    capacity_limit: int = 0
    current_load: int = 0
    area_id: Optional[str] = None
    
    # ĐÃ XÓA: coordinates: Coordinates 
    # (Theo yêu cầu của bạn để tránh rắc rối validation)
    
    status: WarehouseStatus = WarehouseStatus.ACTIVE
    contact_phone: Optional[str] = None

class WarehouseCreate(WarehouseBase):
    pass
    

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    type: Optional[WarehouseType] = None
    capacity_limit: Optional[int] = None
    current_load: Optional[int] = None
    area_id: Optional[str] = None
    
    # ĐÃ XÓA: coordinates 
    
    status: Optional[WarehouseStatus] = None
    contact_phone: Optional[str] = None

class Warehouse(WarehouseBase):
    # Config cho Pydantic v2 để map từ SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)
    
    warehouse_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # --- SỬA LỖI QUAN TRỌNG ---
    # Phải để Optional và mặc định là None để chấp nhận giá trị NULL từ DB
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Thêm quan hệ (nếu cần)
    area: Optional[Area] = None
    
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

# Order schemas
class OrderBase(BaseModel):
    order_code: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    receiver_latitude: Decimal
    receiver_longitude: Decimal


class OrderCreate(OrderBase):
    sme_id: str


class OrderUpdate(BaseModel):
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    receiver_latitude: Optional[Decimal] = None
    receiver_longitude: Optional[Decimal] = None
    status: Optional[str] = None


class OrderUpdateByAI(BaseModel):
    pickup_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    status: Optional[str] = None


class Order(OrderBase):
    order_id: str
    sme_id: str
    pickup_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    status: str
    barcode_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    sme: Optional[SME] = None
    pickup_warehouse: Optional[Warehouse] = None
    destination_warehouse: Optional[Warehouse] = None

    class Config:
        from_attributes = True


# OrderRoute schemas
class OrderRouteBase(BaseModel):
    sequence_order: int
    estimated_time_minutes: Optional[int] = None
    status: str = "PENDING"


class OrderRouteCreate(OrderRouteBase):
    order_id: str
    from_warehouse_id: Optional[str] = None
    to_warehouse_id: Optional[str] = None


class OrderRouteUpdate(BaseModel):
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OrderRoute(OrderRouteBase):
    route_id: str
    order_id: str
    from_warehouse_id: Optional[str] = None
    to_warehouse_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    from_warehouse: Optional[Warehouse] = None
    to_warehouse: Optional[Warehouse] = None

    class Config:
        from_attributes = True
        

