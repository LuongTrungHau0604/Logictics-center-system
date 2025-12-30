# app/services/shipper_service.py
from datetime import datetime
import aiomysql
import logging
from fastapi import HTTPException
from app.crud.crud_shipper import CRUDShipper
from app.schemas.shipper import ShipperLocationUpdate, ShipperTokenUpdate, ShipperProfileOut
from app.schemas.user import UserOut

logger = logging.getLogger(__name__)

class ShipperService:
    """
    Logic nghiệp vụ riêng cho Shipper:
    - Cập nhật vị trí GPS
    - Cập nhật FCM Token
    - Lấy thông tin Profile chi tiết
    """

    @staticmethod
    async def get_profile(
        db: aiomysql.Connection,
        current_user: UserOut
    ) -> ShipperProfileOut:
        """
        Lấy thông tin chi tiết của Shipper dựa trên User đang login.
        """
        # 1. Kiểm tra Role
        if current_user.role != "SHIPPER":
            raise HTTPException(status_code=403, detail="Tài khoản không phải là Shipper")

        # 2. Lấy profile từ DB
        profile = await CRUDShipper.get_profile_by_user_id(db, current_user.user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ Shipper")
            
        return profile

    @staticmethod
    async def update_location(
        db: aiomysql.Connection,
        current_user: UserOut,
        location_data: ShipperLocationUpdate
    ):
        """
        Cập nhật vị trí hiện tại của Shipper.
        """
        # 1. Lấy thông tin Shipper
        shipper = await CRUDShipper.get_by_user_id(db, current_user.user_id)
        if not shipper:
            raise HTTPException(status_code=404, detail="Shipper not found")

        shipper_id = shipper['shipper_id']

        try:
            await db.begin()
            
            # 2. Update vào DB
            # Lưu ý: Cần đảm bảo CRUDShipper.update hỗ trợ update các trường này
            update_data = {
                "current_latitude": location_data.current_lat,
                "current_longitude": location_data.current_lon,
                "last_location_update": datetime.utcnow()  # <--- Sửa thành datetime của Python
            }
            
            await CRUDShipper.update(db, shipper_id, update_data)
            
            await db.commit()
            logger.info(f"📍 Updated location for {shipper_id}: {location_data.current_lat}, {location_data.current_lon}")
            return {"status": "success", "msg": "Location updated"}

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error updating location: {e}")
            raise HTTPException(status_code=500, detail="Could not update location")

    @staticmethod
    async def update_fcm_token(
        db: aiomysql.Connection,
        current_user: UserOut,
        token_data: ShipperTokenUpdate
    ):
        """
        Lưu Device Token để bắn thông báo.
        """
        shipper = await CRUDShipper.get_by_user_id(db, current_user.user_id)
        if not shipper:
            raise HTTPException(status_code=404, detail="Shipper not found")

        shipper_id = shipper['shipper_id']

        try:
            await db.begin()
            
            await CRUDShipper.update(db, shipper_id, {"fcm_token": token_data.fcm_token})
            
            await db.commit()
            logger.info(f"📲 Updated FCM Token for {shipper_id}")
            return {"status": "success", "msg": "Token updated"}

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error updating token: {e}")
            raise HTTPException(status_code=500, detail="Could not update token")