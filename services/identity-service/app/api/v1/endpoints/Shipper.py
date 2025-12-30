# app/api/v1/endpoints/shippers.py
from fastapi import APIRouter, Depends
from app.db.session import get_db 
from app.api.v1.deps import get_current_user 
from app.schemas.user import UserOut 
from app.schemas.shipper import ShipperProfileOut, ShipperLocationUpdate, ShipperTokenUpdate
from app.services.shipper_service import ShipperService # Import Service vừa tạo
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Shipper"])

@router.get("/me", response_model=ShipperProfileOut)
async def get_my_shipper_profile(
    current_user: UserOut = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của Shipper đang đăng nhập.
    """
    return await ShipperService.get_profile(db, current_user)

@router.post("/me/location")
async def update_my_location(
    location_in: ShipperLocationUpdate,
    current_user: UserOut = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    App Shipper gọi API này liên tục (background) để cập nhật vị trí.
    """
    return await ShipperService.update_location(db, current_user, location_in)

@router.put("/me/device-token")
async def update_my_device_token(
    token_in: ShipperTokenUpdate,
    current_user: UserOut = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    App Shipper gọi API này khi vừa mở app để đăng ký nhận thông báo.
    """
    return await ShipperService.update_fcm_token(db, current_user, token_in)