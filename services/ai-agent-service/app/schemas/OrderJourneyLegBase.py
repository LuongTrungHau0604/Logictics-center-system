from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from app.models import WarehouseType, WarehouseStatus
from pydantic import BaseModel, Field, ConfigDict
from app.models import LegType, LegStatus

class LegDetail(BaseModel):
    sequence: int
    leg_type: str
    status: str
    shipper_id: Optional[str]
    estimated_distance: Optional[float]

# Schema tổng hợp cho một dòng đơn hàng trên bảng Dispatch
class DispatchOrderSummary(BaseModel):
    order_id: str
    order_code: str  # Cần join bảng Orders để lấy
    current_status: str # Trạng thái chung của đơn hàng
    pickup_location: str # Lấy từ origin_sme_id hoặc warehouse đầu tiên
    delivery_location: str # Lấy từ destination warehouse cuối cùng hoặc receiver
    total_distance: float
    assigned_shipper: Optional[str] # Shipper của chặng hiện tại
    priority: str = "normal" # Mặc định hoặc lấy từ Order
    legs: List[LegDetail] # Danh sách các chặng để debug hoặc hiển thị chi tiết
    
class OrderJourneyLegBase(BaseModel):
    sequence: int
    leg_type: LegType
    status: LegStatus = LegStatus.PENDING
    origin_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    assigned_shipper_id: Optional[str] = None

class OrderJourneyLegCreate(OrderJourneyLegBase):
    order_id: str # Phải cung cấp khi tạo

class OrderJourneyLeg(OrderJourneyLegBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Quan hệ (tùy chọn)
    # origin_warehouse: Optional[Warehouse] = None
    # destination_warehouse: Optional[Warehouse] = None
    # shipper: Optional[Shipper] = None