# app/routers/dispatch.py

from asyncio.log import logger
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.db.session import get_db
from app import models
from app.services.DispatchService import DispatchService, get_enum_value

router = APIRouter()
logger = logging.getLogger(__name__)

# --- SCHEMA DEFINITIONS (Data Transfer Objects) ---

class JourneyLegResponse(BaseModel):
    id: int
    sequence: int
    leg_type: str
    status: str
    assigned_shipper_id: Optional[str] = None
    # --- THÊM DÒNG NÀY ---
    shipper_full_name: Optional[str] = None 
    # ---------------------
    origin_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    origin_sme_id: Optional[str] = None
    destination_is_receiver: bool = False
    estimated_distance: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class PendingOrderResponse(BaseModel):
    order_id: str
    order_code: str
    status: str
    sme_id: str
    receiver_name: str
    receiver_address: str
    created_at: datetime
    area_id: Optional[str] = None

    class Config:
        from_attributes = True

class ShipperResponse(BaseModel):
    shipper_id: str
    full_name: str
    vehicle_type: str
    status: str
    area_id: str
    rating: float

    class Config:
        from_attributes = True

class AssignShipperRequest(BaseModel):
    order_id: str
    shipper_id: str # Shipper lấy hàng (Pickup)
    destination_hub_id: str # Kho Hub (Điểm đến chặng 1)
    destination_satellite_id: Optional[str] = None 

class UpdateJourneyLegRequest(BaseModel):
    assigned_shipper_id: Optional[str] = None
    origin_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    status: Optional[str] = None
    estimated_distance: Optional[float] = None

# Response models for DispatchPage
class DispatchOrderResponse(BaseModel):
    """Order data for Dispatch Console table"""
    id: str  # order_id
    code: str  # order_code
    from_location: str  # SME location (area_id or sme_id)
    to_location: str  # receiver address
    priority: str  # Calculated based on order attributes
    total_distance: float  # Sum of all leg distances
    status: str  # Order status
    
    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/pending-orders", response_model=List[PendingOrderResponse])
def get_pending_orders(db: Session = Depends(get_db)):
    """Lấy danh sách đơn hàng PENDING và IN_TRANSIT chờ điều phối."""
    orders = db.query(models.Order, models.SME.area_id)\
        .join(models.SME, models.Order.sme_id == models.SME.sme_id)\
        .filter(models.Order.status.in_(["PENDING", "IN_TRANSIT"]))\
        .all()
    
    result = []
    for order, area_id in orders:
        o_dict = PendingOrderResponse.model_validate(order)
        o_dict.area_id = area_id
        result.append(o_dict)
    return result

@router.get("/shippers/by-area/{area_id}", response_model=List[ShipperResponse])
def get_shippers_by_area(area_id: str, db: Session = Depends(get_db)):
    """Lấy danh sách shipper khả dụng trong khu vực."""
    try:
        # Kiểm tra area tồn tại không
        area = db.query(models.Area).filter(models.Area.area_id == area_id).first()
        if not area:
            return []  # Trả về list rỗng thay vì lỗi
        
        shippers = db.query(models.Shipper)\
            .join(models.Employee, models.Shipper.employee_id == models.Employee.employee_id)\
            .filter(
                models.Shipper.area_id == area_id,
                models.Shipper.status.in_(["ONLINE", "IDLE", "DELIVERING"])  # ✅ Add DELIVERING
            ).all()
        # In dispatch.py, add after line 114
        logger.info(f"🔍 Searching shippers in area: {area_id}")
        logger.info(f"📊 Found {len(shippers)} shippers")
        for s in shippers:
            logger.info(f"  - {s.shipper_id}: {s.vehicle_type}, status={s.status}")
        result = []
        for s in shippers:
            result.append(ShipperResponse(
                shipper_id=s.shipper_id,
                full_name=s.employee.full_name if s.employee else "Unknown",
                vehicle_type=get_enum_value(s.vehicle_type),  # ✅ Use helper function
                status=get_enum_value(s.status),               # ✅ Use helper function
                area_id=s.area_id,
                rating=float(s.rating or 0)
            ))
        return result
    except Exception as e:
        logger.error(f"Error in get_shippers_by_area: {e}")
        return []

