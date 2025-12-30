import requests
import time
import re
from typing import Optional, Tuple
import logging
import httpx
import os
from app.core.config import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Import Coordinates từ DirectionService để consistent
class Coordinates(BaseModel):
    """Schema tọa độ cơ bản"""
    latitude: float = Field(..., ge=-90, le=90, description="Vĩ độ")
    longitude: float = Field(..., ge=-180, le=180, description="Kinh độ")
    


# --- CÁC HÀM XỬ LÝ ĐỊA CHỈ (Giữ nguyên) ---

def _clean_address(address: str) -> str:
    """
    Tiền xử lý địa chỉ nhẹ nhàng (Giữ nguyên logic của bạn).
    """
    if not address or not address.strip():
        return ""
    
    cleaned = ' '.join(address.split()).strip()
    cleaned = re.sub(r'\s*,\s*', ', ', cleaned)
    cleaned = re.sub(r',+', ', ', cleaned)
    cleaned = re.sub(r',?\s*\d{5,6}\s*,?\s*$', '', cleaned)
    
    replacements = {
        r'\bĐ\.\s+': 'Đường ',
        r'\bP\.\s*(\d+)': r'Phường \1',
        r'\bQ\.\s*(\d+)': r'Quận \1',
        r'\bTP\.\s*': 'Thành phố ',
    }
    for pattern, replacement in replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned)
    
    city_replacements = {
        r'\bTPHCM\b': 'Thành phố Hồ Chí Minh',
        r'\bHCM\b(?!\s+City)': 'Hồ Chí Minh',
        r'\bSaigon\b': 'Hồ Chí Minh',
        r'\bHanoi\b': 'Hà Nội',
        r'\bDanang\b': 'Đà Nẵng',
    }
    for pattern, replacement in city_replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip()

def _add_vietnam_context(address: str) -> str:
    """
    Thêm context Việt Nam vào địa chỉ nếu cần thiết (Giữ nguyên).
    """
    lower_address = address.lower()
    vietnam_keywords = [
        'việt nam', 'vietnam', 'vn',
        'hồ chí minh', 'hcm', 'saigon',
        'hà nội', 'hanoi',
        'đà nẵng', 'danang',
        'cần thơ', 'hải phòng',
        'thành phố hồ chí minh'
    ]
    has_vietnam_context = any(keyword in lower_address for keyword in vietnam_keywords)
    
    if not has_vietnam_context:
        return f"{address}, Vietnam"
    return address

# --- HÀM TÌM TỌA ĐỘ (ĐÃ VIẾT LẠI HOÀN TOÀN) ---

