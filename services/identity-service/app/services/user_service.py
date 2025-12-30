import logging
import aiomysql
from typing import Optional
from fastapi import HTTPException
from datetime import datetime

from app.crud.crud_user import CRUDUser
from app.schemas.user import UserOut, UserUpdate, UserCreate
from app.core.security import get_password_hash  # Import hashing function
from app.crud.crud_sme import CRUDSme
logger = logging.getLogger(__name__)

class UserService:
    
    @staticmethod
    async def register_regular_user(
        db: aiomysql.Connection, 
        user_data: UserCreate
    ) -> UserOut:
        """
        Đăng ký người dùng bình thường (không phải SME Owner).
        """
        try:
            logger.info(f"Bắt đầu đăng ký user thường: {user_data.username}")
            
            # DEBUG: Log user_data type
            logger.info(f"🔍 user_data type: {type(user_data)}")
            logger.info(f"🔍 user_data content: {user_data}")
            
            # SỬA LỖI: Ensure user_data is UserCreate object
            if isinstance(user_data, dict):
                logger.warning("user_data is dict, converting to UserCreate")
                user_data = UserCreate(**user_data)
            
            # 1. Kiểm tra username đã tồn tại chưa
            existing_user_by_username = await CRUDUser.get_by_username(db, user_data.username)
            if existing_user_by_username:
                logger.warning(f"Username {user_data.username} đã tồn tại")
                raise HTTPException(
                    status_code=400,
                    detail="Username đã được sử dụng"
                )
            
            # 2. Kiểm tra email đã tồn tại chưa
            existing_user_by_email = await CRUDUser.get_by_email(db, user_data.email)
            if existing_user_by_email:
                logger.warning(f"Email {user_data.email} đã tồn tại")
                raise HTTPException(
                    status_code=400,
                    detail="Email đã được sử dụng"
                )
                
            found_sme_id: Optional[str] = None
            final_role: str
            
            # 3. Tìm SME ID bằng SĐT và xác thực vai trò
            if hasattr(user_data, 'sme_phone') and user_data.sme_phone:
                logger.info(f"Tìm kiếm SME với SĐT: {user_data.sme_phone}")
                sme = await CRUDSme.get_by_phone(db, user_data.sme_phone)
                
                if not sme:
                    logger.warning(f"Không tìm thấy SME với SĐT: {user_data.sme_phone}")
                    raise HTTPException(
                        status_code=400,
                        detail="Không tìm thấy doanh nghiệp (SME) với SĐT được cung cấp"
                    )
                
                found_sme_id = sme.sme_id
                final_role = "SME_USER"
                logger.info(f"Tìm thấy SME (ID: {found_sme_id}). Gán role: {final_role}")
            
            else:
                final_role = "USER"
                logger.info(f"Không có SĐT SME. Gán role: {final_role}")
            
            # 4. Hash password - SỬA LỖI: Access password safely
            try:
                password = user_data.password if hasattr(user_data, 'password') else user_data['password']
                hashed_password = get_password_hash(password)
                logger.info("✅ Password hashed successfully")
            except Exception as hash_error:
                logger.error(f"❌ Password hashing failed: {hash_error}")
                raise HTTPException(
                    status_code=500,
                    detail="Lỗi mã hóa mật khẩu"
                )
            
            # 5. Tạo user mới
            user_id = CRUDUser.generate_user_id()
            
            # 6. Chuẩn bị data cho DB - SỬA LỖI: Safe attribute access
            user_db_data = {
                "user_id": user_id,
                "username": getattr(user_data, 'username', None),
                "email": getattr(user_data, 'email', None),
                "phone": getattr(user_data, 'phone', None),
                "role": final_role,
                "password_hash": hashed_password,
                "sme_id": found_sme_id,
                "created_at": datetime.utcnow()
            }
            
            # Validate required fields
            if not user_db_data["username"] or not user_db_data["email"]:
                raise HTTPException(
                    status_code=400,
                    detail="Username và email là bắt buộc"
                )
            
            # 7. Insert vào database
            created_user = await CRUDUser.create_user_from_dict(db, user_db_data)
            
            if not created_user:
                logger.error(f"Không thể tạo user trong database: {user_db_data['username']}")
                raise HTTPException(
                    status_code=500,
                    detail="Không thể tạo tài khoản"
                )
            
            logger.info(f"✅ Đăng ký thành công user: {created_user.username} (ID: {created_user.user_id})")
            
            return created_user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Lỗi đăng ký user: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi hệ thống: {str(e)}"
            )
    
    @staticmethod
    async def get_user_details(db: aiomysql.Connection, user_id: str) -> Optional[UserOut]:
        """
        Lấy thông tin chi tiết của user bằng ID.
        """
        logger.info(f"Đang lấy chi tiết cho user: {user_id}")
        user = await CRUDUser.get_by_id(db, user_id)
        if not user:
            logger.warning(f"Không tìm thấy user: {user_id}")
            return None
        return user

    @staticmethod
    async def update_user_profile(
        db: aiomysql.Connection, 
        user_id: str, 
        user_data: UserUpdate
    ) -> Optional[UserOut]:
        """
        Cập nhật thông tin profile cho user.
        """
        logger.info(f"Đang cập nhật profile cho user: {user_id}")
        
        # (Lưu ý: CRUDUser.update_user đã xử lý việc hash password nếu 'password' được cung cấp)
        updated_user = await CRUDUser.update_user(db, user_id, user_data)
        
        if not updated_user:
            logger.error(f"Cập nhật thất bại cho user: {user_id}")
            return None
            
        return updated_user
    
    @staticmethod
    async def get_user_by_username(db: aiomysql.Connection, username: str) -> Optional[UserOut]:
        """
        Lấy user theo username (dùng cho authentication).
        """
        logger.info(f"Tìm user theo username: {username}")
        return await CRUDUser.get_by_username(db, username)
    
    @staticmethod
    async def get_user_by_email(db: aiomysql.Connection, email: str) -> Optional[UserOut]:
        """
        Lấy user theo email.
        """
        logger.info(f"Tìm user theo email: {email}")
        return await CRUDUser.get_by_email(db, email)
    
    @staticmethod
    async def check_user_exists(db: aiomysql.Connection, username: str = None, email: str = None) -> bool:
        """
        Kiểm tra user đã tồn tại chưa (theo username hoặc email).
        """
        if username:
            user = await CRUDUser.get_by_username(db, username)
            if user:
                return True
        
        if email:
            user = await CRUDUser.get_by_email(db, email)
            if user:
                return True
        
        return False