from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from sqlalchemy.orm import joinedload 

from app.db.session import get_db
# Import các hàm service cũ
from app.services.WarehouseService import (
    find_nearest_warehouse,
    get_warehouse_capacity_info,
    check_warehouse_availability,
    _calculate_haversine_distance,
    create_warehouse
)
# Import CRUD instance để xử lý Update/Delete
from app.crud import Warehouse as crud_warehouse
from app import models

# Import Schemas
from app.schemas.Warehouse import Warehouse, WarehouseCreate, WarehouseUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

# --- (Giữ nguyên các Pydantic Schemas phụ trợ: NearestWarehouseRequest, v.v...) ---
class NearestWarehouseRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class NearestWarehouseResponse(BaseModel):
    warehouse: Warehouse 
    distance_km: float
    coordinates: dict

class CapacityInfoResponse(BaseModel):
    warehouse_id: str
    name: str
    capacity_limit: int
    current_load: int
    available_capacity: int
    utilization_percentage: float

class AvailabilityCheckRequest(BaseModel):
    warehouse_id: str
    required_capacity: int = Field(1, gt=0)

class AvailabilityCheckResponse(BaseModel):
    warehouse_id: str
    is_available: bool
    capacity_info: Optional[CapacityInfoResponse]

class DistanceCalculationRequest(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float

class DistanceCalculationResponse(BaseModel):
    distance_km: float
    point1: dict
    point2: dict


# ==========================================
# CÁC ENDPOINT CHÍNH (CRUD)
# ==========================================

# 1. CREATE
@router.post("/", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
async def create_warehouse_endpoint(
    warehouse_in: WarehouseCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo mới một kho hàng.
    """
    try:
        logger.info(f"Creating new warehouse: {warehouse_in.name}")
        # Gọi service hoặc gọi trực tiếp crud_warehouse.create(db, obj_in=warehouse_in)
        return await create_warehouse(db, warehouse_in)
    except Exception as e:
        logger.error(f"Error creating warehouse: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo kho: {str(e)}"
        )

# 2. READ ALL
@router.get("/", response_model=List[Warehouse])
async def get_all_warehouses_endpoint(
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả các kho.
    """
    try:
        warehouses = db.query(models.Warehouse).options(
            joinedload(models.Warehouse.area)
        ).all()
        return warehouses
    except Exception as e:
        logger.error(f"Error retrieving warehouses: {e}")
        raise HTTPException(status_code=500, detail="Lỗi server khi lấy danh sách kho")

# 3. READ ONE
@router.get("/{warehouse_id}", response_model=Warehouse)
async def get_warehouse_by_id(
    warehouse_id: str,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết một kho.
    SỬA LỖI: Dùng db.query trực tiếp để tránh lỗi 'id' vs 'warehouse_id'.
    """
    # --- CODE MỚI (CHẠY ỔN ĐỊNH) ---
    warehouse = db.query(models.Warehouse)\
        .filter(models.Warehouse.warehouse_id == warehouse_id)\
        .first()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
        
    return warehouse
# 4. UPDATE (Đã sửa lỗi logic)
@router.put("/{warehouse_id}", response_model=Warehouse)
async def update_warehouse_endpoint(
    warehouse_id: str,
    warehouse_in: WarehouseUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin kho hàng.
    """
    try:
        # 1. Tìm kho bằng SQLAlchemy trực tiếp (An toàn nhất)
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.warehouse_id == warehouse_id).first()
        
        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kho với ID {warehouse_id}"
            )
        
        # 2. Thực hiện update dữ liệu
        update_data = warehouse_in.model_dump(exclude_unset=True) # Lấy các trường cần sửa
        
        for field, value in update_data.items():
            setattr(warehouse, field, value)
            
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)
        
        logger.info(f"Updated warehouse {warehouse_id}")
        return warehouse

    except HTTPException:
        raise
    except Exception as e:
        db.rollback() # Rollback nếu lỗi
        logger.error(f"Error updating warehouse: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật kho: {str(e)}"
        )

# 5. DELETE (Đã sửa lỗi 'type object Warehouse has no attribute get')
@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse_endpoint(
    warehouse_id: str,
    db: Session = Depends(get_db)
):
    """
    Xóa kho hàng.
    """
    try:
        # 1. Tìm kho (Sử dụng db.query thay vì Warehouse.get)
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.warehouse_id == warehouse_id).first()
        
        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kho với ID {warehouse_id}"
            )
        
        # 2. Thực hiện xóa
        db.delete(warehouse)
        db.commit()
        
        logger.info(f"Deleted warehouse {warehouse_id}")
        return None 

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting warehouse: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa kho: {str(e)}"
        )
