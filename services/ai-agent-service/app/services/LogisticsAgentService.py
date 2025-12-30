import asyncio
import httpx
import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

# Import models, schemas và services
from app import models
from app.schemas import Warehouse as warehouse_schemas
from app.schemas.ai_schemas import Coordinates
from app.crud.Warehouse import find_nearest_warehouses
from app.services.DirectionService import get_route_distance  # Service này đã hỗ trợ vehicle_type
from app.services.WarehouseService import get_warehouse_capacity_info, find_nearest_warehouse
from app.services.GeocodingService import get_coordinates_from_address
from app.crud import crud_order  
from app.crud import crud_shipper

logger = logging.getLogger(__name__)

# --- Helper Function: Haversine Distance (Fallback) ---
def _calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách đường chim bay (Haversine formula).
    Dùng làm phương án dự phòng khi không gọi được API bản đồ.
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

class LogisticsAgentService:
    """
    Service "Cầu nối" chính để xử lý logistics routing:
    1. Nhận địa chỉ/tọa độ.
    2. Tìm Kho (Warehouse) gần nhất (thực tế).
    3. Gọi DirectionService để tính khoảng cách đường bộ THỰC TẾ.
    """
    
    def __init__(self):
        self.http_client: Optional[httpx.AsyncClient] = None
        self.name = "LogisticsAgentService"
        logger.info(f"Initialized {self.name}")
    
    async def __aenter__(self):
        """Async context manager entry: Mở HTTP Client"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit: Đóng HTTP Client"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def _call_geocoding_service(self, address: str) -> Optional[Coordinates]:
        """
        Gọi geocoding service THẬT để chuyển đổi địa chỉ thành tọa độ.
        """
        try:
            coords = await get_coordinates_from_address(address, self.http_client)
            
            if coords:
                return coords
            else:
                logger.warning(f"❌ Geocoding Failed for address: {address}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Exception in geocoding service: {e}")
            return None
    
    def _extract_warehouse_coordinates_fixed(self, db: Session, warehouse: models.Warehouse) -> tuple[Optional[float], Optional[float]]:
        """
        Trích xuất tọa độ từ Warehouse model và tự động sửa lỗi đảo ngược lat/lon.
        """
        try:
            if hasattr(warehouse, 'latitude') and hasattr(warehouse, 'longitude'):
                if warehouse.latitude is not None and warehouse.longitude is not None:
                    try:
                        lat = float(warehouse.latitude)
                        lon = float(warehouse.longitude)
                    except ValueError:
                        return None, None
                    
                    # Logic sửa lỗi tọa độ bị đảo ngược (Vĩ độ VN phải từ 8-24)
                    if lat > 90 or lat < -90: 
                        return lon, lat 
                    
                    return lat, lon
            return None, None
            
        except Exception as e:
            logger.error(f"💥 Error extracting coordinates for warehouse {warehouse.warehouse_id}: {e}")
            return None, None
    
    async def _call_find_nearest_warehouse_by_road(
        self, 
        db: Session, 
        coords: Coordinates,
        required_capacity: int,
        vehicle_type: str = "car" # <--- FIX: Thêm tham số vehicle_type
    ) -> Optional[warehouse_schemas.WarehouseInfo]:
        """
        Tìm kho gần nhất và phù hợp nhất dựa trên khoảng cách đường bộ thực tế.
        """
        try:
            # 1. Tìm các ứng viên kho gần nhất theo không gian (nhanh)
            candidates = await run_in_threadpool(
                find_nearest_warehouses,
                db,
                latitude=coords.latitude,   
                longitude=coords.longitude, 
                limit=5 
            )
            
            if not candidates:
                logger.warning("❌ No warehouse candidates found using spatial search")
                return None
            
            # 2. Chuẩn bị các task tính toán khoảng cách
            tasks = []
            valid_warehouses = []
            
            for warehouse in candidates:
                warehouse_lat, warehouse_lon = self._extract_warehouse_coordinates_fixed(db, warehouse)
                
                if warehouse_lat is None or warehouse_lon is None:
                    continue
                
                wh_coords = Coordinates(
                    latitude=warehouse_lat, 
                    longitude=warehouse_lon 
                )
                
                # <--- FIX: Truyền vehicle_type vào hàm tính khoảng cách
                task = get_route_distance(coords, wh_coords, self.http_client, vehicle_type=vehicle_type)
                tasks.append(task)
                valid_warehouses.append(warehouse)
            
            if not tasks:
                return None
                
            # 3. Chạy song song tất cả các task tính khoảng cách
            distances = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 4. Chọn kho tốt nhất (Gần nhất + Đủ sức chứa)
            min_distance = float('inf')
            best_warehouse: Optional[models.Warehouse] = None
            
            for warehouse, dist in zip(valid_warehouses, distances):
                if isinstance(dist, Exception) or dist is None:
                    continue
                
                if dist < min_distance:
                    capacity_info = await run_in_threadpool(
                        get_warehouse_capacity_info,
                        db,
                        warehouse.warehouse_id
                    )
                    
                    if not capacity_info:
                        continue
                    
                    available_capacity = capacity_info['available_capacity']
                    
                    if available_capacity >= required_capacity:
                        min_distance = dist
                        best_warehouse = warehouse
                    else:
                        pass
            
            if best_warehouse is None:
                logger.error("❌ No suitable warehouse found (Distance/Capacity issue)")
                return None
            
            # 5. Trả về thông tin kho tốt nhất
            final_capacity_info = await run_in_threadpool(
                get_warehouse_capacity_info,
                db,
                best_warehouse.warehouse_id
            )
            
            final_lat, final_lon = self._extract_warehouse_coordinates_fixed(db, best_warehouse)
            
            warehouse_info = warehouse_schemas.WarehouseInfo(
                warehouse_id=best_warehouse.warehouse_id,
                name=best_warehouse.name,
                address=best_warehouse.address,
                latitude=final_lat,   
                longitude=final_lon,  
                type=best_warehouse.type.value if best_warehouse.type else "LOCAL_DEPOT",
                status=best_warehouse.status.value if best_warehouse.status else "ACTIVE",
                capacity_limit=final_capacity_info['capacity_limit'],
                current_load=final_capacity_info['current_load'],
                available_capacity=final_capacity_info['available_capacity'],
                distance_km=min_distance
            )
            
            return warehouse_info
            
        except Exception as e:
            logger.error(f"💥 Error in _call_find_nearest_warehouse_by_road: {e}")
            return None
        
    async def _call_find_nearest_warehouse_fallback(
        self, 
        db: Session, 
        coords: Coordinates
    ) -> Optional[warehouse_schemas.WarehouseInfo]:
        """
        Fallback method: Tìm kho bằng khoảng cách đường chim bay.
        """
        try:
            nearest_warehouse = await run_in_threadpool(
                find_nearest_warehouse,
                db,
                coords.latitude,  
                coords.longitude  
            )
            
            if not nearest_warehouse:
                return None
            
            capacity_info = await run_in_threadpool(
                get_warehouse_capacity_info,
                db,
                nearest_warehouse.warehouse_id
            )
            
            if not capacity_info:
                return None
            
            warehouse_lat, warehouse_lon = self._extract_warehouse_coordinates_fixed(db, nearest_warehouse)
            
            if warehouse_lat is None or warehouse_lon is None:
                return None
            
            air_distance = _calculate_haversine_distance(
                coords.latitude, coords.longitude,
                warehouse_lat, warehouse_lon
            )
            
            warehouse_info = warehouse_schemas.WarehouseInfo(
                warehouse_id=nearest_warehouse.warehouse_id,
                name=nearest_warehouse.name,
                address=nearest_warehouse.address,
                latitude=warehouse_lat,
                longitude=warehouse_lon,
                type=nearest_warehouse.type.value if nearest_warehouse.type else "LOCAL_DEPOT",
                status=nearest_warehouse.status.value if nearest_warehouse.status else "ACTIVE",
                capacity_limit=capacity_info['capacity_limit'],
                current_load=capacity_info['current_load'],
                available_capacity=capacity_info['available_capacity'],
                distance_km=air_distance
            )
            
            return warehouse_info
            
        except Exception as e:
            logger.error(f"💥 Error in fallback warehouse search: {e}")
            return None
    
    async def process_route_request(
        self, 
        db: Session,
        business_address: str,
        receiver_address: str,
        required_capacity: int,
        origin_coords: Optional[Tuple[float, float]] = None,
        dest_coords: Optional[Tuple[float, float]] = None,
        vehicle_type: str = "car" # <--- FIX: Thêm tham số vehicle_type
    ) -> dict:
        """
        Xử lý request routing. 
        """
        try:
            # --- Step 1: Xác định tọa độ điểm đi (SME/Business) ---
            business_coords_obj = None
            
            if origin_coords and origin_coords[0] is not None and origin_coords[1] is not None:
                business_coords_obj = Coordinates(
                    latitude=origin_coords[0], 
                    longitude=origin_coords[1]
                )
            elif business_address:
                business_coords_obj = await self._call_geocoding_service(business_address)
            
            if not business_coords_obj:
                return {
                    "status": "ERROR",
                    "message": "Cannot determine coordinates for Business/Origin",
                    "business_address": business_address,
                    "error_type": "GEOCODING_FAILED"
                }

            # --- Step 2: Xác định tọa độ điểm đến (Receiver/Hub) ---
            receiver_coords_obj = None
            
            if dest_coords and dest_coords[0] is not None and dest_coords[1] is not None:
                receiver_coords_obj = Coordinates(
                    latitude=dest_coords[0], 
                    longitude=dest_coords[1]
                )
            elif receiver_address:
                receiver_coords_obj = await self._call_geocoding_service(receiver_address)

            if not receiver_coords_obj:
                return {
                    "status": "ERROR", 
                    "message": "Cannot determine coordinates for Receiver/Dest",
                    "receiver_address": receiver_address,
                    "error_type": "GEOCODING_FAILED"
                }

            # --- Step 3: Find warehouse ---
            # <--- FIX: Truyền vehicle_type xuống hàm tìm kho
            warehouse_info = await self._call_find_nearest_warehouse_by_road(
                db, business_coords_obj, required_capacity, vehicle_type=vehicle_type
            )
            
            # --- Step 4: Fallback ---
            if not warehouse_info:
                warehouse_info = await self._call_find_nearest_warehouse_fallback(
                    db, business_coords_obj
                )
                
                if warehouse_info and warehouse_info.available_capacity < required_capacity:
                    return {
                        "status": "REJECTED",
                        "message": f"Nearest warehouse insufficient capacity",
                        "error_type": "INSUFFICIENT_CAPACITY"
                    }
            
            if not warehouse_info:
                return {
                    "status": "ERROR",
                    "message": "No suitable warehouse found",
                    "error_type": "NO_WAREHOUSE"
                }

            # --- Step 5: Calculate delivery route distance ---
            warehouse_coords_obj = Coordinates(
                latitude=warehouse_info.latitude, 
                longitude=warehouse_info.longitude 
            )
            
            # <--- FIX: Truyền vehicle_type vào hàm tính quãng đường
            delivery_distance = await get_route_distance(
                warehouse_coords_obj, receiver_coords_obj, self.http_client, vehicle_type=vehicle_type
            )
            
            total_distance = warehouse_info.distance_km + delivery_distance
            
            return {
                "status": "SUCCESS",
                "message": "Route calculated successfully",
                "business_coords": business_coords_obj.model_dump(), 
                "receiver_coords": receiver_coords_obj.model_dump(), 
                "warehouse": warehouse_info.model_dump(),        
                "pickup_distance_km": warehouse_info.distance_km,
                "delivery_distance_km": delivery_distance,
                "total_distance_km": round(total_distance, 2),
                "vehicle_type": vehicle_type, # Trả về loại xe đã dùng để tính
                "route_summary": {
                    "pickup": f"Business -> {warehouse_info.name}",
                    "delivery": f"{warehouse_info.name} -> Destination"
                },
                "geocoding_type": "HYBRID"
            }
            
        except Exception as e:
            logger.error(f"💥 Error processing route request: {e}")
            return {
                "status": "ERROR",
                "message": f"Internal error: {str(e)}",
                "error_type": "INTERNAL_ERROR"
            }

# Utility function updated
async def process_logistics_route(
    db: Session,
    business_address: str, 
    receiver_address: str, 
    required_capacity: int = 1,
    origin_coords: tuple[float, float] = None, 
    dest_coords: tuple[float, float] = None,
    vehicle_type: str = "car" # <--- FIX: Thêm tham số vehicle_type
) -> dict:
    """
    Hàm tiện ích để chạy logic routing.
    """
    async with LogisticsAgentService() as agent:
        return await agent.process_route_request(
            db, 
            business_address, 
            receiver_address, 
            required_capacity,
            origin_coords=origin_coords, 
            dest_coords=dest_coords,
            vehicle_type=vehicle_type # <--- FIX: Truyền vehicle_type vào service
        )