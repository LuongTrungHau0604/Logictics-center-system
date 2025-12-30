import math
import httpx
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app import models
from app.crud.Warehouse import get_all_active_warehouses, crud_warehouse
from app.schemas.Warehouse import WarehouseCreate

# ✅ CORRECT: Import directly from the sibling file
from app.services.GeocodingService import get_coordinates_from_address

logger = logging.getLogger(__name__)

# --- Main Functions ---

async def create_warehouse(db: Session, warehouse_in: WarehouseCreate) -> models.Warehouse:
    """
    Tạo mới kho hàng. 
    Tự động geocoding bằng cách gọi trực tiếp GeocodingService nếu thiếu tọa độ.
    """
    try:
        # 1. Kiểm tra xem FE có gửi tọa độ lên không
        if not warehouse_in.latitude or not warehouse_in.longitude:
            logger.info(f"⚠️ Missing coordinates for warehouse '{warehouse_in.name}'. Attempting internal geocoding...")
            
            # 2. Gọi trực tiếp hàm Python (Không qua HTTP Request nội bộ)
            # GeocodingService yêu cầu httpx client, ta tạo context manager ở đây
            async with httpx.AsyncClient() as client:
                coords = await get_coordinates_from_address(warehouse_in.address, client)
            
            if coords:
                warehouse_in.latitude = coords.latitude
                warehouse_in.longitude = coords.longitude
                logger.info(f"✅ Geocoding successful: ({coords.latitude}, {coords.longitude})")
            else:
                logger.warning("❌ Could not geocode address. Warehouse will be created without coordinates.")
        
        # 3. Tạo kho
        return crud_warehouse.create(db, obj_in=warehouse_in)
        
    except Exception as e:
        logger.error(f"Error creating warehouse: {e}")
        raise e

# ... (Keep the rest of your calculation functions below exactly as they were) ...

def _calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')

    R = 6371.0
    try:
        lat1_rad = math.radians(float(lat1))
        lon1_rad = math.radians(float(lon1))
        lat2_rad = math.radians(float(lat2))
        lon2_rad = math.radians(float(lon2))
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    except ValueError:
        return float('inf')

def _extract_warehouse_coordinates(db: Session, warehouse: models.Warehouse) -> tuple[Optional[float], Optional[float]]:
    try:
        if hasattr(warehouse, 'latitude') and hasattr(warehouse, 'longitude'):
            if warehouse.latitude is not None and warehouse.longitude is not None:
                lat = float(warehouse.latitude)
                lon = float(warehouse.longitude)
                
                if lat > 90 or lat < -90:
                    return lon, lat  
                if lat > 100 and lon < 25:
                     return lon, lat
                return lat, lon
        return None, None
    except Exception as e:
        logger.error(f"Error extracting coordinates: {e}")
        return None, None

def find_nearest_warehouse(db: Session, lat: float, lon: float) -> Optional[models.Warehouse]:
    try:
        warehouses = get_all_active_warehouses(db)
        if not warehouses: return None
        
        nearest_warehouse = None
        min_distance = float('inf')
        
        for warehouse in warehouses:
            w_lat, w_lon = _extract_warehouse_coordinates(db, warehouse)
            if w_lat is None: continue
            
            distance = _calculate_haversine_distance(lat, lon, w_lat, w_lon)
            if distance < min_distance:
                min_distance = distance
                nearest_warehouse = warehouse
        return nearest_warehouse
    except Exception as e:
        logger.error(f"Error finding nearest warehouse: {e}")
        return None

def find_warehouses_within_radius(db: Session, lat: float, lon: float, radius_km: float) -> list[tuple[models.Warehouse, float]]:
    try:
        warehouses = get_all_active_warehouses(db)
        if not warehouses: return []
        
        warehouses_in_radius = []
        for warehouse in warehouses:
            w_lat, w_lon = _extract_warehouse_coordinates(db, warehouse)
            if w_lat is None: continue
            
            distance = _calculate_haversine_distance(lat, lon, w_lat, w_lon)
            if distance <= radius_km:
                warehouses_in_radius.append((warehouse, distance))
        
        warehouses_in_radius.sort(key=lambda x: x[1])
        return warehouses_in_radius
    except Exception as e:
        logger.error(f"Error finding warehouses within radius: {e}")
        return []

def get_warehouse_capacity_info(db: Session, warehouse_id: str) -> Optional[dict]:
    try:
        query = select(models.Warehouse).where(models.Warehouse.warehouse_id == warehouse_id)
        warehouse = db.execute(query).scalar_one_or_none()
        if not warehouse: return None
        
        limit = warehouse.capacity_limit or 1
        load = warehouse.current_load or 0
        return {
            'warehouse_id': warehouse.warehouse_id,
            'name': warehouse.name,
            'capacity_limit': limit,
            'current_load': load,
            'available_capacity': limit - load,
            'utilization_percentage': (load / limit) * 100
        }
    except Exception as e:
        logger.error(f"Error getting warehouse capacity info for {warehouse_id}: {e}")
        return None

def check_warehouse_availability(db: Session, warehouse_id: str, required_capacity: int = 1) -> bool:
    info = get_warehouse_capacity_info(db, warehouse_id)
    return info['available_capacity'] >= required_capacity if info else False