# ==========================================
# CÁC ENDPOINT UTILITY KHÁC (Giữ nguyên)
# ==========================================

@router.post("/find-nearest", response_model=NearestWarehouseResponse)
async def find_nearest_warehouse_endpoint(
    request: NearestWarehouseRequest,
    db: Session = Depends(get_db)
):
    try:
        nearest_warehouse = find_nearest_warehouse(db, request.latitude, request.longitude)
        
        if not nearest_warehouse:
            raise HTTPException(status_code=404, detail="Không tìm thấy kho nào hoạt động")
        
        distance = _calculate_haversine_distance(
            request.latitude, request.longitude,
            float(nearest_warehouse.latitude), float(nearest_warehouse.longitude)
        )
        
        response = NearestWarehouseResponse(
            warehouse=Warehouse.from_orm(nearest_warehouse),
            distance_km=round(distance, 2),
            coordinates={
                "search_point": {"latitude": request.latitude, "longitude": request.longitude},
                "warehouse_point": {"latitude": float(nearest_warehouse.latitude), "longitude": float(nearest_warehouse.longitude)}
            }
        )
        return response
    except Exception as e:
        logger.error(f"Error finding nearest warehouse: {e}")
        raise HTTPException(status_code=500, detail="Lỗi server khi tìm kho gần nhất")

