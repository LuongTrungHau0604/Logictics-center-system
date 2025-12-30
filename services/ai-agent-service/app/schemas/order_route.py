from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class OrderRouteBase(BaseModel):
    order_id: str
    from_warehouse_id: str
    to_warehouse_id: Optional[str] = None
    sequence_order: int
    distance_km: Decimal
    estimated_time_minutes: int


class OrderRouteCreate(OrderRouteBase):
    pass


class OrderRouteUpdate(BaseModel):
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OrderRouteOut(OrderRouteBase):
    route_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RouteOptimizationWithSave(BaseModel):
    """Schema cho response khi tối ưu và lưu route"""
    optimization_id: str
    total_routes_created: int
    total_distance_km: Decimal
    total_estimated_hours: float
    routes: List[OrderRouteOut]
    unassigned_orders: List[str]


class ExistingOrderRequest(BaseModel):
    """Schema cho đơn hàng đã có trong database"""
    order_id: str


class SMEInfo(BaseModel):
    """Thông tin SME"""
    sme_id: str
    business_name: str
    address: str
    contact_phone: str
    email: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class OrderInfo(BaseModel):
    """Thông tin đơn hàng từ database"""
    order_id: str
    order_code: str
    sme_id: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    receiver_latitude: float
    receiver_longitude: float
    weight_kg: float
    dimensions: str
    notes: Optional[str] = None
    status: str


class RouteOptimizationResult(BaseModel):
    """Kết quả tối ưu tuyến đường SME -> Customer"""
    optimization_id: str
    order_id: str
    sme_info: SMEInfo
    customer_info: dict
    route_segments: List[dict]
    total_distance_km: Decimal
    total_estimated_time_minutes: int
    estimated_pickup_time: datetime
    estimated_delivery_time: datetime
    status: str = "PLANNED"


class OrderProcessingResponse(BaseModel):
    """Response cho việc xử lý đơn hàng"""
    order_id: str
    processing_status: str  # SUCCESS, FAILED, QUEUED
    sme_info: Optional[SMEInfo] = None
    route_result: Optional[RouteOptimizationResult] = None
    queue_info: Optional[dict] = None
    error_message: Optional[str] = None