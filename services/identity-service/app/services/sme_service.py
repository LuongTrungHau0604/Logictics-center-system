import logging
import httpx
import aiomysql
from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime 

# --- Import CRUD (Lớp truy cập CSDL thô) ---
from app.crud.crud_sme import CRUDSme
from app.crud.crud_user import CRUDUser 
from app.crud.crud_area import CRUDArea
# --- Import Schemas (Mô hình Pydantic) ---
# (Import SMECreate/UserCreate để tạo object)
from app.schemas.sme import SMECreate, SMEUpdate, SMEOut
from app.schemas.user import UserCreate, UserOut
# (Import schema đăng ký "phẳng" mới)
from app.schemas.SME_Registration import SmeOwnerRegistration
from app.core.security import get_password_hash

from app.services.GeocodingService import get_coordinates_from_address

# --- Import Dịch vụ bên ngoài ---
from app.services.GeocodingService import get_coordinates_from_address, _clean_address, _add_vietnam_context

logger = logging.getLogger(__name__)

class SmeService:
    """
    Lớp Service cho SME, chịu trách nhiệm cho logic nghiệp vụ.
    """

    @staticmethod
    async def register_sme_owner(
        db: aiomysql.Connection,
        http_client: httpx.AsyncClient,
        reg_data: SmeOwnerRegistration
    ) -> UserOut:
        """
        Đăng ký SME Owner (Tách Latitude/Longitude)
        """
        try:
            logger.info(f"Bắt đầu đăng ký SME Owner: {reg_data.tax_code}")
            
            # 1. Validate (Giữ nguyên phần validate cũ của bạn)
            existing_sme = await CRUDSme.get_sme_by_tax_code(db, reg_data.tax_code)
            if existing_sme:
                # ... (Giữ nguyên logic lỗi 409)
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tax code already registered")
            
            existing_user = await CRUDUser.get_by_email(db, reg_data.email)
            if existing_user:
                # ... (Giữ nguyên logic lỗi 409)
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
            
            # 2. Geocoding (ĐÃ SỬA: Tách lat/lon)
            latitude = None
            longitude = None
            
            if reg_data.address and reg_data.address.strip():
                try:
                    coords_obj = await get_coordinates_from_address(
                        reg_data.address,
                        http_client
                    )
                    if coords_obj:
                        # Lấy giá trị float trực tiếp, KHÔNG tạo string "POINT(...)" nữa
                        latitude = coords_obj.latitude
                        longitude = coords_obj.longitude
                        logger.info(f"Geocoding successful: Lat={latitude}, Lon={longitude}")
                except Exception as geo_error:
                    logger.warning(f"Geocoding failed: {geo_error}")
                    # Continue with None
            
            # Tìm Area
            area_id = None
            if latitude is not None and longitude is not None:
                logger.info(f"Bắt đầu tìm kiếm Area cho SME tại ({latitude}, {longitude})")
                
                # GỌI HÀM CRUD MỚI (Truyền 2 tham số)
                area_id = await CRUDArea.find_area_by_coordinates(db, latitude, longitude)
                
                if area_id:
                    logger.info(f"✅ SME được gán vào Area ID: {area_id}")
                else:
                    logger.warning("⚠️ SME không thuộc Area nào.")
            else:
                logger.info("Bỏ qua tìm kiếm Area vì không có tọa độ.")
            
            # 3. Tạo SME record (ĐÃ SỬA: Dùng 2 cột lat/lon)
            sme_id = CRUDSme.generate_sme_id()
            sme_data = {
                "sme_id": sme_id,
                "business_name": reg_data.business_name,
                "tax_code": reg_data.tax_code,
                "address": reg_data.address,
                "contact_phone": reg_data.phone,
                "email": reg_data.email,
                
                # --- THAY ĐỔI Ở ĐÂY ---
                # Xóa key "coordinates", thay bằng 2 key mới:
                "latitude": latitude,
                "longitude": longitude,
                "status": "PENDING",  # Mặc định INACTIVE
                "area_id": area_id,
                "created_at": datetime.utcnow()
            }
            
            # Gọi hàm create_sme (Bạn cần đảm bảo hàm này trong CRUDSme đã được sửa để nhận dict này)
            created_sme = await CRUDSme.create_sme(db, sme_data) # Bỏ tham số coordinates_str thừa
            
            if not created_sme:
                raise HTTPException(status_code=500, detail="Failed to create SME record")
            
            # 4. Tạo User record (Giữ nguyên code cũ của bạn)
            user_id = CRUDUser.generate_user_id()
            user_data = {
                "user_id": user_id,
                "username": reg_data.username,
                "email": reg_data.email,
                "phone": reg_data.phone,
                "role": "SME_OWNER",
                "password_hash": get_password_hash(reg_data.password),
                "sme_id": sme_id,
                "created_at": datetime.utcnow()
            }
            
            created_user = await CRUDUser.create_user(db, user_data)
            if not created_user:
                raise HTTPException(status_code=500, detail="Failed to create user record")
            
            logger.info(f"✅ SME Owner records created successfully (PENDING COMMIT)")
            return created_user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Lỗi trong SmeService.register_sme_owner: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    async def get_sme_details(db: aiomysql.Connection, sme_id: str) -> Optional[SMEOut]:
        """
        Lấy chi tiết SME và danh sách các user thuộc SME đó.
        """
        logger.info(f"Đang lấy chi tiết cho SME: {sme_id}")
        
        # 1. Lấy thông tin SME (đã dùng ST_AsText)
        sme = await CRUDSme.get_sme_by_id(db, sme_id)
        if not sme:
            return None
        
        # 2. Lấy danh sách user
        users_list = await CRUDUser.get_users_by_sme_id(db, sme_id)
        
        # 3. Gán danh sách user vào SME
        sme.users = users_list
        return sme

    @staticmethod
    async def create_sme_user(
        db: aiomysql.Connection,
        sme_id: str,
        user_data: UserCreate,
        current_user: UserOut # (Dùng để check quyền)
    ) -> UserOut:
        """
        Tạo một user mới (SME_USER) cho một SME đã tồn tại.
        (Được gọi bởi SME Owner hoặc Admin)
        """
        
        # Kiểm tra SME có tồn tại không
        sme = await CRUDSme.get_sme_by_id(db, sme_id)
        if not sme:
            raise HTTPException(status_code=404, detail=f"SME {sme_id} không tồn tại.")
        
        # Kiểm tra email
        if await CRUDUser.get_by_email(db, user_data.email):
            raise HTTPException(status_code=400, detail=f"Email {user_data.email} đã được sử dụng.")
        
        # Ghi đè role và sme_id để đảm bảo bảo mật
        user_create_data = user_data.model_copy()
        user_create_data.role = "SME_USER" # Luôn là SME_USER
        user_create_data.sme_id = sme_id   # Luôn là SME của người gọi
        
        new_user = await CRUDUser.create_user(db, user_create_data)
        if not new_user:
            raise HTTPException(status_code=500, detail="Không thể tạo user cho SME.")
            
        return new_user

    @staticmethod
    async def update_sme_details(
        db: aiomysql.Connection,
        http_client: httpx.AsyncClient,
        sme_id: str,
        sme_data: SMEUpdate
    ) -> Optional[SMEOut]:
        """
        Cập nhật chi tiết SME (gọi bởi Owner hoặc Admin).
        Tự động geocode lại nếu 'address' thay đổi.
        """
        logger.info(f"Đang cập nhật SME: {sme_id}")
        
        # Lấy các trường client gửi lên
        update_payload = sme_data.model_dump(exclude_unset=True)
        
        # Kiểm tra nếu địa chỉ thay đổi
        if "address" in update_payload:
            new_address = update_payload["address"]
            if new_address and new_address.strip():
                # Geocode lại
                logger.info(f"Địa chỉ thay đổi, đang geocode lại: {new_address}")
                cleaned_address = _clean_address(new_address)
                full_address = _add_vietnam_context(cleaned_address)
                coords_obj = await get_coordinates_from_address(full_address, http_client)
                
                if coords_obj:
                    # SỬA LỖI: ĐẢO NGƯỢC thứ tự - POINT(latitude longitude) cho MySQL
                    update_payload["coordinates"] = f"POINT({coords_obj.latitude} {coords_obj.longitude})"
                else:
                    update_payload["coordinates"] = None
            
        
        # Tạo lại đối tượng SMEUpdate đã được validate
        final_update_data = SMEUpdate.model_validate(update_payload)
        
        return await CRUDSme.update_sme(db, sme_id, final_update_data)

    @staticmethod
    async def get_all_smes(db: aiomysql.Connection, skip: int = 0, limit: int = 100) -> List[SMEOut]:
        """
        (Admin) Lấy danh sách tất cả SME.
        """
        return await CRUDSme.get_all_smes(db, skip, limit)

    @staticmethod
    async def get_smes_by_status(db: aiomysql.Connection, status: str, skip: int = 0, limit: int = 100) -> List[SMEOut]:
        """
        (Admin) Lấy danh sách SME theo trạng thái.
        """
        return await CRUDSme.get_smes_by_status(db, status, skip, limit)