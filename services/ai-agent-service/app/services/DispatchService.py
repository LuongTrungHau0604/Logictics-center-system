# services/ai-agent-service/app/services/DispatchService.py
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
import httpx

from app import models
from app.crud import crud_warehouse, crud_shipper
from app.services.GeocodingService import get_coordinates_from_address
from app.services.DirectionService import get_route_distance
from app.schemas.ai_schemas import Coordinates

logger = logging.getLogger(__name__)

# Helper function để extract enum value
def get_enum_value(enum_obj) -> str:
    """Extract string value from SQLAlchemy Enum object."""
    if enum_obj is None:
        return None
    enum_str = str(enum_obj)
    if '.' in enum_str:
        return enum_str.split('.')[-1]
    return enum_str

async def calculate_distance_between_points(
    origin_lat: float,
    origin_lon: float, 
    dest_lat: float,
    dest_lon: float,
    vehicle_type: str = "MOTORBIKE"
) -> float:
    """
    Calculate actual road distance using Goong API.
    Returns distance in kilometers.
    """
    try:
        async with httpx.AsyncClient() as client:
            coord1 = Coordinates(latitude=origin_lat, longitude=origin_lon)
            coord2 = Coordinates(latitude=dest_lat, longitude=dest_lon)
            
            distance_km = await get_route_distance(coord1, coord2, client, vehicle_type)
            return round(distance_km, 2)
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        # Fallback to haversine
        return calculate_haversine_fallback(origin_lat, origin_lon, dest_lat, dest_lon)

