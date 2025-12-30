import logging
import re
import asyncio
import httpx
from typing import Optional, Tuple, Dict, Any
from app.core.config import settings
from app.schemas.ai_schemas import Coordinates

logger = logging.getLogger(__name__)

# --- 1. CÁC HÀM HỖ TRỢ (UTILS) ---

def _clean_address(address: str) -> str:
    """Chuẩn hóa địa chỉ đầu vào để tăng độ chính xác."""
    if not address or not address.strip():
        return ""
    
    cleaned = ' '.join(address.split()).strip()
    cleaned = re.sub(r'\s*,\s*', ', ', cleaned)
    cleaned = re.sub(r',+', ', ', cleaned)
    
    # Chuẩn hóa một số từ viết tắt thông dụng ở VN
    replacements = {
        r'\bĐ\.\s+': 'Đường ',
        r'\bP\.\s*(\d+)': r'Phường \1',
        r'\bQ\.\s*(\d+)': r'Quận \1',
        r'\bTP\.\s*': 'Thành phố ',
    }
    for pattern, replacement in replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned)
        
    return cleaned.strip()

def is_vietnam_coordinates(lat: float, lon: float) -> bool:
    """Kiểm tra tọa độ có nằm trong lãnh thổ VN không."""
    return 8.0 <= lat <= 23.5 and 102.0 <= lon <= 110.0

def _get_api_key() -> str:
    """Lấy API Key ưu tiên Goong, fallback về ORS cũ nếu cần."""
    key = getattr(settings, "GOONG_API_KEY", None) or getattr(settings, "ORS_API_KEY", None)
    if not key or "YOUR" in key:
        logger.warning("❌ No valid API Key found.")
        return ""
    return key

# --- 2. CÁC HÀM CORE GEOCODING (GOONG.IO) ---

async def get_coordinates_from_address(address: str, client: httpx.AsyncClient) -> Optional[Coordinates]:
    """
    Cách 1: Lấy tọa độ từ địa chỉ (Geocoding).
    URL: /Geocode?address=...
    """
    cleaned_address = _clean_address(address)
    if not cleaned_address:
        return None

    api_key = _get_api_key()
    if not api_key: return None

    try:
        url = "https://rsapi.goong.io/Geocode"
        params = {
            "api_key": api_key,
            "address": cleaned_address,
        }
        
        response = await client.get(url, params=params, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                # Goong trả về array, lấy kết quả đầu tiên tin cậy nhất
                best = results[0]
                loc = best.get("geometry", {}).get("location", {})
                lat, lng = loc.get("lat"), loc.get("lng")
                
                if lat and lng and is_vietnam_coordinates(lat, lng):
                    return Coordinates(latitude=lat, longitude=lng)
                    
        return None

    except Exception as e:
        logger.error(f"Error in geocoding address '{address}': {e}")
        return None

async def get_coordinates_by_place_id(place_id: str, client: httpx.AsyncClient) -> Optional[Coordinates]:
    """
    Cách 2: Lấy tọa độ từ Place ID (Dùng kết hợp sau khi Autocomplete).
    URL: /Geocode?place_id=...
    """
    api_key = _get_api_key()
    if not api_key: return None

    try:
        url = "https://rsapi.goong.io/Geocode"
        params = {
            "api_key": api_key,
            "place_id": place_id,
        }

        response = await client.get(url, params=params, timeout=10.0)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                loc = results[0].get("geometry", {}).get("location", {})
                lat, lng = loc.get("lat"), loc.get("lng")
                
                if lat and lng:
                    return Coordinates(latitude=lat, longitude=lng)
        return None

    except Exception as e:
        logger.error(f"Error getting place details for '{place_id}': {e}")
        return None

async def get_address_suggestions(text: str, client: httpx.AsyncClient) -> list[dict]:
    """
    Autocomplete: Trả về gợi ý địa điểm & Place ID.
    URL: /Place/AutoComplete
    """
    if not text or len(text) < 2:
        return []

    api_key = _get_api_key()
    if not api_key: return []

    try:
        url = "https://rsapi.goong.io/Place/AutoComplete"
        params = {
            "api_key": api_key,
            "input": text,
            "limit": 5,
        }

        response = await client.get(url, params=params, timeout=5.0)

        if response.status_code == 200:
            predictions = response.json().get("predictions", [])
            results = []
            for pred in predictions:
                results.append({
                    "label": pred.get("description", ""),
                    "place_id": pred.get("place_id"),
                    # Autocomplete Goong KHÔNG trả lat/long ngay.
                    # Frontend cần dùng place_id gọi tiếp hàm get_coordinates_by_place_id
                    "latitude": None, 
                    "longitude": None 
                })
            return results
        return []

    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return []

# --- 3. BATCH & WRAPPERS (Giữ lại để tương thích logic cũ) ---

async def async_batch_geocode_addresses(
    addresses: list[str], 
    delay_seconds: float = 0.2
) -> dict[str, Optional[Coordinates]]:
    """Xử lý hàng loạt địa chỉ (Async)."""
    results = {}
    async with httpx.AsyncClient(timeout=20.0) as client:
        for i, address in enumerate(addresses):
            results[address] = await get_coordinates_from_address(address, client)
            if i < len(addresses) - 1:
                await asyncio.sleep(delay_seconds)
    return results

def get_coordinates(address: str) -> Optional[Tuple[float, float]]:
    """
    Sync Wrapper (Chỉ giữ lại nếu code cũ còn dùng).
    """
    try:
        async def _run():
            async with httpx.AsyncClient() as client:
                res = await get_coordinates_from_address(address, client)
                return (res.latitude, res.longitude) if res else None
                
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Nếu đang trong loop async mà gọi hàm sync này thì rất nguy hiểm
                # Tốt nhất nên refactor code gọi sang dùng async/await
                return None 
            return loop.run_until_complete(_run())
        except RuntimeError:
            return asyncio.run(_run())
    except Exception:
        return None
# --- Thêm vào file app/services/GeocodingService.py ---

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Kiểm tra tọa độ có hợp lệ về mặt toán học không.
    Latitude: -90 đến 90
    Longitude: -180 đến 180
    """
    try:
        return -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (ValueError, TypeError):
        return False

def is_vietnam_coordinates(lat: float, lon: float) -> bool:
    """
    Kiểm tra tọa độ có nằm trong lãnh thổ Việt Nam không (ước lượng).
    Giúp loại bỏ các kết quả sai (ví dụ: địa chỉ ở Mỹ hoặc nước khác).
    """
    try:
        # Vĩ độ (Lat) Việt Nam: khoảng 8.0 đến 23.5
        # Kinh độ (Lon) Việt Nam: khoảng 102.0 đến 110.0
        return 8.0 <= float(lat) <= 23.5 and 102.0 <= float(lon) <= 110.0
    except (ValueError, TypeError):
        return False