async def get_coordinates_from_address(address: str, client: httpx.AsyncClient) -> Optional[Coordinates]:
    """
    Gọi OpenRouteService Geocoding API để lấy tọa độ từ địa chỉ.
    """
    try:
        api_key = settings.ORS_API_KEY
        
        logger.info(f"🌍 Starting geocoding for: {address}")
        logger.info(f"🔑 API Key status: {'Valid' if api_key and api_key != 'YOUR_ORS_API_KEY' else 'Missing/Invalid'}")
        
        if not api_key or api_key == "YOUR_ORS_API_KEY":
            logger.warning("❌ No valid ORS API key, using fallback geocoding")
            return _fallback_geocoding(address)
        
        # ORS Geocoding endpoint
        url = "https://api.openrouteservice.org/geocode/search"
        
        # Parameters theo ORS API docs
        params = {
            "api_key": api_key,
            "text": address,
            "size": 5,  # Lấy 5 kết quả để có nhiều lựa chọn
            "boundary.country": "VN",  # Chỉ tìm trong Việt Nam
            "layers": "address,venue"  # Tìm địa chỉ cụ thể
        }
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "SOA-LogisticsSystem/1.0"
        }
        
        logger.info(f"📍 Calling ORS Geocoding API for: {address}")
        
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        
        logger.info(f"📡 ORS API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            
            logger.info(f"🎯 Found {len(features)} geocoding results")
            
            if features:
                # Lấy kết quả tốt nhất (confidence score cao nhất)
                best_feature = features[0]
                
                for feature in features:
                    properties = feature.get("properties", {})
                    confidence = properties.get("confidence", 0)
                    logger.debug(f"  Result: {properties.get('label', 'Unknown')} (confidence: {confidence})")
                
                geometry = best_feature["geometry"]
                coordinates = geometry["coordinates"]  # [lon, lat] format từ ORS
                properties = best_feature.get("properties", {})
                
                longitude = coordinates[0]
                latitude = coordinates[1]
                confidence = properties.get("confidence", 0)
                label = properties.get("label", "Unknown location")
                
                # Validate coordinates cho Việt Nam
                if (8.0 <= latitude <= 23.5 and 102.0 <= longitude <= 110.0):  # Phạm vi Việt Nam
                    result = Coordinates(latitude=latitude, longitude=longitude)
                    logger.info(f"✅ REAL GEOCODING SUCCESS: {address}")
                    logger.info(f"   📍 Result: {label}")
                    logger.info(f"   📐 Coordinates: ({latitude:.6f}, {longitude:.6f})")
                    logger.info(f"   🎯 Confidence: {confidence}")
                    return result
                else:
                    logger.warning(f"⚠️ Coordinates outside Vietnam: lat={latitude}, lon={longitude}")
                    return _fallback_geocoding(address)
            else:
                logger.warning(f"❌ No geocoding results found for: {address}")
                return _fallback_geocoding(address)
                
        elif response.status_code == 400:
            error_text = response.text
            logger.error(f"❌ Geocoding API 400 Bad Request: {error_text}")
            return _fallback_geocoding(address)
            
        elif response.status_code == 401:
            logger.error("❌ Geocoding API 401 Unauthorized - check API key")
            return _fallback_geocoding(address)
            
        elif response.status_code == 403:
            logger.error("❌ Geocoding API 403 Forbidden - API key may be expired or quota exceeded")
            return _fallback_geocoding(address)
            
        elif response.status_code == 429:
            logger.error("❌ Geocoding API 429 Rate Limited")
            return _fallback_geocoding(address)
            
        else:
            logger.warning(f"❌ Geocoding API returned status {response.status_code}: {response.text[:200]}")
            return _fallback_geocoding(address)
            
    except httpx.TimeoutException:
        logger.warning("⏱️ Geocoding API timeout, using fallback")
        return _fallback_geocoding(address)
    except httpx.RequestError as e:
        logger.error(f"🌐 Geocoding API request error: {e}, using fallback")
        return _fallback_geocoding(address)
    except Exception as e:
        logger.error(f"💥 Unexpected error in geocoding: {e}, using fallback")
        return _fallback_geocoding(address)

def _fallback_geocoding(address: str) -> Optional[Coordinates]:
    """
    Fallback geocoding dựa trên pattern matching địa chỉ Việt Nam chi tiết.
    """
    try:
        address_lower = address.lower()
        
        logger.info(f"🔄 Using FALLBACK geocoding for: {address}")
        
        # === HỒ CHÍ MINH CITY PATTERNS (Chi tiết theo quận) ===
        hcm_district_coords = {
            # Các quận trung tâm
            r'quận 1': (10.7769, 106.7009),  # Quận 1
            r'quận 2': (10.7825, 106.7325),  # Quận 2 (cũ)
            r'quận 3': (10.7778, 106.6928),  # Quận 3
            r'quận 4': (10.7572, 106.7025),  # Quận 4
            r'quận 5': (10.7594, 106.6672),  # Quận 5
            r'quận 6': (10.7477, 106.6345),  # Quận 6
            r'quận 7': (10.7381, 106.7196),  # Quận 7 ⭐
            r'quận 8': (10.7505, 106.6776),  # Quận 8 ⭐
            r'quận 9': (10.8017, 106.7699),  # Quận 9 (cũ)
            r'quận 10': (10.7728, 106.6675), # Quận 10
            r'quận 11': (10.7635, 106.6500), # Quận 11
            r'quận 12': (10.8658, 106.6575), # Quận 12
            
            # Quận ngoại thành
            r'quận thủ đức': (10.8526, 106.7567),
            r'quận bình thạnh': (10.8015, 106.7108),
            r'quận tân bình': (10.8009, 106.6527),
            r'quận phú nhuận': (10.7980, 106.6834),
            r'quận gò vấp': (10.8376, 106.6834),
            r'quận bình tân': (10.7645, 106.6023),
            r'quận tân phú': (10.7874, 106.6296),
            
            # Địa danh cụ thể
            r'phú thuận': (10.7381, 106.7196),  # Phường Phú Thuận, Q7
            r'phạm nhữ tăng': (10.7505, 106.6776),  # Đường Phạm Nhữ Tăng, Q8
        }
        
        # Kiểm tra HCM patterns
        for pattern, coords in hcm_district_coords.items():
            if re.search(pattern, address_lower):
                logger.info(f"🎯 Matched HCM pattern '{pattern}': {address}")
                return Coordinates(latitude=coords[0], longitude=coords[1])
        
        # HCM general patterns
        hcm_general = [
            r'hồ chí minh', r'sài gòn', r'tphcm', r'tp\.hcm', r'ho chi minh'
        ]
        
        for pattern in hcm_general:
            if re.search(pattern, address_lower):
                logger.info(f"🎯 Matched general HCM pattern: {address}")
                return Coordinates(latitude=10.7769, longitude=106.7009)  # Trung tâm HCM
        
        # === HÀ NỘI PATTERNS ===
        hanoi_patterns = {
            r'hà nội|hanoi': (21.0285, 105.8542),
            r'ba đình': (21.0336, 105.8325),
            r'hoàn kiếm': (21.0285, 105.8542),
            r'hai bà trưng': (21.0158, 105.8542),
            r'đống đa': (21.0245, 105.8302),
            r'tây hồ': (21.0583, 105.8214),
            r'cầu giấy': (21.0328, 105.7938),
            r'thanh xuân': (20.9876, 105.8109),
        }
        
        for pattern, coords in hanoi_patterns.items():
            if re.search(pattern, address_lower):
                logger.info(f"🎯 Matched Hanoi pattern '{pattern}': {address}")
                return Coordinates(latitude=coords[0], longitude=coords[1])
        
        # === ĐÀ NẴNG PATTERNS ===
        danang_patterns = {
            r'đà nẵng|da nang': (16.0471, 108.2068),
            r'hải châu': (16.0545, 108.2207),
            r'thanh khê': (16.0739, 108.1967),
            r'sơn trà': (16.0761, 108.2468),
            r'ngũ hành sơn': (15.9695, 108.2461),
        }
        
        for pattern, coords in danang_patterns.items():
            if re.search(pattern, address_lower):
                logger.info(f"🎯 Matched Da Nang pattern '{pattern}': {address}")
                return Coordinates(latitude=coords[0], longitude=coords[1])
        
        # Default fallback to HCM
        logger.warning(f"🔄 No specific pattern matched, defaulting to HCM center: {address}")
        return Coordinates(latitude=10.7769, longitude=106.7009)
        
    except Exception as e:
        logger.error(f"💥 Error in fallback geocoding: {e}")
        # Absolute fallback
        return Coordinates(latitude=10.7769, longitude=106.7009)

# --- CÁC HÀM HỖ TRỢ (Giữ nguyên) ---

def batch_geocode_addresses(addresses: list[str], delay_seconds: float = 1.5) -> dict[str, Optional[Tuple[float, float]]]:
    """
    Geocode nhiều địa chỉ cùng lúc.
    Lưu ý: ORS có rate limit (vd: 40 req/phút), 
    delay 1.5s là an toàn.
    """
    results = {}
    
    for i, address in enumerate(addresses):
        logger.info(f"Geocoding address {i+1}/{len(addresses)}: {address}")
        # Đổi tên hàm
        results[address] = get_coordinates_from_address(address)
        
        if i < len(addresses) - 1:
            time.sleep(delay_seconds)
    
    return results

def validate_coordinates(lat: float, lon: float) -> bool:
    """Kiểm tra tọa độ có hợp lệ không."""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def is_vietnam_coordinates(lat: float, lon: float) -> bool:
    """Kiểm tra tọa độ có nằm trong lãnh thổ Việt Nam không (ước lượng)."""
    # Vĩ độ Bắc: 8.0 - 23.5
    # Kinh độ Đông: 102.0 - 110.0
    return 8.0 <= lat <= 23.5 and 102.0 <= lon <= 110.0

# --- Cập nhật hàm test ---
def test_address_geocoding():
    """
    Hàm test để kiểm tra việc geocoding bằng ORS.
    """
    # Địa chỉ cũ (Linh Đông) mà Nominatim đã thất bại
    test_addresses = [
        "82 Đường 36, Linh Đông, Thủ Đức, Thành phố Hồ Chí Minh, Việt Nam",
        "25 Đ. Số 10, Khu đô thị Sala, Thủ Đức, Thành phố Hồ Chí Minh 70000, Việt Nam",
        "793/57/16, Đ. Trần Xuân Soạn, Tân Hưng, Quận 7, Thành phố Hồ Chí Minh 700000, Việt Nam",
        "19 Đ. Nguyễn Hữu Thọ, Tân Hưng, Quận 7, Thành phố Hồ Chí Minh 758307, Việt Nam",
        "Dinh Độc Lập, 135 Nam Kỳ Khởi Nghĩa, Bến Thành, Quận 1, TPHCM"
    ]
    
    print("=== ORS Geocoding Test ===")
    print("Lưu ý: Đảm bảo file .env đã có ORS_API_KEY hợp lệ.")
    
    results = batch_geocode_addresses(test_addresses)
    
    print("\n=== Test Results ===")
    for addr, coords in results.items():
        print(f"Original: {addr}")
        if coords:
            print(f"Result:   ✅ {coords}")
        else:
            print(f"Result:   ❌ FAILED")
        print("-" * 80)

