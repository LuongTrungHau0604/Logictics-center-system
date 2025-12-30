import logging
import aiomysql
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.security import verify_password
from app.crud.crud_user import CRUDUser 
from app.schemas.user import UserOut, UserInDB
from app.core.config import settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """
        Tạo JWT access token
        """
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)
            
            to_encode.update({"exp": expire})
            
            # SỬA LỖI 1: Dùng settings.SECRET_KEY (Viết hoa)
            encoded_jwt = jwt.encode(
                to_encode, 
                settings.SECRET_KEY, 
                algorithm=settings.ALGORITHM
            )
            
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"❌ Token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create access token"
            )

    @staticmethod
    async def authenticate_user(
        db: aiomysql.Connection, 
        username: str, 
        password: str
    ) -> Optional[UserInDB]:
        """
        Xác thực user khi Login
        """
        try:
            # Lưu ý: db ở đây là Connection, cần tạo cursor trong CRUD
            # (Giả sử CRUDUser của bạn đã xử lý việc tạo cursor từ connection)
            
            logger.info(f"Đang tìm user để xác thực: {username}")
            
            user = await CRUDUser.get_by_username_for_auth(db, username)
            
            if not user:
                logger.info(f"Không tìm thấy user bằng username, thử email: {username}")
                user = await CRUDUser.get_by_email_for_auth(db, username)
            
            if not user:
                logger.warning(f"Xác thực thất bại: Không tìm thấy user {username}")
                return None
            
            if not verify_password(password, user.password_hash):
                logger.warning(f"Xác thực thất bại: Sai mật khẩu cho user {username}")
                return None
            
            logger.info(f"✅ Xác thực thành công: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi xác thực user {username}: {e}")
            return None

    @staticmethod
    async def get_user_from_token(db: aiomysql.Connection, token: str) -> Optional[UserOut]:
        """
        Lấy user từ JWT token.
        SỬA ĐỔI QUAN TRỌNG: Logic này đã được cập nhật để khớp với auth.py
        """
        try:
            # SỬA LỖI 1: Dùng settings.SECRET_KEY (Viết hoa)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # 1. Lấy user_id từ 'sub' (Vì auth.py lưu user_id vào sub)
            user_id_str: str = payload.get("sub")
            
            if user_id_str is None:
                logger.warning("❌ Token payload không có 'sub'")
                return None

            # 2. Tìm user theo ID (Thay vì tìm theo username)
            # Lưu ý: Bạn cần đảm bảo CRUDUser có hàm get (tìm theo ID)
            try:
                # Nếu ID trong DB là số int, cần ép kiểu. Nếu là UUID/String, giữ nguyên.
                # Dựa vào log cũ của bạn (f6ce...), có vẻ là String/UUID, nhưng thường DB là int.
                # Tôi sẽ thử ép kiểu int, nếu lỗi thì dùng string.
                if user_id_str.isdigit():
                    user_id = int(user_id_str)
                else:
                    user_id = user_id_str
                    
                # GỌI CRUD THEO ID
                user = await CRUDUser.get(db, user_id)
                
            except AttributeError:
                # Fallback: Nếu CRUDUser chưa có hàm .get(), ta dùng .get_by_username 
                # nhưng phải lấy 'username' từ payload (auth.py CÓ lưu username trong token)
                logger.warning("⚠️ CRUDUser có thể thiếu hàm get(id). Thử fallback sang username.")
                username_in_token = payload.get("username")
                if username_in_token:
                     user = await CRUDUser.get_by_username(db, username_in_token)
                else:
                    logger.error("❌ Không thể tìm user: Token thiếu username và CRUD thiếu get(id)")
                    return None

            if user is None:
                logger.warning(f"❌ User not found in database with ID: {user_id_str}")
                return None
            
            return user
            
        except JWTError as e:
            logger.warning(f"❌ JWT decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user from token: {e}")
            return None
            
auth_service = AuthService()