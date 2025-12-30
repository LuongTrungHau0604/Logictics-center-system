from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Coordinates(BaseModel):
    """Model tọa độ cơ bản"""
    latitude: float = Field(..., ge=-90, le=90, description="Vĩ độ")
    longitude: float = Field(..., ge=-180, le=180, description="Kinh độ")


class RouteRequest(BaseModel):
    """Model đầu vào cho API tính toán tuyến đường"""
    business_address: str = Field(..., min_length=1, description="Địa chỉ doanh nghiệp/SME")
    receiver_address: str = Field(..., min_length=1, description="Địa chỉ người nhận")
    required_capacity: int = Field(..., gt=0, description="Sức chứa yêu cầu")

class WaypointType(str, Enum):
    """Enum cho loại waypoint"""
    BUSINESS = "business"
    WAREHOUSE = "warehouse"
    DESTINATION = "destination"

class Waypoint(BaseModel):
    """Một điểm dừng trên tuyến đường"""
    description: str = Field(..., description="Mô tả điểm dừng")
    waypoint_type: WaypointType = Field(..., description="Loại waypoint")
    coordinates: Coordinates = Field(..., description="Tọa độ của waypoint")

class RouteStatus(str, Enum):
    """Enum cho trạng thái route"""
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    ERROR = "ERROR"

class RouteResponse(BaseModel):
    """Model đầu ra cho API tính toán tuyến đường"""
    total_distance_km: float = Field(..., description="Tổng khoảng cách (km)")
    status: RouteStatus = Field(..., description="Trạng thái tuyến đường")
    waypoints: List[Waypoint] = Field(default=[], description="Danh sách điểm dừng")
    message: Optional[str] = Field(None, description="Thông báo chi tiết")

# Additional models cho LogisticsAgent
class WarehouseInfo(BaseModel):
    """Thông tin kho hàng"""
    warehouse_id: str
    name: str
    coordinates: Coordinates
    available_capacity: int

class GeocodingResult(BaseModel):
    """Kết quả geocoding"""
    address: str
    coordinates: Coordinates
    success: bool
    
class AgentProcessingResult(BaseModel):
    """Kết quả xử lý của Agent"""
    business_geocoding: GeocodingResult
    receiver_geocoding: GeocodingResult
    nearest_warehouse: Optional[WarehouseInfo]
    capacity_check_passed: bool
    route: RouteResponse