def calculate_haversine_fallback(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Fallback haversine calculation in km."""
    import math
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 2)

class DispatchService:
    """
    Service quản lý OrderJourneyLeg cho Dispatch thủ công.
    Tương thích với logic Agent nhưng cho phép can thiệp thủ công.
    """
    
    @staticmethod
    async def create_complete_journey(
        db: Session,
        order_id: str,
        shipper_id_pickup: str,
        destination_hub_id: str,
        destination_satellite_id: str,
        shipper_id_delivery: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tạo đầy đủ 3 chặng cho đơn hàng với distance calculation:
        1. PICKUP: SME → Hub
        2. TRANSFER: Hub → Satellite
        3. DELIVERY: Satellite → Receiver
        
        Returns:
            Dict với thông tin 3 legs đã tạo
        """
        try:
            # Validate Order
            order = db.query(models.Order).filter(
                models.Order.order_id == order_id
            ).first()
            
            if not order:
                raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
            
            # Check order status
            order_status = get_enum_value(order.status)
            if order_status not in ["PENDING", "IN_TRANSIT"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Order must be PENDING or IN_TRANSIT, current: {order_status}"
                )
            
            # Get SME coordinates
            sme = db.query(models.SME).filter(models.SME.sme_id == order.sme_id).first()
            if not sme or not sme.latitude or not sme.longitude:
                raise HTTPException(status_code=400, detail="SME coordinates not available")
            
            sme_lat = float(sme.latitude)
            sme_lon = float(sme.longitude)
            
            # Validate Warehouses
            hub = db.query(models.Warehouse).filter(
                models.Warehouse.warehouse_id == destination_hub_id
            ).first()
            
            satellite = db.query(models.Warehouse).filter(
                models.Warehouse.warehouse_id == destination_satellite_id
            ).first()
            
            if not hub or not satellite:
                raise HTTPException(status_code=404, detail="Hub or Satellite warehouse not found")
            
            if not hub.latitude or not hub.longitude or not satellite.latitude or not satellite.longitude:
                raise HTTPException(status_code=400, detail="Warehouse coordinates not available")
            
            hub_lat = float(hub.latitude)
            hub_lon = float(hub.longitude)
            satellite_lat = float(satellite.latitude)
            satellite_lon = float(satellite.longitude)
            
            # Validate Shipper
            pickup_shipper = db.query(models.Shipper).filter(
                models.Shipper.shipper_id == shipper_id_pickup
            ).first()
            
            if not pickup_shipper:
                raise HTTPException(status_code=404, detail=f"Shipper {shipper_id_pickup} not found")
            
            shipper_status = get_enum_value(pickup_shipper.status)
            if shipper_status not in ["ONLINE", "IDLE"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Shipper must be ONLINE or IDLE, current: {shipper_status}"
                )
            
            shipper_vehicle = get_enum_value(pickup_shipper.vehicle_type)
            
            # ✅ Calculate distances for each leg
            logger.info(f"📏 Calculating distances for order {order_id}...")
            
            # LEG 1: SME → Hub
            distance_leg1 = await calculate_distance_between_points(
                sme_lat, sme_lon, hub_lat, hub_lon, shipper_vehicle
            )
            logger.info(f"  Leg 1 (SME→Hub): {distance_leg1} km")
            
            # LEG 2: Hub → Satellite (usually TRUCK)
            distance_leg2 = await calculate_distance_between_points(
                hub_lat, hub_lon, satellite_lat, satellite_lon, "TRUCK"
            )
            logger.info(f"  Leg 2 (Hub→Satellite): {distance_leg2} km")
            
            # LEG 3: Satellite → Receiver (need receiver coordinates)
            distance_leg3 = None
            if order.receiver_address:
                try:
                    async with httpx.AsyncClient() as client:
                        receiver_coords = await get_coordinates_from_address(order.receiver_address, client)
                        if receiver_coords:
                            distance_leg3 = await calculate_distance_between_points(
                                satellite_lat, satellite_lon, 
                                receiver_coords.latitude, receiver_coords.longitude,
                                "MOTORBIKE"
                            )
                            logger.info(f"  Leg 3 (Satellite→Receiver): {distance_leg3} km")
                except Exception as e:
                    logger.warning(f"Could not calculate leg 3 distance: {e}")
            
            # Check if legs already exist
            existing_legs = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == order_id
            ).all()
            
            if existing_legs:
                raise HTTPException(
                    status_code=400,
                    detail=f"Journey legs already exist for order {order_id}"
                )
            
            # LEG 1: PICKUP (SME → Hub)
            pickup_leg = models.OrderJourneyLeg(
                order_id=order_id,
                sequence=1,
                leg_type="PICKUP",
                status="PENDING",
                origin_sme_id=order.sme_id,
                origin_warehouse_id=None,
                destination_warehouse_id=destination_hub_id,
                destination_is_receiver=False,
                assigned_shipper_id=shipper_id_pickup,
                estimated_distance=distance_leg1,  # ✅ Add calculated distance
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(pickup_leg)
            
            # LEG 2: TRANSFER (Hub → Satellite)
            transfer_leg = models.OrderJourneyLeg(
                order_id=order_id,
                sequence=2,
                leg_type="TRANSFER",
                status="PENDING",
                origin_warehouse_id=destination_hub_id,
                origin_sme_id=None,
                destination_warehouse_id=destination_satellite_id,
                destination_is_receiver=False,
                assigned_shipper_id=None,
                estimated_distance=distance_leg2,  # ✅ Add calculated distance
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(transfer_leg)
            
            # LEG 3: DELIVERY (Satellite → Receiver)
            delivery_leg = models.OrderJourneyLeg(
                order_id=order_id,
                sequence=3,
                leg_type="DELIVERY",
                status="PENDING",
                origin_warehouse_id=destination_satellite_id,
                origin_sme_id=None,
                destination_is_receiver=True,
                destination_warehouse_id=None,
                assigned_shipper_id=shipper_id_delivery,
                estimated_distance=distance_leg3,  # ✅ Add calculated distance (may be None)
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(delivery_leg)
            
            # Update Order Status
            order.status = "IN_TRANSIT"
            order.updated_at = datetime.utcnow()
            
            # Update Pickup Shipper Status
            pickup_shipper.status = "DELIVERING"
            pickup_shipper.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(pickup_leg)
            db.refresh(transfer_leg)
            db.refresh(delivery_leg)
            
            total_distance = sum(filter(None, [distance_leg1, distance_leg2, distance_leg3]))
            
            return {
                "success": True,
                "order_id": order_id,
                "message": "Journey created successfully with distance calculation",
                "total_distance_km": round(total_distance, 2),
                "legs": [
                    {
                        "id": pickup_leg.id,
                        "sequence": 1,
                        "type": "PICKUP",
                        "from": f"SME-{order.sme_id}",
                        "to": destination_hub_id,
                        "shipper": shipper_id_pickup,
                        "status": "PENDING",
                        "distance_km": distance_leg1
                    },
                    {
                        "id": transfer_leg.id,
                        "sequence": 2,
                        "type": "TRANSFER",
                        "from": destination_hub_id,
                        "to": destination_satellite_id,
                        "shipper": None,
                        "status": "PENDING",
                        "distance_km": distance_leg2
                    },
                    {
                        "id": delivery_leg.id,
                        "sequence": 3,
                        "type": "DELIVERY",
                        "from": destination_satellite_id,
                        "to": "RECEIVER",
                        "shipper": shipper_id_delivery,
                        "status": "PENDING",
                        "distance_km": distance_leg3
                    }
                ]
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating journey: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def update_leg(
        db: Session,
        leg_id: int,
        updates: Dict[str, Any]
    ) -> models.OrderJourneyLeg:
        """
        Cập nhật một leg cụ thể với automatic distance recalculation.
        """
        try:
            leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.id == leg_id
            ).first()
            
            if not leg:
                raise HTTPException(status_code=404, detail=f"Leg {leg_id} not found")
            
            leg_status = get_enum_value(leg.status)
            if leg_status == "COMPLETED" and 'status' not in updates:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot update a completed leg"
                )
            
            # Track if we need to recalculate distance
            recalculate_distance = False
            
            # Update shipper
            if 'assigned_shipper_id' in updates and updates['assigned_shipper_id']:
                shipper = db.query(models.Shipper).filter(
                    models.Shipper.shipper_id == updates['assigned_shipper_id']
                ).first()
                if not shipper:
                    raise HTTPException(status_code=404, detail="Shipper not found")
                
                leg.assigned_shipper_id = updates['assigned_shipper_id']
                
                # Update shipper status
                shipper.status = "DELIVERING"
                shipper.updated_at = datetime.utcnow()
                recalculate_distance = True
            
            # Update destination warehouse
            if 'destination_warehouse_id' in updates and updates['destination_warehouse_id']:
                warehouse = db.query(models.Warehouse).filter(
                    models.Warehouse.warehouse_id == updates['destination_warehouse_id']
                ).first()
                if not warehouse:
                    raise HTTPException(status_code=404, detail="Destination warehouse not found")
                
                leg.destination_warehouse_id = updates['destination_warehouse_id']
                recalculate_distance = True
            
            # Update origin warehouse
            if 'origin_warehouse_id' in updates and updates['origin_warehouse_id']:
                warehouse = db.query(models.Warehouse).filter(
                    models.Warehouse.warehouse_id == updates['origin_warehouse_id']
                ).first()
                if not warehouse:
                    raise HTTPException(status_code=404, detail="Origin warehouse not found")
                
                leg.origin_warehouse_id = updates['origin_warehouse_id']
                recalculate_distance = True
            
            # Update status
            if 'status' in updates:
                new_status = updates['status']
                
                if new_status == "IN_PROGRESS" and not leg.assigned_shipper_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot start leg without assigned shipper"
                    )
                
                leg.status = new_status
                
                if new_status == "IN_PROGRESS":
                    leg.started_at = datetime.utcnow()
                elif new_status == "COMPLETED":
                    leg.completed_at = datetime.utcnow()
            
            # ✅ Recalculate distance if warehouse changed
            if recalculate_distance:
                try:
                    distance = await DispatchService._calculate_leg_distance(db, leg)
                    if distance:
                        leg.estimated_distance = distance
                        logger.info(f"✅ Recalculated distance for leg {leg_id}: {distance} km")
                except Exception as e:
                    logger.warning(f"Could not recalculate distance: {e}")
            
            # Manual distance override
            if 'estimated_distance' in updates:
                leg.estimated_distance = updates['estimated_distance']
            
            leg.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(leg)
            
            return leg
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating leg: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def _calculate_leg_distance(db: Session, leg: models.OrderJourneyLeg) -> Optional[float]:
        """Helper to calculate distance for a leg based on its type."""
        try:
            # Get origin coordinates
            origin_lat, origin_lon = None, None
            
            if leg.origin_sme_id:
                sme = db.query(models.SME).filter(models.SME.sme_id == leg.origin_sme_id).first()
                if sme and sme.latitude and sme.longitude:
                    origin_lat, origin_lon = float(sme.latitude), float(sme.longitude)
            elif leg.origin_warehouse_id:
                warehouse = db.query(models.Warehouse).filter(
                    models.Warehouse.warehouse_id == leg.origin_warehouse_id
                ).first()
                if warehouse and warehouse.latitude and warehouse.longitude:
                    origin_lat, origin_lon = float(warehouse.latitude), float(warehouse.longitude)
            
            # Get destination coordinates
            dest_lat, dest_lon = None, None
            
            if leg.destination_warehouse_id:
                warehouse = db.query(models.Warehouse).filter(
                    models.Warehouse.warehouse_id == leg.destination_warehouse_id
                ).first()
                if warehouse and warehouse.latitude and warehouse.longitude:
                    dest_lat, dest_lon = float(warehouse.latitude), float(warehouse.longitude)
            elif leg.destination_is_receiver:
                order = db.query(models.Order).filter(models.Order.order_id == leg.order_id).first()
                if order and order.receiver_address:
                    async with httpx.AsyncClient() as client:
                        coords = await get_coordinates_from_address(order.receiver_address, client)
                        if coords:
                            dest_lat, dest_lon = coords.latitude, coords.longitude
            
            if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
                return None
            
            # Get vehicle type from shipper
            vehicle_type = "MOTORBIKE"  # default
            if leg.assigned_shipper_id:
                shipper = db.query(models.Shipper).filter(
                    models.Shipper.shipper_id == leg.assigned_shipper_id
                ).first()
                if shipper:
                    vehicle_type = get_enum_value(shipper.vehicle_type)
            
            distance = await calculate_distance_between_points(
                origin_lat, origin_lon, dest_lat, dest_lon, vehicle_type
            )
            
            return distance
            
        except Exception as e:
            logger.error(f"Error calculating leg distance: {e}")
            return None
    
    @staticmethod
    async def assign_transfer_shipper(
        db: Session,
        order_id: str,
        shipper_id: str
    ) -> models.OrderJourneyLeg:
        """
        Gán shipper cho chặng TRANSFER với distance calculation.
        """
        try:
            transfer_leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == order_id,
                models.OrderJourneyLeg.sequence == 2,
                models.OrderJourneyLeg.leg_type == "TRANSFER"
            ).first()
            
            if not transfer_leg:
                raise HTTPException(status_code=404, detail=f"Transfer leg not found for order {order_id}")
            
            shipper = db.query(models.Shipper).filter(
                models.Shipper.shipper_id == shipper_id
            ).first()
            
            if not shipper:
                raise HTTPException(status_code=404, detail=f"Shipper {shipper_id} not found")
            
            shipper_status = get_enum_value(shipper.status)
            if shipper_status not in ["ONLINE", "IDLE"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Shipper must be ONLINE or IDLE, current: {shipper_status}"
                )
            
            shipper_vehicle = get_enum_value(shipper.vehicle_type)
            if shipper_vehicle not in ["TRUCK", "CAR"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Transfer leg requires TRUCK or CAR, shipper has: {shipper_vehicle}"
                )
            
            transfer_leg.assigned_shipper_id = shipper_id
            
            # ✅ Recalculate distance with new shipper's vehicle type
            if not transfer_leg.estimated_distance:
                distance = await DispatchService._calculate_leg_distance(db, transfer_leg)
                if distance:
                    transfer_leg.estimated_distance = distance
            
            transfer_leg.updated_at = datetime.utcnow()
            
            shipper.status = "DELIVERING"
            shipper.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(transfer_leg)
            
            return transfer_leg
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning transfer shipper: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def assign_delivery_shipper(
        db: Session,
        order_id: str,
        shipper_id: str
    ) -> models.OrderJourneyLeg:
        """
        Gán shipper cho chặng DELIVERY với distance calculation.
        """
        try:
            delivery_leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == order_id,
                models.OrderJourneyLeg.sequence == 3,
                models.OrderJourneyLeg.leg_type == "DELIVERY"
            ).first()
            
            if not delivery_leg:
                raise HTTPException(status_code=404, detail=f"Delivery leg not found for order {order_id}")
            
            shipper = db.query(models.Shipper).filter(
                models.Shipper.shipper_id == shipper_id
            ).first()
            
            if not shipper:
                raise HTTPException(status_code=404, detail=f"Shipper {shipper_id} not found")
            
            shipper_status = get_enum_value(shipper.status)
            if shipper_status not in ["ONLINE", "IDLE"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Shipper must be ONLINE or IDLE, current: {shipper_status}"
                )
            
            delivery_leg.assigned_shipper_id = shipper_id
            
            # ✅ Calculate distance if not already set
            if not delivery_leg.estimated_distance:
                distance = await DispatchService._calculate_leg_distance(db, delivery_leg)
                if distance:
                    delivery_leg.estimated_distance = distance
            
            delivery_leg.updated_at = datetime.utcnow()
            
            shipper.status = "DELIVERING"
            shipper.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(delivery_leg)
            
            return delivery_leg
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning delivery shipper: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def delete_leg(db: Session, leg_id: int) -> bool:
        """Xóa một leg (chỉ nếu chưa bắt đầu)."""
        try:
            leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.id == leg_id
            ).first()
            
            if not leg:
                raise HTTPException(status_code=404, detail=f"Leg {leg_id} not found")
            
            leg_status = get_enum_value(leg.status)
            if leg_status in ["IN_PROGRESS", "COMPLETED"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot delete leg with status: {leg_status}"
                )
            
            db.delete(leg)
            db.commit()
            return True
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting leg: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    

    @staticmethod
    def get_order_journey(db: Session, order_id: str):
        """
        Lấy toàn bộ journey của một order kèm theo Tên Shipper.
        Trả về list of tuples: (OrderJourneyLeg, full_name)
        """
        try:
            # Thực hiện Query Join 3 bảng
            results = db.query(
                models.OrderJourneyLeg, 
                models.Employee.full_name
            )\
            .outerjoin(models.Shipper, models.OrderJourneyLeg.assigned_shipper_id == models.Shipper.shipper_id)\
            .outerjoin(models.Employee, models.Shipper.employee_id == models.Employee.employee_id)\
            .filter(models.OrderJourneyLeg.order_id == order_id)\
            .order_by(models.OrderJourneyLeg.sequence)\
            .all()
            
            return results
        except Exception as e:
            logger.error(f"Error getting order journey: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def reassign_warehouse(
        db: Session,
        leg_id: int,
        new_warehouse_id: str,
        is_destination: bool = True
    ) -> models.OrderJourneyLeg:
        """Thay đổi kho và tự động tính lại distance."""
        try:
            leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.id == leg_id
            ).first()
            
            if not leg:
                raise HTTPException(status_code=404, detail=f"Leg {leg_id} not found")
            
            warehouse = db.query(models.Warehouse).filter(
                models.Warehouse.warehouse_id == new_warehouse_id
            ).first()
            
            if not warehouse:
                raise HTTPException(status_code=404, detail=f"Warehouse {new_warehouse_id} not found")
            
            if is_destination:
                leg.destination_warehouse_id = new_warehouse_id
            else:
                leg.origin_warehouse_id = new_warehouse_id
            
            # ✅ Recalculate distance
            distance = await DispatchService._calculate_leg_distance(db, leg)
            if distance:
                leg.estimated_distance = distance
            
            leg.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(leg)
            
            return leg
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error reassigning warehouse: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))