@router.get("/capacity/{warehouse_id}", response_model=CapacityInfoResponse)
async def get_warehouse_capacity_endpoint(warehouse_id: str, db: Session = Depends(get_db)):
    try:
        capacity_info = get_warehouse_capacity_info(db, warehouse_id)
        if not capacity_info:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy kho với ID: {warehouse_id}")
        return CapacityInfoResponse(**capacity_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi server khi lấy thông tin capacity")

@router.post("/check-availability", response_model=AvailabilityCheckResponse)
async def check_warehouse_availability_endpoint(request: AvailabilityCheckRequest, db: Session = Depends(get_db)):
    try:
        is_available = check_warehouse_availability(db, request.warehouse_id, request.required_capacity)
        capacity_info_dict = get_warehouse_capacity_info(db, request.warehouse_id)
        
        capacity_info = None
        if capacity_info_dict:
            capacity_info = CapacityInfoResponse(**capacity_info_dict)
        
        return AvailabilityCheckResponse(
            warehouse_id=request.warehouse_id,
            is_available=is_available,
            capacity_info=capacity_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi server khi kiểm tra availability")

@router.post("/calculate-distance", response_model=DistanceCalculationResponse)
async def calculate_distance_endpoint(request: DistanceCalculationRequest):
    try:
        distance = _calculate_haversine_distance(
            request.lat1, request.lon1, request.lat2, request.lon2
        )
        return DistanceCalculationResponse(
            distance_km=round(distance, 2),
            point1={"latitude": request.lat1, "longitude": request.lon1},
            point2={"latitude": request.lat2, "longitude": request.lon2}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi server khi tính khoảng cách")

# ==========================================
# WAREHOUSE USAGE SYNC (SCAN PICKUP ORDERS)
# ==========================================

class WarehouseUsageSyncResponse(BaseModel):
    total_warehouses_scanned: int
    warehouses_updated: List[dict]
    total_orders_counted: int
    timestamp: str

@router.post("/sync-usage", response_model=WarehouseUsageSyncResponse)
async def sync_warehouse_usage(
    db: Session = Depends(get_db)
):
    """
    Quét tất cả đơn hàng có PICKUP COMPLETED và cập nhật current_load cho warehouse.
    
    Logic:
    1. Tìm tất cả legs PICKUP với status COMPLETED
    2. Xác định warehouse đích (destination_warehouse_id)
    3. Đếm số lượng đơn hàng tại mỗi warehouse
    4. Cập nhật current_load
    """
    try:
        logger.info("🔄 Starting warehouse usage sync...")
        
        # 1. Query tất cả PICKUP legs đã hoàn thành
        from sqlalchemy import func
        
        # Subquery: Đếm số đơn hàng tại mỗi warehouse
        warehouse_usage = db.query(
            models.OrderJourneyLeg.destination_warehouse_id.label('warehouse_id'),
            func.count(models.OrderJourneyLeg.order_id).label('order_count')
        ).filter(
            models.OrderJourneyLeg.leg_type == models.LegType.PICKUP,
            models.OrderJourneyLeg.status == models.LegStatus.COMPLETED,
            models.OrderJourneyLeg.destination_warehouse_id.isnot(None)
        ).group_by(
            models.OrderJourneyLeg.destination_warehouse_id
        ).all()
        
        updated_warehouses = []
        total_orders = 0
        
        # 2. Cập nhật current_load cho từng warehouse
        for wh_id, count in warehouse_usage:
            warehouse = db.query(models.Warehouse).filter(
                models.Warehouse.warehouse_id == wh_id
            ).first()
            
            if warehouse:
                old_load = warehouse.current_load
                warehouse.current_load = count
                total_orders += count
                
                updated_warehouses.append({
                    "warehouse_id": wh_id,
                    "warehouse_name": warehouse.name,
                    "old_load": old_load,
                    "new_load": count,
                    "capacity_limit": warehouse.capacity_limit
                })
                
                logger.info(f"✅ Updated {warehouse.name}: {old_load} -> {count} orders")
        
        # 3. Reset warehouses không có đơn hàng nào
        all_warehouses = db.query(models.Warehouse).all()
        warehouse_ids_with_orders = {wh_id for wh_id, _ in warehouse_usage}
        
        for warehouse in all_warehouses:
            if warehouse.warehouse_id not in warehouse_ids_with_orders and warehouse.current_load > 0:
                old_load = warehouse.current_load
                warehouse.current_load = 0
                updated_warehouses.append({
                    "warehouse_id": warehouse.warehouse_id,
                    "warehouse_name": warehouse.name,
                    "old_load": old_load,
                    "new_load": 0,
                    "capacity_limit": warehouse.capacity_limit
                })
                logger.info(f"🔄 Reset {warehouse.name}: {old_load} -> 0")
        
        db.commit()
        
        from datetime import datetime
        
        return WarehouseUsageSyncResponse(
            total_warehouses_scanned=len(all_warehouses),
            warehouses_updated=updated_warehouses,
            total_orders_counted=total_orders,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error syncing warehouse usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đồng bộ usage: {str(e)}"
        )

@router.get("/{warehouse_id}/stats")
async def get_warehouse_detailed_stats(
    warehouse_id: str,
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê chi tiết về đơn hàng trong kho.
    """
    try:
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.warehouse_id == warehouse_id
        ).first()
        
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        # Đếm đơn hàng theo trạng thái
        orders_in_warehouse = db.query(models.OrderJourneyLeg).filter(
            models.OrderJourneyLeg.destination_warehouse_id == warehouse_id,
            models.OrderJourneyLeg.leg_type == models.LegType.PICKUP,
            models.OrderJourneyLeg.status == models.LegStatus.COMPLETED
        ).all()
        
        # Phân loại đơn hàng
        pending_transfer = 0
        in_progress = 0
        
        for leg in orders_in_warehouse:
            # Kiểm tra leg TRANSFER tiếp theo
            transfer_leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == leg.order_id,
                models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER
            ).first()
            
            if transfer_leg:
                if transfer_leg.status == models.LegStatus.PENDING:
                    pending_transfer += 1
                elif transfer_leg.status == models.LegStatus.IN_PROGRESS:
                    in_progress += 1
        
        return {
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse.name,
            "capacity_limit": warehouse.capacity_limit,
            "current_load": warehouse.current_load,
            "utilization_rate": round((warehouse.current_load / warehouse.capacity_limit * 100), 2) if warehouse.capacity_limit > 0 else 0,
            "orders_breakdown": {
                "total": len(orders_in_warehouse),
                "waiting_for_transfer": pending_transfer,
                "transfer_in_progress": in_progress
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting warehouse stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/sync-usage", response_model=WarehouseUsageSyncResponse)
async def sync_warehouse_usage(
    db: Session = Depends(get_db)
):
    """
    Đồng bộ lại Current Load của tất cả các kho dựa trên vị trí thực tế của đơn hàng.
    Logic:
    1. Lấy tất cả các leg đã COMPLETED.
    2. Group by Order ID -> Tìm leg có sequence lớn nhất (trạng thái mới nhất của đơn hàng).
    3. Nếu leg mới nhất là PICKUP hoặc TRANSFER -> +1 tồn kho cho destination_warehouse_id.
    4. Nếu leg mới nhất là DELIVERY -> Đơn hàng đã ra khỏi hệ thống kho -> Không tính.
    """
    try:
        logger.info("🔄 Starting warehouse usage sync (Logic: Last Completed Leg)...")
        
        # 1. Lấy tất cả các leg đã hoàn thành
        # Chỉ lấy các trường cần thiết để tối ưu query
        all_completed_legs = db.query(
            models.OrderJourneyLeg.order_id,
            models.OrderJourneyLeg.sequence,
            models.OrderJourneyLeg.leg_type,
            models.OrderJourneyLeg.destination_warehouse_id
        ).filter(
            models.OrderJourneyLeg.status == models.LegStatus.COMPLETED
        ).all()
        
        # 2. Xử lý logic tìm vị trí hiện tại của từng đơn hàng trong RAM (Python)
        # Dictionary để lưu leg mới nhất của từng order: {order_id: leg_object}
        latest_leg_map = {}
        
        for leg in all_completed_legs:
            order_id = leg.order_id
            
            # Nếu chưa có trong map hoặc tìm thấy sequence cao hơn (mới hơn)
            if order_id not in latest_leg_map:
                latest_leg_map[order_id] = leg
            else:
                if leg.sequence > latest_leg_map[order_id].sequence:
                    latest_leg_map[order_id] = leg
                    
        # 3. Tính toán số lượng tồn kho cho từng kho
        warehouse_counts = {} # {warehouse_id: count}
        
        total_orders_tracked = 0
        
        for order_id, leg in latest_leg_map.items():
            # Nếu chặng cuối cùng là DELIVERY, đơn hàng đã giao -> Không tính capacity
            if leg.leg_type == models.LegType.DELIVERY:
                continue
                
            # Nếu là PICKUP hoặc TRANSFER, đơn hàng đang nằm tại destination_warehouse_id
            if leg.destination_warehouse_id:
                wh_id = leg.destination_warehouse_id
                warehouse_counts[wh_id] = warehouse_counts.get(wh_id, 0) + 1
                total_orders_tracked += 1

        # 4. Cập nhật vào Database
        updated_warehouses = []
        all_warehouses = db.query(models.Warehouse).all()
        
        for warehouse in all_warehouses:
            # Lấy số lượng mới tính toán (nếu không có thì là 0)
            new_load = warehouse_counts.get(warehouse.warehouse_id, 0)
            
            # Chỉ update nếu có sự thay đổi để giảm tải DB write không cần thiết
            if warehouse.current_load != new_load:
                old_load = warehouse.current_load
                warehouse.current_load = new_load
                
                updated_warehouses.append({
                    "warehouse_id": warehouse.warehouse_id,
                    "warehouse_name": warehouse.name,
                    "old_load": old_load,
                    "new_load": new_load,
                    "capacity_limit": warehouse.capacity_limit
                })
                logger.info(f"✅ Updated {warehouse.name}: {old_load} -> {new_load}")
        
        db.commit()
        
        from datetime import datetime
        return WarehouseUsageSyncResponse(
            total_warehouses_scanned=len(all_warehouses),
            warehouses_updated=updated_warehouses,
            total_orders_counted=total_orders_tracked,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error syncing warehouse usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đồng bộ usage: {str(e)}"
        )