@router.get("/summary", response_model=List[DispatchOrderResponse])
def get_dispatch_summary(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả đơn hàng (IN_TRANSIT, DELIVERING) với thông tin hành trình
    để hiển thị trên Dispatch Console.
    
    Response format phù hợp với DispatchPage.tsx
    """
    try:
        # Lấy tất cả đơn hàng đang trong vận chuyển
        orders = db.query(models.Order).filter(
            models.Order.status.in_(["PENDING", "IN_TRANSIT", "DELIVERING", "AT_WAREHOUSE"])
        ).all()
        
        result = []
        
        for order in orders:
            # Lấy tất cả legs của order
            legs = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == order.order_id
            ).order_by(models.OrderJourneyLeg.sequence).all()
            
            # Tính toán tổng distance
            total_distance = 0.0
            for leg in legs:
                if leg.estimated_distance:
                    total_distance += float(leg.estimated_distance)
            
            # Lấy thông tin SME/từ điểm
            from_location = order.area_id or order.sme_id or "Unknown"
            
            # Destination
            to_location = order.receiver_address or "Receiver"
            
            # Xác định priority (có thể dựa trên weight, note, hoặc status)
            priority = "MEDIUM"  # Default
            if order.weight and float(order.weight) > 10:
                priority = "HIGH"
            elif order.weight and float(order.weight) < 2:
                priority = "LOW"
            
            # Nếu có note chứa "urgent" thì priority HIGH
            if order.note and "urgent" in order.note.lower():
                priority = "HIGH"
            
            # Tạo response object
            dispatch_order = DispatchOrderResponse(
                id=order.order_id,
                code=order.order_code,
                from_location=from_location,
                to_location=to_location,
                priority=priority,
                total_distance=total_distance,
                status=str(order.status)
            )
            result.append(dispatch_order)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_dispatch_summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assign-shipper")
async def assign_shipper_to_order(
    request: AssignShipperRequest,
    db: Session = Depends(get_db)
):
    """Assign shipper and create 3-leg journey with automatic distance calculation."""
    
    if not all([request.order_id, request.shipper_id, request.destination_hub_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    satellite_id = request.destination_satellite_id or request.destination_hub_id

    try:
        # ✅ Call async method
        result = await DispatchService.create_complete_journey(
            db=db,
            order_id=request.order_id,
            shipper_id_pickup=request.shipper_id,
            destination_hub_id=request.destination_hub_id,
            destination_satellite_id=satellite_id,
            shipper_id_delivery=None
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Assign shipper error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/legs/{leg_id}", response_model=JourneyLegResponse)
async def update_journey_leg(
    leg_id: int,
    request: UpdateJourneyLegRequest,
    db: Session = Depends(get_db)
):
    """Update leg with automatic distance recalculation."""
    try:
        updates = request.model_dump(exclude_unset=True)
        # ✅ Call async method
        leg = await DispatchService.update_leg(db, leg_id, updates)
        return leg
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Update leg error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transfer/assign-shipper")
async def assign_transfer_shipper_endpoint(
    order_id: str,
    shipper_id: str,
    db: Session = Depends(get_db)
):
    """Assign shipper to TRANSFER leg."""
    try:
        leg = await DispatchService.assign_transfer_shipper(db, order_id, shipper_id)
        return {
            "success": True,
            "leg_id": leg.id,
            "shipper_id": shipper_id,
            "distance_km": float(leg.estimated_distance) if leg.estimated_distance else None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Assign transfer shipper error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delivery/assign-shipper")
async def assign_delivery_shipper_endpoint(
    order_id: str,
    shipper_id: str,
    db: Session = Depends(get_db)
):
    """Assign shipper to DELIVERY leg."""
    try:
        leg = await DispatchService.assign_delivery_shipper(db, order_id, shipper_id)
        return {
            "success": True,
            "leg_id": leg.id,
            "shipper_id": shipper_id,
            "distance_km": float(leg.estimated_distance) if leg.estimated_distance else None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Assign delivery shipper error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/legs/{leg_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journey_leg(leg_id: int, db: Session = Depends(get_db)):
    """Xóa một chặng (nếu chưa chạy)."""
    DispatchService.delete_leg(db, leg_id)
    return None

@router.get("/orders/{order_id}/legs", response_model=List[JourneyLegResponse])
def get_order_journey_legs(order_id: str, db: Session = Depends(get_db)):
    """Lấy chi tiết 3 chặng của đơn hàng kèm tên Shipper."""
    # Gọi service đã được update (xem phần dưới)
    raw_results = DispatchService.get_order_journey(db, order_id)
    
    # Map kết quả từ Service sang Schema
    response = []
    for leg, full_name in raw_results:
        leg_dict = JourneyLegResponse.model_validate(leg)
        leg_dict.shipper_full_name = full_name # Gán tên lấy được từ query
        response.append(leg_dict)
        
    return response

@router.get("/all-orders", response_model=List[PendingOrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    """Lấy danh sách TẤT CẢ đơn hàng để quản lý (Bao gồm cả COMPLETED/CANCELLED)."""
    orders = db.query(models.Order, models.SME.area_id)\
        .join(models.SME, models.Order.sme_id == models.SME.sme_id)\
        .order_by(models.Order.created_at.desc())\
        .all()
    
    result = []
    for order, area_id in orders:
        o_dict = PendingOrderResponse.model_validate(order)
        o_dict.area_id = area_id
        result.append(o_dict)
    return result