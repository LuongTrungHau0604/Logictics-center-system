import httpx
import logging
from typing import Optional
from app.core.config import settings
from app.schemas.ai_schemas import Coordinates

logger = logging.getLogger(__name__)

async def get_route_distance(
    coord1: Coordinates, 
    coord2: Coordinates, 
    client: httpx.AsyncClient,
    vehicle_type: str = "car" # Mặc định là 'car' nếu không truyền
) -> float:
    """
    Gọi Goong.io Distance Matrix API để lấy khoảng cách thực tế.
    
    Args:
        coord1: Tọa độ điểm xuất phát.
        coord2: Tọa độ điểm đến.
        client: httpx Client.
        vehicle_type: Loại xe trong DB (VD: 'TRUCK', 'MOTORBIKE'). 
                      Hàm sẽ tự convert sang format của Goong.
    """
    try:
        # 1. Lấy API Key
        api_key = getattr(settings, "GOONG_API_KEY", None) or getattr(settings, "ORS_API_KEY", None)
        
        if not api_key or "YOUR" in api_key:
            logger.error("❌ API Key is not configured.")
            raise ValueError("API Key missing.")
        
        # 2. Xử lý Mapping loại xe (Database -> Goong API)
        # DB của bạn: 'TRUCK', 'MOTORBIKE'
        # Goong API: 'truck', 'bike', 'car', 'taxi', 'hd'
        
        vehicle_map = {
            "TRUCK": "truck",
            "MOTORBIKE": "bike",
            "MOTO": "bike",      # Phòng hờ
            "XE_MAY": "bike",    # Phòng hờ
            "CAR": "car",
            "OTO": "car",
            "VAN": "truck"
        }
        
        # Chuẩn hóa input đầu vào (chuyển về chữ hoa, xóa khoảng trắng)
        input_type = str(vehicle_type).upper().strip() if vehicle_type else "CAR"
        
        # Lấy giá trị map được, nếu không có thì mặc định là 'car'
        goong_vehicle = vehicle_map.get(input_type, "car")

        logger.debug(f"🚚 Routing vehicle: '{vehicle_type}' -> mapped to Goong: '{goong_vehicle}'")

        # 3. Cấu hình Request
        url = "https://rsapi.goong.io/DistanceMatrix"
        
        origin_str = f"{coord1.latitude},{coord1.longitude}"
        dest_str = f"{coord2.latitude},{coord2.longitude}"
        
        params = {
            "api_key": api_key,
            "origins": origin_str,
            "destinations": dest_str,
            "vehicle": goong_vehicle # <--- Tham số mới
        }
        
        # 4. Gọi API
        response = await client.get(url, params=params, timeout=15.0)
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get("rows", [])
            
            if rows:
                elements = rows[0].get("elements", [])
                if elements:
                    element = elements[0]
                    status = element.get("status")
                    
                    if status == "OK":
                        distance_meters = element.get("distance", {}).get("value", 0)
                        distance_km = distance_meters / 1000.0
                        
                        logger.info(f"✅ Route ({goong_vehicle}): {distance_km:.2f}km")
                        return distance_km
                    
                    elif status == "ZERO_RESULTS":
                        # Với xe máy/bike, đôi khi đi cao tốc sẽ không tìm thấy đường
                        logger.warning(f"⚠️ No route found for {goong_vehicle}. Ensure coordinates are reachable.")
                        raise ValueError(f"No route found for vehicle {goong_vehicle}")
                    else:
                        raise ValueError(f"Goong API Status: {status}")
            
            raise ValueError("Invalid Goong API response format")

        else:
            error_text = response.text
            logger.error(f"❌ Goong API Error {response.status_code}: {error_text}")
            raise Exception(f"Goong API Error {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error in Routing API: {e}")
        raise e