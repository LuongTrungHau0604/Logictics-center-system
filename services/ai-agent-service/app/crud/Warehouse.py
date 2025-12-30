# --- CRUD cho Warehouse ---
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
import logging
import math
from typing import Type, List, Optional
from app import models, schemas
from app.crud.Base import CRUDBase
from app.schemas import schemas
import uuid
# Thiết lập logger
logger = logging.getLogger(__name__)

def _calculate_haversine_distance_sql(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách Haversine trong Python.
    """
    R = 6371000.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class CRUDWarehouse(CRUDBase):
    def create(self, db: Session, *, obj_in: schemas.WarehouseCreate) -> models.Warehouse:
        """
        Tạo Warehouse.
        Đã cập nhật: Lưu trực tiếp dữ liệu từ schema (bao gồm lat/lon nếu có)
        """
        try:
            # Chuyển obj_in thành dict
            obj_in_data = obj_in.model_dump()
            if "warehouse_id" not in obj_in_data:
                # Sinh ID dạng WH-ABC12345 (8 ký tự hex)
                obj_in_data["warehouse_id"] = f"WH-{uuid.uuid4().hex[:8].upper()}"
            # Tạo model object
            db_obj = models.Warehouse(**obj_in_data)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating Warehouse: {e}")
            raise

    def update(self, db: Session, *, db_obj: models.Warehouse, obj_in: schemas.WarehouseUpdate) -> models.Warehouse:
        """
        Cập nhật Warehouse.
        """
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating Warehouse {db_obj.warehouse_id}: {e}")
            raise
            
    def find_nearest_warehouses(
        self, db: Session, *, latitude: float, longitude: float, limit: int = 5
    ) -> List[models.Warehouse]:
        try:
            logger.info(f"Finding nearest warehouses using separate columns for ({latitude}, {longitude})")
            statement = select(models.Warehouse).where(
                models.Warehouse.status == models.WarehouseStatus.ACTIVE,
                models.Warehouse.latitude.isnot(None),
                models.Warehouse.longitude.isnot(None)
            )
            warehouses = db.execute(statement).scalars().all()
            if not warehouses:
                return []
            
            warehouse_distances = []
            for warehouse in warehouses:
                try:
                    wh_lat = float(warehouse.latitude)
                    wh_lon = float(warehouse.longitude)
                    if wh_lat > 90 or wh_lat < -90:
                        wh_lat, wh_lon = wh_lon, wh_lat
                    distance_meters = _calculate_haversine_distance_sql(
                        latitude, longitude, wh_lat, wh_lon
                    )
                    warehouse_distances.append((warehouse, distance_meters))
                except (ValueError, TypeError):
                    continue
            
            warehouse_distances.sort(key=lambda x: x[1])
            return [wh for wh, dist in warehouse_distances[:limit]]
        except SQLAlchemyError as e:
            logger.error(f"Error finding nearest warehouses: {e}")
            return []

    def get_all_active_warehouses(self, db: Session) -> List[models.Warehouse]:
        try:
            statement = select(models.Warehouse).where(models.Warehouse.status == models.WarehouseStatus.ACTIVE)
            results = db.execute(statement).scalars().all()
            return results
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving active warehouses: {e}")
            return []

# Instance của CRUD class
crud_warehouse = CRUDWarehouse(models.Warehouse)

# --- Helper functions ---
def get_all_active_warehouses(db: Session) -> List[models.Warehouse]:
    return crud_warehouse.get_all_active_warehouses(db)

def find_nearest_warehouses(db: Session, *, latitude: float, longitude: float, limit: int = 5) -> List[models.Warehouse]:
    return crud_warehouse.find_nearest_warehouses(db, latitude=latitude, longitude=longitude, limit=limit)

# --- HÀM STANDALONE cho compatibility ---
def get_all_active_warehouses(db: Session) -> List[models.Warehouse]:
    return crud_warehouse.get_all_active_warehouses(db)

def find_nearest_warehouses(
    db: Session, *, latitude: float, longitude: float, limit: int = 5
) -> List[models.Warehouse]:
    return crud_warehouse.find_nearest_warehouses(
        db, latitude=latitude, longitude=longitude, limit=limit
    )

def find_warehouses_within_radius(
    db: Session, latitude: float, longitude: float, radius_km: float
) -> List[models.Warehouse]:
    """
    Tìm warehouses trong bán kính cho trước.
    """
    try:
        warehouses = get_all_active_warehouses(db)
        warehouses_in_radius = []
        
        for warehouse in warehouses:
            if warehouse.latitude is None or warehouse.longitude is None:
                continue
                
            wh_lat = float(warehouse.latitude)
            wh_lon = float(warehouse.longitude)
            
            if wh_lat > 90 or wh_lat < -90:
                wh_lat, wh_lon = wh_lon, wh_lat
                
            distance_meters = _calculate_haversine_distance_sql(
                latitude, longitude, wh_lat, wh_lon
            )
            distance_km = distance_meters / 1000.0
            
            if distance_km <= radius_km:
                warehouses_in_radius.append(warehouse)
        
        logger.info(f"Found {len(warehouses_in_radius)} warehouses within {radius_km}km")
        return warehouses_in_radius
        
    except Exception as e:
        logger.error(f"Error finding warehouses within radius: {e}")
        return []
# --- ADD THIS TO THE END OF Warehouse.py ---

def find_nearest_warehouse(db: Session, latitude: float, longitude: float) -> Optional[models.Warehouse]:
    """
    Wrapper function to find the SINGLE nearest warehouse.
    Used by IntelligentLogisticsAI to find the destination hub.
    """
    # Reuse the existing plural function with limit=1
    results = find_nearest_warehouses(db, latitude=latitude, longitude=longitude, limit=1)
    return results[0] if results else None