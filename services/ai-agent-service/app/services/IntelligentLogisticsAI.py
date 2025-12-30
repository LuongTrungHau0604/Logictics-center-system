import asyncio
import datetime
import os
import httpx
import google.generativeai as genai
import json
import logging
import math
from typing import Dict, Any, List, Union
from openai import OpenAI
from groq import Groq
# Import models & settings
from app.core.config import settings
from app import models
from app.db.session import SessionLocal
from app.crud import crud_order, crud_shipper, crud_warehouse # Ensure crud_warehouse is imported

logger = logging.getLogger(__name__)


# =========================================================================
# 🛠️ HELPER: MATH DISTANCE (HAVERSINE)
# =========================================================================
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách đường chim bay (km) giữa 2 tọa độ.
    Dùng để lọc nhanh các shipper ở gần mà không tốn quota API Goong.
    """
    R = 6371  # Bán kính trái đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 2)


def find_nearest_shippers_tool(area_id: str, order_lat: float, order_lon: float, limit: int = 3) -> List[dict]:
    """
    Tìm Top N shipper gần vị trí lấy hàng nhất (SME) dựa trên tọa độ thời gian thực.
    """
    print(f"🎯 AGENT ACTION: Finding {limit} nearest shippers to ({order_lat}, {order_lon})...")
    
    # 1. Lấy danh sách tất cả shipper rảnh trong khu vực
    all_shippers = get_available_shippers_tool(area_id)
    
    if not all_shippers:
        return []

    ranked_shippers = []

    # 2. Tính khoảng cách cho từng shipper
    for shipper in all_shippers:
        dist_km = calculate_haversine_distance(
            shipper["current_lat"], shipper["current_lon"],
            order_lat, order_lon
        )
        
        # Chỉ lấy shipper trong bán kính hợp lý (ví dụ: < 15km)
        if dist_km < 15.0:
            ranked_shippers.append({
                "shipper_id": shipper["shipper_id"],
                "name": shipper["name"],
                "distance_km": dist_km,
                "current_lat": shipper["current_lat"],
                "current_lon": shipper["current_lon"]
            })

    # 3. Sắp xếp tăng dần theo khoảng cách (Gần nhất lên đầu)
    ranked_shippers.sort(key=lambda x: x["distance_km"])
    
    # 4. Trả về Top N
    top_candidates = ranked_shippers[:limit]
    
    # Cách 2 (Khuyên dùng): Tách biến ra cho dễ đọc
    results_str = [f"{s['name']} ({s['distance_km']}km)" for s in top_candidates]
    print(f"✅ Recommended: {results_str}")
    return top_candidates
# =========================================================================
# 🛠️ HELPER: GOONG DISTANCE MATRIX
# =========================================================================
def calculate_goong_matrix(origins: str, destinations: str, vehicle: str = "bike") -> dict:
    """
    Helper function to call Goong API.
    Returns the full JSON response or None on failure.
    """
    api_key = getattr(settings, "GOONG_API_KEY", None) or "YXQcYgieEF2tToSQG1IYwwxpS5yMUXJ0wh7sMALf"
    if not api_key:
        print("❌ Error: No Goong API Key.")
        return None

    url = "https://rsapi.goong.io/DistanceMatrix"
    params = {
        "api_key": api_key,
        "origins": origins,
        "destinations": destinations,
        "vehicle": vehicle
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Goong API Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"❌ Goong API Exception: {e}")
        return None

# =========================================================================
# 🛠️ AGENT TOOLS
# =========================================================================

def check_road_distance_tool(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """
    Calculates the actual road distance (km) between two coordinates using Goong.
    Used by the Agent to check Shipper <-> SME distance.
    """
    data = calculate_goong_matrix(f"{lat1},{lon1}", f"{lat2},{lon2}", "bike")
    
    if data:
        rows = data.get("rows", [])
        if rows:
            elements = rows[0].get("elements", [])
            if elements and elements[0].get("status") == "OK":
                dist_meters = elements[0].get("distance", {}).get("value", 0)
                return {"distance_km": round(dist_meters / 1000.0, 2)}
    
    return {"distance_km": 999.0}

def get_pending_orders_tool(area_id: str) -> Union[List[dict], str]:
    """Fetches pending orders and their SME pickup locations."""
    print(f"👀 AGENT EYES: Scanning database for pending orders in {area_id}...")
    db = SessionLocal()
    results = []
    try:
        orders = crud_order.get_pending_orders_by_area(db, area_id=area_id)
        
        # ✅ EARLY EXIT: Không có đơn hàng
        if not orders:
            return "SKIP_PHASE_1: No pending orders in this area. Proceed directly to Phase 2 (Transfer)."
        
        for order in orders:
            if order.sme and order.sme.latitude and order.sme.longitude:
                results.append({
                    "order_id": order.order_id,
                    "pickup_lat": float(order.sme.latitude),
                    "pickup_lon": float(order.sme.longitude),
                    "weight": float(order.weight) if order.weight else 1.0,
                })
        return results
    except Exception as e:
        print(f"❌ Error in get_pending_orders_tool: {e}")
        return "ERROR: Database query failed"
    finally:
        db.close()

def get_available_shippers_tool(area_id: str) -> List[dict]:
    """Finds available shippers (Motorbikes) in the area with REAL-TIME GPS."""
    print(f"🚚 AGENT ACTION: searching for available shippers in '{area_id}'...")
    db = SessionLocal()
    results = []
    try:
        shippers = crud_shipper.get_available_shippers_by_area(
            db, area_id=area_id, vehicle_type=models.VehicleType.MOTORBIKE
        )
        
        # Lấy thông tin Area để làm fallback nếu shipper chưa có GPS
        area = db.query(models.Area).filter(models.Area.area_id == area_id).first()
        default_lat = float(area.center_latitude) if area and area.center_latitude else 10.7769
        default_lon = float(area.center_longitude) if area and area.center_longitude else 106.7009

        for shipper in shippers:
            if not shipper.employee: continue
            
            # ✅ LOGIC MỚI: Ưu tiên lấy tọa độ Real-time của Shipper
            if shipper.current_latitude and shipper.current_longitude:
                lat = float(shipper.current_latitude)
                lon = float(shipper.current_longitude)
                source = "GPS"
            else:
                # Nếu không có, dùng tọa độ trung tâm Area
                lat = default_lat
                lon = default_lon
                source = "Default"

            results.append({
                "shipper_id": shipper.shipper_id,
                "name": shipper.employee.full_name,
                "current_lat": lat,
                "current_lon": lon,
                "vehicle": "MOTORBIKE",
                "location_source": source
            })
        
        print(f"✅ Found {len(results)} shippers in {area_id}.")
        return results
    finally:
        db.close()

# 🔥 UPDATED TOOL: SMART ASSIGNMENT WITH NEAREST HUB CALCULATION
def assign_order_tool(order_id: str, shipper_id: str) -> str:
    """
    Assigns an order to a shipper AND calculates the route to the NEAREST HUB.
    Uses Goong API to find the optimal Hub for the Pickup Leg.
    """
    print(f"✍️ AGENT ACTION: Assigning Order {order_id} to Shipper {shipper_id}...")
    
    db = SessionLocal()
    
    try:
        # 1. Fetch Order & Shipper
        order = db.get(models.Order, order_id)
        shipper = db.get(models.Shipper, shipper_id)
        
        if not order: return f"ERROR: Order {order_id} not found."
        if not shipper: return f"ERROR: Shipper {shipper_id} not found."
        
        # 2. Get SME Coordinates (Origin)
        if not order.sme or not order.sme.latitude or not order.sme.longitude:
            return "ERROR: Order SME has no coordinates."
        
        sme_lat = float(order.sme.latitude)
        sme_lon = float(order.sme.longitude)

        # 3. Find ALL Active Hubs
        hubs = db.query(models.Warehouse)\
            .filter(models.Warehouse.type == models.WarehouseType.HUB, 
                   models.Warehouse.status == models.WarehouseStatus.ACTIVE)\
            .all()
            
        if not hubs:
            return "ERROR: No active HUBs found in the system."

        # 4. Calculate Distance to ALL Hubs using Goong Matrix
        # Create destination string: "lat1,lon1|lat2,lon2|..."
        hub_coords = [f"{h.latitude},{h.longitude}" for h in hubs if h.latitude and h.longitude]
        
        if not hub_coords:
            return "ERROR: Hubs defined but missing coordinates."
            
        destinations_str = "|".join(hub_coords)
        origins_str = f"{sme_lat},{sme_lon}"

        print(f"🗺️ Calculating distance from SME ({origins_str}) to {len(hubs)} Hubs...")
        matrix_data = calculate_goong_matrix(origins_str, destinations_str, "bike")
        
        best_hub = None
        min_dist_meters = float('inf')

        if matrix_data:
            rows = matrix_data.get("rows", [])
            if rows:
                elements = rows[0].get("elements", [])
                # Iterate through results to find the nearest Hub
                for i, element in enumerate(elements):
                    if element.get("status") == "OK":
                        dist = element.get("distance", {}).get("value", float('inf'))
                        if dist < min_dist_meters:
                            min_dist_meters = dist
                            best_hub = hubs[i]

        # Fallback if API fails or no routes found
        if not best_hub:
            print("⚠️ Warning: Goong API failed to find route to Hubs. Defaulting to first Hub.")
            best_hub = hubs[0]
            min_dist_meters = 5000 # Default 5km

        dist_km = round(min_dist_meters / 1000.0, 2)
        print(f"✅ Optimal Entry Hub: {best_hub.name} (Distance: {dist_km} km)")

        # 5. Create Journey Legs
        entry_hub_id = best_hub.warehouse_id

        # LEG 1: PICKUP (SME -> Nearest Hub)
        pickup_leg = models.OrderJourneyLeg(
            order_id=order_id,
            assigned_shipper_id=shipper_id,
            sequence=1,
            leg_type=models.LegType.PICKUP,
            status=models.LegStatus.PENDING,
            origin_sme_id=order.sme_id,
            destination_warehouse_id=entry_hub_id,
            destination_is_receiver=False,
            estimated_distance=dist_km # Saved from Goong API
        )
        db.add(pickup_leg)
        
        # LEG 2: TRANSFER (Entry Hub -> Dest Hub)
        transfer_leg = models.OrderJourneyLeg(
            order_id=order_id,
            sequence=2,
            leg_type=models.LegType.TRANSFER,
            status=models.LegStatus.PENDING,
            origin_warehouse_id=entry_hub_id,
            destination_warehouse_id=entry_hub_id, # Will be updated by Middle Mile Agent later
            destination_is_receiver=False
        )
        db.add(transfer_leg)
        
        # LEG 3: DELIVERY (Dest Hub -> Receiver)
        delivery_leg = models.OrderJourneyLeg(
            order_id=order_id,
            sequence=3,
            leg_type=models.LegType.DELIVERY,
            status=models.LegStatus.PENDING,
            origin_warehouse_id=entry_hub_id,
            destination_is_receiver=True
        )
        db.add(delivery_leg)

        # 6. Update Status
        order.status = models.OrderStatus.IN_TRANSIT
        shipper.status = models.ShipperStatus.DELIVERING
        
        db.commit()
        return f"SUCCESS: Order assigned to {shipper.employee.full_name}. Routing to nearest hub: {best_hub.name}."

    except Exception as e:
        db.rollback()
        print(f"❌ Error in assign_order_tool: {e}")
        return f"ERROR: {str(e)}"
    finally:
        db.close()

# (Other Middle Mile tools remain the same as previously defined)
def get_hub_transfer_backlog_tool(hub_id: str) -> List[dict]:
    # ... (Same as your provided code) ...
    # For brevity, assuming you have this from your previous copy
    print(f"🏭 Checking backlog at {hub_id}...")
    db = SessionLocal()
    try:
        legs = db.query(models.OrderJourneyLeg).filter(
            models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER,
            models.OrderJourneyLeg.status == models.LegStatus.PENDING,
            models.OrderJourneyLeg.origin_warehouse_id == hub_id
        ).all()
        return [{"leg_id": l.id, "order_id": l.order_id, "dest": l.destination_warehouse_id} for l in legs]
    finally:
        db.close()

def get_available_trucks_tool(hub_id: str) -> List[dict]:
    # ... (Same as your provided code) ...
    print(f"🚛 Looking for trucks at {hub_id}...")
    db = SessionLocal()
    try:
        trucks = db.query(models.Shipper).join(models.Employee).filter(
            models.Shipper.vehicle_type == models.VehicleType.TRUCK,
            models.Shipper.status == models.ShipperStatus.ONLINE,
            models.Employee.warehouse_id == hub_id
        ).all()
        return [{"truck_id": t.shipper_id, "name": t.employee.full_name} for t in trucks]
    finally:
        db.close()

def assign_transfer_truck_tool(truck_id: str, leg_ids: List[int]) -> str:
    # ... (Same as your provided code) ...
    print(f"🏗️ Loading truck {truck_id}...")
    db = SessionLocal()
    try:
        truck = db.get(models.Shipper, truck_id)
        if not truck: return "Error"
        for leg_id in leg_ids:
            leg = db.get(models.OrderJourneyLeg, leg_id)
            if leg: leg.assigned_shipper_id = truck_id
        truck.status = models.ShipperStatus.DELIVERING
        db.commit()
        return "SUCCESS"
    finally:
        db.close()

def find_nearest_satellite_tool(receiver_lat: float, receiver_lon: float) -> dict:
    """Finds nearest Satellite using Goong Matrix."""
    print(f"📡 AGENT ACTION: API calculating nearest satellite...")
    db = SessionLocal()
    try:
        warehouses = crud_warehouse.get_all_active_warehouses(db)
        candidates = [w for w in warehouses if str(w.type) == "SATELLITE" and w.latitude]
        if not candidates: return {"error": "No satellites"}
        
        origins = f"{receiver_lat},{receiver_lon}"
        destinations = "|".join([f"{w.latitude},{w.longitude}" for w in candidates[:25]])
        
        data = calculate_goong_matrix(origins, destinations, "truck")
        if not data: return {"error": "API Error"}
        
        elements = data.get("rows", [])[0].get("elements", [])
        best_wh = None
        min_dist = float('inf')
        
        for i, el in enumerate(elements):
            if el.get("status") == "OK":
                val = el.get("distance", {}).get("value", float('inf'))
                if val < min_dist:
                    min_dist = val
                    best_wh = candidates[i]
                    
        if best_wh:
            return {"satellite_id": best_wh.warehouse_id, "name": best_wh.name, "dist_km": min_dist/1000}
        return {"error": "No route"}
    finally:
        db.close()

def route_orders_to_satellite_tool(order_ids: List[str], satellite_id: str) -> str:
    # ... (Same as your provided code) ...
    print(f"📍 Routing {len(order_ids)} orders...")
    db = SessionLocal()
    try:
        # Implementation to update destination_warehouse_id
        for oid in order_ids:
            leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == oid,
                models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER
            ).first()
            if leg: leg.destination_warehouse_id = satellite_id
        db.commit()
        return "SUCCESS"
    finally:
        db.close()

# =========================================================================
# 🧠 NEW TOOL: OPTIMIZE MIDDLE MILE (Hub -> Nearest Satellite)
# =========================================================================


def optimize_hub_routing_tool(hub_id: str = None) -> str:
    """
    Optimizes routing for pending Transfer Legs.
    If hub_id is None, it scans ALL Hubs (Global Mode).
    """
    target_msg = f"Hub {hub_id}" if hub_id else "ALL HUBS (Global Scan)"
    print(f"🧩 AGENT ACTION: Optimizing routes for {target_msg}...")
    
    db = SessionLocal()
    updated_count = 0
    hub_cache = {} 
    route_dist_cache = {} 

    try:
        satellites = db.query(models.Warehouse).filter(
            models.Warehouse.type == models.WarehouseType.SATELLITE,
            models.Warehouse.status == models.WarehouseStatus.ACTIVE
        ).all()
        
        if not satellites: return "ERROR: No active Satellites found in system."

        sat_coords = [f"{s.latitude},{s.longitude}" for s in satellites if s.latitude]
        sat_dest_str = "|".join(sat_coords)

        query = db.query(models.OrderJourneyLeg).filter(
            models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER,
            models.OrderJourneyLeg.status == models.LegStatus.PENDING
        )

        if hub_id:
            query = query.filter(models.OrderJourneyLeg.origin_warehouse_id == hub_id)
        
        pending_transfers = query.all()

        if not pending_transfers:
            return f"REPORT: No pending transfers found for {target_msg}."

        for leg in pending_transfers:
            order = db.get(models.Order, leg.order_id)
            if not order or not order.receiver_latitude: continue

            current_hub_id = leg.origin_warehouse_id
            if current_hub_id not in hub_cache:
                current_hub = db.get(models.Warehouse, current_hub_id)
                if current_hub:
                    hub_cache[current_hub_id] = current_hub
                else:
                    continue
            
            current_hub = hub_cache[current_hub_id]
            hub_origin_str = f"{current_hub.latitude},{current_hub.longitude}"
            rec_origin_str = f"{order.receiver_latitude},{order.receiver_longitude}"
            
            # Step A: Find Best Satellite (Receiver -> Satellites)
            matrix_data = calculate_goong_matrix(rec_origin_str, sat_dest_str, "truck")
            best_sat = None
            min_dist_meters = float('inf')

            if matrix_data and "rows" in matrix_data:
                elements = matrix_data["rows"][0].get("elements", [])
                for i, el in enumerate(elements):
                    if el.get("status") == "OK":
                        val = el.get("distance", {}).get("value", float('inf'))
                        if val < min_dist_meters:
                            min_dist_meters = val
                            best_sat = satellites[i]
            
            if best_sat:
                # Step B: Calculate Transfer Distance (Hub -> Best Satellite)
                cache_key = f"{current_hub.warehouse_id}_{best_sat.warehouse_id}"
                if cache_key in route_dist_cache:
                    transfer_dist_km = route_dist_cache[cache_key]
                else:
                    sat_loc = f"{best_sat.latitude},{best_sat.longitude}"
                    t_data = calculate_goong_matrix(hub_origin_str, sat_loc, "truck")
                    t_dist = 0
                    if t_data and "rows" in t_data:
                        els = t_data["rows"][0].get("elements", [])
                        if els and els[0].get("status") == "OK":
                            t_dist = els[0].get("distance", {}).get("value", 0)
                    transfer_dist_km = round(t_dist / 1000.0, 2)
                    route_dist_cache[cache_key] = transfer_dist_km
                
                leg.destination_warehouse_id = best_sat.warehouse_id
                leg.estimated_distance = transfer_dist_km 
                
                delivery_leg = db.query(models.OrderJourneyLeg).filter(
                    models.OrderJourneyLeg.order_id == leg.order_id,
                    models.OrderJourneyLeg.leg_type == models.LegType.DELIVERY
                ).first()
                if delivery_leg:
                    delivery_leg.origin_warehouse_id = best_sat.warehouse_id
                    delivery_leg.estimated_distance = round(min_dist_meters / 1000.0, 2)

                updated_count += 1

        db.commit()
        return f"SUCCESS: Optimized {updated_count} orders across {len(hub_cache)} Hubs."

    except Exception as e:
        db.rollback()
        return f"ERROR: {str(e)}"
    finally:
        db.close()
        
        
# =========================================================================
# ⚖️ NEW TOOL: REBALANCE SHIPPERS (Cross-Area Dispatch)
# =========================================================================

def rebalance_shippers_tool(overloaded_area_id: str, max_distance_km: float = 20.0) -> str:
    """
    Scans for IDLE shippers in NEARBY areas using Goong API and reassigns them to the overloaded area.
    
    Args:
        overloaded_area_id: The ID of the area needing help.
        max_distance_km: Maximum road distance to search for support (default 10km).
    """
    print(f"⚖️ AGENT ACTION: Rebalancing logic triggered for {overloaded_area_id} (Range: {max_distance_km}km)...")
    
    db = SessionLocal()
    moved_count = 0
    report = []

    try:
        # 1. Get Target Area Info
        target_area = db.query(models.Area).filter(models.Area.area_id == overloaded_area_id).first()
        if not target_area or not target_area.center_latitude or not target_area.center_longitude:
            return "ERROR: Target area not found or missing GPS."

        # 2. Get All Other Areas to check distances
        # We only get areas that have valid coordinates
        other_areas = db.query(models.Area).filter(
            models.Area.area_id != overloaded_area_id,
            models.Area.center_latitude.isnot(None),
            models.Area.center_longitude.isnot(None)
        ).all()
        
        if not other_areas:
            return "REPORT: No other areas available to check."

        # 3. Calculate Distances using Goong API
        candidates = []
        
        # Prepare Goong API strings
        origin_str = f"{target_area.center_latitude},{target_area.center_longitude}"
        
        # Note: Goong Matrix allows max 25 destinations per request usually. 
        # For safety in a real app, you might chunk this. Here we assume < 25 neighbors for simplicity.
        # If > 25, we take the first 25 or you need to implement chunking logic.
        batch_areas = other_areas[:25] 
        dest_coords = [f"{a.center_latitude},{a.center_longitude}" for a in batch_areas]
        dest_str = "|".join(dest_coords)

        # Call the helper function (Defined in your main file)
        matrix_data = calculate_goong_matrix(origin_str, dest_str, vehicle="bike")
        
        if matrix_data and "rows" in matrix_data:
            elements = matrix_data["rows"][0].get("elements", [])
            
            for i, element in enumerate(elements):
                if element.get("status") == "OK":
                    # Convert meters to km
                    distance_km = element.get("distance", {}).get("value", 99999) / 1000.0
                    
                    if distance_km <= max_distance_km:
                        candidates.append(batch_areas[i])
                        print(f"   -> Found neighbor: {batch_areas[i].name} ({distance_km:.2f} km away)")

        if not candidates:
            return f"REPORT: No neighboring areas found within {max_distance_km}km."

        # 4. Steal Idle Shippers from Valid Neighbors
        for neighbor in candidates:
            if moved_count >= 5: break # Cap at 5 shippers

            # Query SHIPPERS table directly (per your schema)
            idle_shippers = db.query(models.Shipper).filter(
                models.Shipper.area_id == neighbor.area_id,
                models.Shipper.status == models.ShipperStatus.ONLINE, # Must be ONLINE
                models.Shipper.vehicle_type == models.VehicleType.MOTORBIKE
            ).limit(2).all() # Take max 2 per neighbor

            for shipper in idle_shippers:
                # REASSIGN AREA (Update Shipper Table)
                previous_area = shipper.area_id
                shipper.area_id = target_area.area_id
                
                # Optional: Add log if you have an employee relationship for names
                shipper_name = shipper.shipper_id
                if shipper.employee:
                    shipper_name = shipper.employee.full_name
                    
                report.append(f"Moved {shipper_name} from {neighbor.name} -> {target_area.name}")
                moved_count += 1
        
        db.commit()
        
        if moved_count == 0:
            return f"REPORT: Neighbors found within {max_distance_km}km, but no IDLE shippers available."
            
        return f"SUCCESS: Rebalanced {moved_count} shippers to {target_area.name}. Details: {', '.join(report)}"

    except Exception as e:
        db.rollback()
        print(f"❌ Error in rebalance_shippers_tool: {e}")
        return f"ERROR: {str(e)}"
    finally:
        db.close()
        
def process_batch_assignments_tool(assignments: List[Dict[str, Any]]) -> str:
    """
    Hybrid Batch Assignment:
    1. Entry Restriction: Must enter via a HUB.
    2. Exit Restriction: Must exit via a SATELLITE.
    3. Dynamic Legs: Agent decides if a Transfer leg is needed (Entry != Exit).
    4. Distance Calculation: Calculates distance for ALL legs, including transfers.
    """
    print(f"⚡ AGENT ACTION: Hybrid Batch processing {len(assignments)} assignments...")
    
    db = SessionLocal()
    success_count = 0
    errors = []
    
    # --- CACHES ---
    # Prevents calling API 100 times for the same Hub->Satellite route
    transfer_dist_cache = {} 
    sme_to_hub_cache = {} 
    receiver_to_sat_cache = {}

    try:
        # 1. Fetch Candidates (Strict Separation)
        # Entry Candidates = HUBS ONLY
        hubs = db.query(models.Warehouse)\
            .filter(models.Warehouse.type == models.WarehouseType.HUB,
                    models.Warehouse.status == models.WarehouseStatus.ACTIVE).all()
            
        # Exit Candidates = SATELLITES ONLY
        satellites = db.query(models.Warehouse)\
            .filter(models.Warehouse.type == models.WarehouseType.SATELLITE,
                    models.Warehouse.status == models.WarehouseStatus.ACTIVE).all()
        
        valid_hubs = [h for h in hubs if h.latitude and h.longitude]
        valid_sats = [s for s in satellites if s.latitude and s.longitude]
        
        if not valid_hubs or not valid_sats:
            return "CRITICAL ERROR: Missing active HUBs or SATELLITES with GPS."

        # Prepare API strings (Limit 25 for batch safety)
        hub_dest_str = "|".join([f"{h.latitude},{h.longitude}" for h in valid_hubs[:25]])
        sat_dest_str = "|".join([f"{s.latitude},{s.longitude}" for s in valid_sats[:25]])

        # 2. Process Assignments
        for task in assignments:
            order_id = task.get("order_id")
            shipper_id = task.get("shipper_id")
            
            # --- Validation ---
            order = db.get(models.Order, order_id)
            shipper = db.get(models.Shipper, shipper_id)
            if not order or not shipper or not order.sme.latitude or not order.receiver_latitude:
                errors.append(f"Data Error: {order_id}")
                continue

            # --- A. Determine Entry Point (Nearest HUB) ---
            sme_loc_key = f"{order.sme.latitude},{order.sme.longitude}"
            entry_wh = None
            pickup_dist = 0.0

            if sme_loc_key in sme_to_hub_cache:
                entry_wh, pickup_dist = sme_to_hub_cache[sme_loc_key]
            else:
                # API: SME -> HUBs
                matrix = calculate_goong_matrix(sme_loc_key, hub_dest_str, "bike")
                if matrix and "rows" in matrix:
                    elements = matrix["rows"][0].get("elements", [])
                    best_idx, min_d = -1, float('inf')
                    for i, el in enumerate(elements):
                        if el.get("status") == "OK" and el["distance"]["value"] < min_d:
                            min_d = el["distance"]["value"]
                            best_idx = i
                    if best_idx != -1:
                        entry_wh = valid_hubs[best_idx]
                        pickup_dist = round(min_d / 1000.0, 2)
                        sme_to_hub_cache[sme_loc_key] = (entry_wh, pickup_dist)
            
            if not entry_wh: entry_wh = valid_hubs[0]

            # --- B. Determine Exit Point (Nearest SATELLITE) ---
            rec_loc_key = f"{order.receiver_latitude},{order.receiver_longitude}"
            exit_wh = None
            delivery_dist = 0.0

            if rec_loc_key in receiver_to_sat_cache:
                exit_wh, delivery_dist = receiver_to_sat_cache[rec_loc_key]
            else:
                # API: Receiver -> SATELLITEs
                matrix = calculate_goong_matrix(rec_loc_key, sat_dest_str, "bike")
                if matrix and "rows" in matrix:
                    elements = matrix["rows"][0].get("elements", [])
                    best_idx, min_d = -1, float('inf')
                    for i, el in enumerate(elements):
                        if el.get("status") == "OK" and el["distance"]["value"] < min_d:
                            min_d = el["distance"]["value"]
                            best_idx = i
                    if best_idx != -1:
                        exit_wh = valid_sats[best_idx]
                        delivery_dist = round(min_d / 1000.0, 2)
                        receiver_to_sat_cache[rec_loc_key] = (exit_wh, delivery_dist)

            if not exit_wh: exit_wh = valid_sats[0]

            # --- C. Dynamic Leg Decision ---
            
            legs_created = []
            
            # Leg 1: Pickup (SME -> Hub)
            l1 = models.OrderJourneyLeg(
                order_id=order_id,
                assigned_shipper_id=shipper_id,
                sequence=1,
                leg_type=models.LegType.PICKUP,
                status=models.LegStatus.PENDING,
                origin_sme_id=order.sme_id,
                destination_warehouse_id=entry_wh.warehouse_id,
                estimated_distance=pickup_dist
            )
            legs_created.append(l1)

            current_seq = 2
            
            # DECISION: Do we need a transfer? (Hub != Satellite)
            if entry_wh.warehouse_id != exit_wh.warehouse_id:
                
                # --- CALCULATE TRANSFER DISTANCE ---
                transfer_dist = 0.0
                cache_key = f"{entry_wh.warehouse_id}_{exit_wh.warehouse_id}"
                
                if cache_key in transfer_dist_cache:
                    transfer_dist = transfer_dist_cache[cache_key]
                else:
                    hub_loc = f"{entry_wh.latitude},{entry_wh.longitude}"
                    sat_loc = f"{exit_wh.latitude},{exit_wh.longitude}"
                    
                    # Call Goong API (Truck mode is better for Hub transfers)
                    t_matrix = calculate_goong_matrix(hub_loc, sat_loc, "truck")
                    
                    if t_matrix and "rows" in t_matrix:
                        elements = t_matrix["rows"][0].get("elements", [])
                        if elements and elements[0].get("status") == "OK":
                            val = elements[0].get("distance", {}).get("value", 0)
                            transfer_dist = round(val / 1000.0, 2)
                            
                            # Save to cache
                            transfer_dist_cache[cache_key] = transfer_dist

                # Leg 2: Transfer (Hub -> Satellite)
                l2 = models.OrderJourneyLeg(
                    order_id=order_id,
                    sequence=current_seq,
                    leg_type=models.LegType.TRANSFER,
                    status=models.LegStatus.PENDING,
                    origin_warehouse_id=entry_wh.warehouse_id,
                    destination_warehouse_id=exit_wh.warehouse_id,
                    destination_is_receiver=False,
                    estimated_distance=transfer_dist  # <--- FIXED: Distance added here
                )
                legs_created.append(l2)
                current_seq += 1

            # Leg 3 (or 2): Delivery (Satellite -> Receiver)
            l3 = models.OrderJourneyLeg(
                order_id=order_id,
                sequence=current_seq,
                leg_type=models.LegType.DELIVERY,
                status=models.LegStatus.PENDING,
                origin_warehouse_id=exit_wh.warehouse_id,
                destination_is_receiver=True,
                estimated_distance=delivery_dist
            )
            legs_created.append(l3)

            # Bulk Save
            for leg in legs_created:
                db.add(leg)

            # Update Status
            order.status = models.OrderStatus.IN_TRANSIT
            shipper.status = models.ShipperStatus.DELIVERING
            success_count += 1

        db.commit()
        return f"SUCCESS: Hybrid routed {success_count}/{len(assignments)} orders."

    except Exception as e:
        db.rollback()
        print(f"❌ Hybrid Batch Failed: {e}")
        return f"CRITICAL FAILURE: {str(e)}"
    finally:
        db.close()

def get_hub_transfer_queue_tool(hub_id: str) -> List[dict]:
    """
    Get a list of orders currently at the Hub waiting for TRANSFER.
    Only returns orders where PICKUP leg is COMPLETED (order is physically in warehouse).
    Returns destination info so the Agent can group them geographically.
    """
    print(f"🏭 AGENT: Scanning Hub {hub_id} for transfer-ready orders (PICKUP completed)...")
    db = SessionLocal()
    results = []
    try:
        # Lấy các chặng TRANSFER đang PENDING tại Hub này
        transfer_legs = db.query(models.OrderJourneyLeg).filter(
            models.OrderJourneyLeg.origin_warehouse_id == hub_id,
            models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER,
            models.OrderJourneyLeg.status == models.LegStatus.PENDING
        ).all()

        for leg in transfer_legs:
            # ✅ KIỂM TRA: Leg PICKUP phải đã COMPLETED (hàng đã ở kho)
            pickup_leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == leg.order_id,
                models.OrderJourneyLeg.leg_type == models.LegType.PICKUP,
                models.OrderJourneyLeg.status == models.LegStatus.COMPLETED
            ).first()
            
            if not pickup_leg:
                # Bỏ qua đơn này vì PICKUP chưa xong
                continue
            
            # Lấy thông tin đơn hàng
            order = db.get(models.Order, leg.order_id)
            if order:
                results.append({
                    "leg_id": leg.id,
                    "order_id": order.order_id,
                    "dest_warehouse": leg.destination_warehouse_id,
                    "receiver_address": order.receiver_address,
                    "weight": str(order.weight)
                })
        
        print(f"✅ Found {len(results)} orders ready for transfer at {hub_id}")
        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        db.close()
        
def assign_batch_to_truck_tool(truck_id: str, order_ids: List[str]) -> str:
    """
    Assign a batch of orders (Transfer Leg) to a single Truck.
    Only assigns orders where PICKUP is COMPLETED (physically in warehouse).
    Used for multi-stop routes (e.g., Hub -> Dist 1 -> Dist 4).
    NOTE: Status remains PENDING until driver scans barcode to start delivery.
    """
    print(f"📦 AGENT ACTION: Loading {len(order_ids)} orders onto Truck {truck_id}...")
    db = SessionLocal()
    count = 0
    skipped = []
    
    try:
        truck = db.get(models.Shipper, truck_id)
        if not truck: return "Error: Truck not found"

        for oid in order_ids:
            # ✅ KIỂM TRA: PICKUP phải đã COMPLETED
            pickup_leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == oid,
                models.OrderJourneyLeg.leg_type == models.LegType.PICKUP,
                models.OrderJourneyLeg.status == models.LegStatus.COMPLETED
            ).first()
            
            if not pickup_leg:
                skipped.append(oid)
                print(f"⚠️ Skipped {oid}: PICKUP not completed yet")
                continue
            
            # Tìm chặng Transfer của đơn này
            leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == oid,
                models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER,
                models.OrderJourneyLeg.status == models.LegStatus.PENDING
            ).first()

            if leg:
                leg.assigned_shipper_id = truck_id
                # ✅ GIỮ NGUYÊN STATUS = PENDING (chỉ assign, chưa chuyển hàng)
                # Status sẽ chuyển sang IN_PROGRESS khi tài xế scan barcode
                count += 1
        
        # ✅ Không thay đổi trạng thái truck ở đây
        # Truck status sẽ được cập nhật khi scan barcode lần đầu
        
        db.commit()
        
        result_msg = f"SUCCESS: Assigned {count}/{len(order_ids)} orders to Truck {truck.employee.full_name}. Awaiting scan to start."
        if skipped:
            result_msg += f" Skipped {len(skipped)} orders (PICKUP not completed)."
        
        return result_msg
        
    except Exception as e:
        db.rollback()
        return f"ERROR: {str(e)}"
    finally:
        db.close()

        
        
# --- TOOL MỚI: QUÉT ĐƠN TRANSFER TRÊN TOÀN BỘ AREA ---
def get_area_transfer_queue_tool(area_id: str) -> Union[List[dict], str]:
    """
    Scans ALL HUBS within a specific AREA to find pending transfer orders.
    Only returns orders where PICKUP leg is COMPLETED (order is physically in warehouse).
    Returns a list of orders grouped by their current Hub location.
    """
    print(f"🌐 AGENT: Scanning ALL HUBS in Area {area_id} for transfer-ready orders...")
    db = SessionLocal()
    results = []
    try:
        # 1. Tìm tất cả Hub thuộc Area này
        hubs = db.query(models.Warehouse).filter(
            models.Warehouse.area_id == area_id,
            models.Warehouse.type == models.WarehouseType.HUB
        ).all()
        
        hub_ids = [h.warehouse_id for h in hubs]
        
        if not hub_ids:
            return "REPORT: No Hubs found in this Area. Task Complete."

        # 2. Tìm tất cả đơn hàng đang nằm tại các Hub này chờ Transfer
        transfer_legs = db.query(models.OrderJourneyLeg).filter(
            models.OrderJourneyLeg.origin_warehouse_id.in_(hub_ids),
            models.OrderJourneyLeg.leg_type == models.LegType.TRANSFER,
            models.OrderJourneyLeg.status == models.LegStatus.PENDING
        ).limit(50).all()

        for leg in transfer_legs:
            # ✅ KIỂM TRA: Leg PICKUP phải đã COMPLETED
            pickup_leg = db.query(models.OrderJourneyLeg).filter(
                models.OrderJourneyLeg.order_id == leg.order_id,
                models.OrderJourneyLeg.leg_type == models.LegType.PICKUP,
                models.OrderJourneyLeg.status == models.LegStatus.COMPLETED
            ).first()
            
            if not pickup_leg:
                # Bỏ qua: hàng chưa được pickup xong, chưa ở kho
                continue
            
            order = db.get(models.Order, leg.order_id)
            current_hub = db.get(models.Warehouse, leg.origin_warehouse_id)
            
            if order and current_hub:
                results.append({
                    "leg_id": leg.id,
                    "order_id": order.order_id,
                    "current_hub_id": current_hub.warehouse_id,
                    "current_hub_name": current_hub.name,
                    "weight": float(order.weight) if order.weight else 1.0,
                    "destination_hub": leg.destination_warehouse_id
                })
        
        if not results:
            print(f"✅ AGENT: No transfer-ready orders in {area_id} (all PICKUP legs incomplete).")
            return "REPORT: No pending transfer orders found in this Area. Process Completed."

        print(f"✅ Found {len(results)} transfer-ready orders across {len(hub_ids)} Hubs")
        return results
        
    finally:
        db.close()
        
# --- TOOL MỚI: TÌM XE TẢI THUỘC AREA ---
def get_trucks_in_area_tool(area_id: str) -> List[dict]:
    """
    Find available TRUCKS that belong to this AREA (not just a specific Hub).
    """
    print(f"🚛 AGENT: Finding trucks managed by Area {area_id}...")
    db = SessionLocal()
    results = []
    try:
        trucks = db.query(models.Shipper).filter(
            models.Shipper.vehicle_type == models.VehicleType.TRUCK,
            models.Shipper.status == models.ShipperStatus.ONLINE,
            models.Shipper.area_id == area_id # Quan trọng: Xe thuộc Area
        ).all()

        for truck in trucks:
            # Giả sử max capacity là 1000kg
            results.append({
                "truck_id": truck.shipper_id,
                "driver_name": truck.employee.full_name if truck.employee else "Driver",
                "max_capacity_kg": 1000.0 
            })
        return results
    finally:
        db.close()
        
# Tool này dùng để xử lý sự cố bất ngờ từ Shipper
def report_incident_tool(shipper_id: str, incident_description: str, current_lat: float, current_lon: float) -> str:
    """
    Phiên bản có Log chi tiết để Debug lỗi không tìm thấy đơn hàng.
    """
    print(f"\n🚨 [START] Handling incident for {shipper_id}...")
    print(f"   - Reason: {incident_description}")
    print(f"   - Location: {current_lat}, {current_lon}")
    
    db = SessionLocal()
    try:
        # 1. Kiểm tra xem Shipper có tồn tại không
        shipper = db.get(models.Shipper, shipper_id)
        if not shipper:
            print(f"❌ [STOP] Shipper ID '{shipper_id}' not found in DB!")
            return f"ERROR: Shipper {shipper_id} does not exist."

        # 2. Tìm các đơn hàng shipper này đang giữ
        # Log ra câu query để kiểm tra
        print(f"🔍 [SCAN] Searching active legs for shipper: {shipper_id}...")
        
        active_legs = db.query(models.OrderJourneyLeg).filter(
            models.OrderJourneyLeg.assigned_shipper_id == shipper_id,
            models.OrderJourneyLeg.status.in_([models.LegStatus.IN_PROGRESS, models.LegStatus.PENDING])
        ).all()
        
        print(f"   -> Found {len(active_legs)} active orders.")

        if not active_legs:
            # 🛑 ĐÂY LÀ CHỖ NÓ DỪNG LẠI Ở TRƯỜNG HỢP CỦA BẠN
            print("🛑 [STOP] No active orders found. Setting shipper to OFFLINE only.")
            
            shipper.status = models.ShipperStatus.OFFLINE
            db.commit()
            return "REPORT: Shipper has no active orders. Status updated to OFFLINE. No rescue needed."

        # 3. Tìm Shipper cứu hộ
        print(f"🚑 [SEARCH] Looking for rescuers near ({current_lat}, {current_lon})...")
        
        # Gọi trực tiếp logic tìm shipper (không qua AI để tránh loop)
        # Lưu ý: Đảm bảo bạn đã import hàm này
        rescuers = find_nearest_shippers_tool(
            area_id=shipper.area_id if shipper.area_id else "AREA-UNKNOWN",
            order_lat=current_lat, 
            order_lon=current_lon, 
            limit=3
        )
        
        # Lọc bỏ chính shipper đang gặp nạn ra khỏi danh sách cứu hộ
        rescuers = [r for r in rescuers if r['shipper_id'] != shipper_id]
        
        if not rescuers:
            print("⚠️ [WARNING] No rescuers found nearby!")
            return "CRITICAL WARNING: No rescuers found nearby! Please contact Admin manually."
            
        rescuer = rescuers[0] # Lấy người gần nhất
        print(f"✅ [FOUND] Rescuer found: {rescuer['name']} (ID: {rescuer['shipper_id']}) - Distance: {rescuer['distance_km']}km")
        
        # 4. Chuyển đơn hàng
        print("🔄 [TRANSFER] Reassigning orders...")
        count = 0
        for leg in active_legs:
            old_status = leg.status
            leg.assigned_shipper_id = rescuer['shipper_id']
            leg.note = f"EMERGENCY TRANSFER: From {shipper_id} ({incident_description})"
            print(f"   - Order {leg.order_id}: {shipper_id} -> {rescuer['shipper_id']} (Status: {old_status})")
            count += 1
            
        # 5. Cập nhật trạng thái
        shipper.status = models.ShipperStatus.OFFLINE
        db.commit()
        
        print(f"🏁 [DONE] Successfully transferred {count} orders.\n")
        return (
            f"🚨 Đã nhận báo cáo sự cố '{incident_description}'!\n"
            f"Hệ thống đã điều phối đồng nghiệp {rescuer['name']} (cách bạn {rescuer['distance_km']}km) "
            f"đến hỗ trợ lấy {count} đơn hàng.\n"
            f"Bạn đã được chuyển sang chế độ OFFLINE để yên tâm xử lý sự cố. Giữ an toàn nhé!"
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ [ERROR] Exception: {str(e)}")
        return f"ERROR handling incident: {str(e)}"
    finally:
        db.close()
# =========================================================================
# 1. ĐỊNH NGHĨA TOOLS (SCHEMA)
# OpenAI cần biết input/output của hàm trông như thế nào
# =========================================================================
TOOLS_SCHEMA = [
    # --- LAST MILE TOOLS ---
    {
        "type": "function",
        "function": {
            "name": "report_incident_tool",
            "description": "Handle real-time incidents (broken vehicle, accident). Reassigns orders to nearest rescuers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shipper_id": {"type": "string"},
                    "incident_description": {"type": "string", "description": "Short description (e.g. 'Flat tire')"},
                    "current_lat": {"type": "number"},
                    "current_lon": {"type": "number"}
                },
                "required": ["shipper_id", "incident_description", "current_lat", "current_lon"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_orders_tool",
            "description": "Get list of pending orders in a specific area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {"type": "string", "description": "The Area ID (e.g., AREA-001)"}
                },
                "required": ["area_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_shippers_tool",
            "description": "Get list of idle motorbikes in a specific area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {"type": "string"}
                },
                "required": ["area_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_batch_assignments_tool",
            "description": "Execute batch assignment matching orders to shippers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "assignments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string"},
                                "shipper_id": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["assignments"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rebalance_shippers_tool",
            "description": "Move shippers from nearby areas to the overloaded area using Goong Distance API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "overloaded_area_id": {"type": "string"},
                    "max_distance_km": {"type": "number", "description": "Maximum search radius (default 20km)"}
                },
                "required": ["overloaded_area_id"]
            }
        }
    },
    # --- MIDDLE MILE TOOLS ---
    {
        "type": "function",
        "function": {
            "name": "get_area_transfer_queue_tool",
            "description": "Scan all Hubs in an Area to find orders waiting for transfer (only returns orders where PICKUP is completed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {"type": "string", "description": "The Area ID to scan."}
                },
                "required": ["area_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hub_transfer_queue_tool",
            "description": "Get pending transfer orders at a specific Hub (only returns orders where PICKUP is completed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "hub_id": {"type": "string"}
                },
                "required": ["hub_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trucks_in_area_tool",
            "description": "Find available trucks assigned to a specific Area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {"type": "string"}
                },
                "required": ["area_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_trucks_tool",
            "description": "Find available trucks at a specific Hub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hub_id": {"type": "string"}
                },
                "required": ["hub_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assign_batch_to_truck_tool",
            "description": "Assign multiple orders to one truck for a consolidated route. Only assigns orders where PICKUP is completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "truck_id": {"type": "string"},
                    "order_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Order IDs to load onto the truck."
                    }
                },
                "required": ["truck_id", "order_ids"]
            }
        }
    },
    # --- OPTIMIZATION TOOLS ---
    {
        "type": "function",
        "function": {
            "name": "optimize_hub_routing_tool",
            "description": "Optimize routing for Hub transfers using Goong API to find nearest Satellites.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hub_id": {"type": "string", "description": "Hub ID or null for global optimization"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_nearest_shippers_tool",
            "description": "Find the nearest available shippers to a specific coordinate (Pickup Location). Returns a sorted list by distance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {"type": "string"},
                    "order_lat": {"type": "number"},
                    "order_lon": {"type": "number"},
                    "limit": {"type": "integer", "description": "Number of shippers to return (default 3)"}
                },
                "required": ["area_id", "order_lat", "order_lon"]
            }
        }
    }
]

class IntelligentLogisticsAI:
    def __init__(self):
        # API Key
        openai_api_key = settings.OPENAI_API_KEY 
        self.client = OpenAI(api_key=openai_api_key)
        self.model_name = "gpt-4o-mini"

        # BẢN ĐỒ HÀM - Mapping function names to actual Python functions
        self.available_functions = {
            # --- Incident Tools ---
            "report_incident_tool": report_incident_tool, # <--- MAPPING MỚI

            # --- Last Mile Tools ---
            "get_pending_orders_tool": get_pending_orders_tool,
            "get_available_shippers_tool": get_available_shippers_tool,
            "process_batch_assignments_tool": process_batch_assignments_tool,
            "rebalance_shippers_tool": rebalance_shippers_tool,
            
            # --- Middle Mile Tools ---
            "get_area_transfer_queue_tool": get_area_transfer_queue_tool,
            "get_hub_transfer_queue_tool": get_hub_transfer_queue_tool,
            "get_trucks_in_area_tool": get_trucks_in_area_tool,
            "get_available_trucks_tool": get_available_trucks_tool,
            "assign_batch_to_truck_tool": assign_batch_to_truck_tool,
            "find_nearest_shippers_tool": find_nearest_shippers_tool,
            # --- Optimization Tools ---
            "optimize_hub_routing_tool": optimize_hub_routing_tool,
        }

        # 🔥 SYSTEM PROMPT: CẬP NHẬT LOGIC XỬ LÝ SỰ CỐ
        self.system_instruction = """
            You are an Intelligent Logistics Coordinator AI Agent.
            Your mission: Optimize Logistics Operations AND Handle Emergency Incidents.
            
            🚨 PRIORITY 0: EMERGENCY INCIDENT HANDLING
            IF the user input describes a problem (e.g., "broken bike", "accident", "cannot deliver", "flat tire"):
                → STOP all standard optimization phases.
                → IMMEDIATELY extract details and call `report_incident_tool`.
                → Do NOT ask for more info. Use the provided context (shipper_id, lat, lon).
                → After handling, report the result and END the session.

            ═══════════════════════════════════════════════════════════════════════
            📋 STANDARD EXECUTION PLAN (Only if NO incident is reported)
            ═══════════════════════════════════════════════════════════════════════
            
            🚨 EXECUTION RULES (STRICT):
            1. PHASE 1 (First Mile):
               - Call `get_pending_orders_tool`.
               - If result is "SKIP_PHASE_1" -> IMMEDIATELY proceed to Phase 2. DO NOT call `get_available_shippers_tool`.
               - If orders exist -> Call `find_nearest_shippers_tool` -> Then `process_batch_assignments_tool`.
               - ONCE ASSIGNMENTS ARE MADE, Phase 1 is COMPLETE.
            
            2. PHASE 2 (Middle Mile):
               - Call `get_area_transfer_queue_tool`.
               - If result contains "No pending transfer" -> STOP. Phase 2 is COMPLETE.
               - If orders exist -> Call `get_trucks_in_area_tool` -> Then `assign_batch_to_truck_tool`.
            
            3. GENERAL:
               - DO NOT call the same tool twice with the same arguments.
               - If you have completed the tasks for both phases, output the exact phrase: "ALL TASKS COMPLETED".
               - Be concise. Do not output filler text like "I will now proceed...". Just call the tools.
            
            [... Giữ nguyên phần hướng dẫn Phase 1 và Phase 2 cũ ở đây để Agent biết cách làm việc bình thường ...]
            """

    async def run_logistics_optimization(self, target_id: str = None, user_message: str = None, context_data: dict = None):
        """
        Updated Run Method to handle both Optimization and Incidents.
        Args:
            target_id: Area ID (for optimization).
            user_message: Text from Shipper (for incidents).
            context_data: Dict containing {shipper_id, lat, lon} (for incidents).
        """
        logger.info(f"🚀 NATIVE AGENT ({self.model_name}) STARTING. Target: {target_id}, Msg: {user_message}")
        
        messages = [{"role": "system", "content": self.system_instruction}]
        
        # --- XỬ LÝ INPUT LINH HOẠT ---
        if user_message and context_data:
            # Chế độ Xử lý sự cố (Incident Mode)
            incident_prompt = f"""
            URGENT INCIDENT REPORT:
            - Message: "{user_message}"
            - Shipper ID: {context_data.get('shipper_id')}
            - Current Location: {context_data.get('lat')}, {context_data.get('lon')}
            
            Action: Handle this immediately.
            """
            messages.append({"role": "user", "content": incident_prompt})
        
        elif target_id:
            # Chế độ Tối ưu hóa (Optimization Mode)
            messages.append({
                "role": "user", 
                "content": f"Target: {target_id}. Execute Phase 1 & Phase 2 immediately."
            })
        else:
            messages.append({"role": "user", "content": "Global Mode. Start."})

        final_report = ""
        MAX_TURNS = 6 
        phase1_done = False
        phase2_done = False

        try:
            for turn in range(MAX_TURNS):
                logger.info(f"⚡ Turn {turn + 1}/{MAX_TURNS}...")

                # 1. GỌI OPENAI
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=TOOLS_SCHEMA,
                    tool_choice="auto",
                    temperature=0.0
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # A. NẾU AGENT MUỐN GỌI TOOL
                if tool_calls:
                    messages.append(response_message)
                    
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"🔧 Executing: {function_name}")
                        
                        function_to_call = self.available_functions.get(function_name)
                        if function_to_call:
                            try:
                                function_result = function_to_call(**function_args)
                                function_response = str(function_result)
                                
                                # --- 🧠 LOGIC DỪNG SỚM (SMART STOP) ---
                                
                                # 1. Kiểm tra Phase 1
                                if function_name == "get_pending_orders_tool":
                                    if "SKIP_PHASE_1" in function_response:
                                        logger.info("⏩ Phase 1 Empty. Auto-skipping to Phase 2.")
                                        phase1_done = True
                                
                                if function_name == "process_batch_assignments_tool":
                                    logger.info("✅ Phase 1 Assignments Executed.")
                                    phase1_done = True

                                # 2. Kiểm tra Phase 2
                                if function_name == "get_area_transfer_queue_tool":
                                    if "No pending transfer" in function_response or "No transfer-ready" in function_response:
                                        logger.info("⏩ Phase 2 Empty. Done.")
                                        phase2_done = True
                                        
                                if function_name == "assign_batch_to_truck_tool":
                                    logger.info("✅ Phase 2 Truck Assigned.")
                                    phase2_done = True
                                    
                                # 3. Kiểm tra Incident
                                if function_name == "report_incident_tool":
                                    logger.info("✅ Incident Handled. Stopping Agent.")
                                    return {
                                        "status": "SUCCESS",
                                        "agent_report": f"INCIDENT RESOLVED: {function_response}",
                                        "history_length": len(messages)
                                    }

                            except Exception as e:
                                function_response = f"Error: {str(e)}"
                        else:
                            function_response = "Error: Function not found"
                            
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        })
                        final_report += f"- {function_name}: {function_response[:50]}...\n"

                    # 🚨 CHECKPOINT: Nếu Optimization Mode xong -> Break
                    if phase1_done and phase2_done and not user_message:
                        logger.info("🏁 AUTO-STOP: Both phases completed based on tool outputs.")
                        break

                # B. NẾU AGENT CHỈ TRẢ LỜI TEXT (KHÔNG GỌI TOOL)
                else:
                    agent_text = response_message.content
                    messages.append({"role": "assistant", "content": agent_text})
                    
                    if "completed" in agent_text.lower() or "done" in agent_text.lower():
                        logger.info("🏁 Agent signaled completion.")
                        break
                    
                    if phase1_done and phase2_done:
                        break

            return {
                "status": "SUCCESS",
                "agent_report": final_report,
                "history_length": len(messages)
            }

        except Exception as e:
            logger.error(f"❌ Agent Error: {e}")
            return {"status": "ERROR", "agent_report": str(e)}