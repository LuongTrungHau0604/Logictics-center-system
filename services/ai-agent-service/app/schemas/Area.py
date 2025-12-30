from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class AreaType(str, Enum):
    CITY = "CITY"
    DISTRICT = "DISTRICT"
    REGION = "REGION"
    CUSTOM = "CUSTOM"

class AreaStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

# Schema cơ sở
class AreaBase(BaseModel):
    name: str
    type: AreaType = AreaType.CUSTOM
    status: AreaStatus = AreaStatus.ACTIVE
    description: Optional[str] = None
    
    # SỬA LỖI TẠI ĐÂY:
    # Chuyển sang Optional[float] và mặc định là None
    radius_km: Optional[float] = Field(None, gt=0) 
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)

# Schema khi tạo mới
class AreaCreate(AreaBase):
    # Nếu khi tạo bắt buộc phải có tọa độ thì override lại ở đây, 
    # còn nếu không bắt buộc thì giữ nguyên như AreaBase
    pass

# Schema khi cập nhật
class AreaUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AreaType] = None
    status: Optional[AreaStatus] = None
    description: Optional[str] = None
    radius_km: Optional[float] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None

# Schema trả về client
class Area(AreaBase):
    area_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True