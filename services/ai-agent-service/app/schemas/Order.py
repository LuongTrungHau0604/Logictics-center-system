from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models import OrderStatus
from app.schemas.OrderJourneyLegBase import OrderJourneyLegBase, OrderJourneyLeg
from typing import List




class OrderBase(BaseModel):
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    receiver_latitude: Optional[float] = None
    receiver_longitude: Optional[float] = None
    sme_id: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    note: Optional[str] = None
    barcode_id: Optional[str] = None

class OrderCreate(OrderBase):
    order_id: str
    order_code: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    
    # Khi tạo đơn, ta tạo luôn các chặng
    legs: List[OrderJourneyLegBase] = [] 

class OrderUpdate(BaseModel):
    # Chỉ cho phép cập nhật 1 số trường
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    # ... (các trường khác có thể update)
    
    # Các trường quan trọng về trạng thái
    status: Optional[OrderStatus] = None
    active_leg_id: Optional[int] = None

class Order(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    
    order_id: str
    order_code: Optional[str] = None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    # Quan hệ (rất quan trọng)
    active_leg: Optional[OrderJourneyLeg] = None
    all_legs: List[OrderJourneyLeg] = []