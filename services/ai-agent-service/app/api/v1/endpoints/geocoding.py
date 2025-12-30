from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List, Tuple
import logging
import httpx 

# --- 1. SỬA IMPORT: Thêm get_coordinates_by_place_id ---
from app.services.GeocodingService import (
    get_address_suggestions,
    get_coordinates_from_address,
    get_coordinates_by_place_id, # <--- CẦN THÊM HÀM NÀY
    validate_coordinates,
    is_vietnam_coordinates
)

router = APIRouter()
logger = logging.getLogger(__name__)

# --- PYDANTIC SCHEMAS ---

class AutocompleteResponse(BaseModel):
    suggestions: List[Dict[str, Any]] # Gồm label, place_id (lat, lon có thể null)

class AddressRequest(BaseModel):
    address: str = Field(..., min_length=1, description="Địa chỉ cần geocoding")

# --- 2. THÊM MODEL MỚI CHO PLACE ID ---
class PlaceDetailRequest(BaseModel):
    place_id: str = Field(..., description="ID địa điểm từ Goong/Google")

class BatchAddressRequest(BaseModel):
    addresses: List[str] = Field(..., min_items=1, max_items=50)
    delay_seconds: float = Field(0.2, ge=0.1, le=5.0) # Goong nhanh hơn, giảm default delay

class CoordinatesResponse(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    is_valid: bool
    is_vietnam: bool

class BatchCoordinatesResponse(BaseModel):
    results: Dict[str, Optional[CoordinatesResponse]]
    success_count: int
    total_count: int

class ValidateCoordinatesRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class ValidationResponse(BaseModel):
    latitude: float
    longitude: float
    is_valid: bool
    is_vietnam: bool


# --- ENDPOINTS ---

@router.post("/geocode", response_model=CoordinatesResponse)
async def geocode_address(request: AddressRequest):
    """
    Geocode trực tiếp từ địa chỉ text (VD: "Hồ Gươm") -> Tọa độ.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            coordinates_obj = await get_coordinates_from_address(request.address, client)
        
        if coordinates_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không thể tìm thấy tọa độ cho địa chỉ: {request.address}"
            )
        
        return CoordinatesResponse(
            latitude=coordinates_obj.latitude,
            longitude=coordinates_obj.longitude,
            address=request.address,
            is_valid=validate_coordinates(coordinates_obj.latitude, coordinates_obj.longitude),
            is_vietnam=is_vietnam_coordinates(coordinates_obj.latitude, coordinates_obj.longitude)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. ENDPOINT MỚI QUAN TRỌNG: Place Detail ---
@router.post("/geocode/place-detail", response_model=CoordinatesResponse)
async def get_place_detail(request: PlaceDetailRequest):
    """
    Lấy tọa độ chính xác từ place_id (Dùng sau khi user chọn từ dropdown Autocomplete).
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            coordinates_obj = await get_coordinates_by_place_id(request.place_id, client)
            
        if coordinates_obj is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy tọa độ từ Place ID này")
            
        return CoordinatesResponse(
            latitude=coordinates_obj.latitude,
            longitude=coordinates_obj.longitude,
            address="Place Detail Result", # Goong Detail API có thể không trả lại tên, hoặc cần gọi thêm
            is_valid=True,
            is_vietnam=is_vietnam_coordinates(coordinates_obj.latitude, coordinates_obj.longitude)
        )
    except Exception as e:
        logger.error(f"Place detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geocode/batch", response_model=BatchCoordinatesResponse)
async def batch_geocode(request: BatchAddressRequest):
    """
    Geocode nhiều địa chỉ.
    """
    try:
        results = {}
        success_count = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for address in request.addresses:
                try:
                    # Gọi hàm service
                    coords = await get_coordinates_from_address(address, client)
                    
                    if coords:
                        results[address] = CoordinatesResponse(
                            latitude=coords.latitude,
                            longitude=coords.longitude,
                            address=address,
                            is_valid=True,
                            is_vietnam=is_vietnam_coordinates(coords.latitude, coords.longitude)
                        )
                        success_count += 1
                    else:
                        results[address] = None
                    
                    # Delay nhỏ để tránh rate limit nếu list quá dài
                    if len(request.addresses) > 1:
                        import asyncio
                        await asyncio.sleep(request.delay_seconds)
                        
                except Exception as e:
                    logger.error(f"Error processing {address}: {e}")
                    results[address] = None
        
        return BatchCoordinatesResponse(
            results=results,
            success_count=success_count,
            total_count=len(request.addresses)
        )
        
    except Exception as e:
        logger.error(f"Batch error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý batch geocoding")

@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_address(text: str):
    """
    API gợi ý địa chỉ. 
    LƯU Ý: Frontend cần lấy `place_id` từ kết quả này, 
    sau đó gọi `/geocode/place-detail` để lấy tọa độ.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            suggestions = await get_address_suggestions(text, client)
            
        return AutocompleteResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return AutocompleteResponse(suggestions=[])

@router.post("/validate", response_model=ValidationResponse)
async def validate_coordinates_endpoint(request: ValidateCoordinatesRequest):
    return ValidationResponse(
        latitude=request.latitude,
        longitude=request.longitude,
        is_valid=validate_coordinates(request.latitude, request.longitude),
        is_vietnam=is_vietnam_coordinates(request.latitude, request.longitude)
    )

@router.get("/test")
async def test_geocoding():
    """Test endpoint."""
    test_address = "Dinh Độc Lập"
    async with httpx.AsyncClient() as client:
        coords = await get_coordinates_from_address(test_address, client)
        
    if coords:
        return {"status": "success", "coords": coords}
    return {"status": "failed"}