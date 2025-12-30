import uuid
import logging
import aiomysql
from datetime import datetime
from typing import Optional, List, Any, Dict, Tuple
from passlib.context import CryptContext

# --- Import các Schemas (Pydantic models) ---
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserInDB

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CRUDUser:
    """
    Lớp chứa các phương thức static để tương tác với bảng 'user'
    sử dụng aiomysql.
    """

    @staticmethod
    def generate_user_id() -> str:
        """Tạo ID ngẫu nhiên cho User"""
        return uuid.uuid4().hex[:30] # Giả sử 30 ký tự

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

    # --- Các hàm chuẩn bị Query (dùng cho Transaction) ---

    @staticmethod
    def prepare_create_user_query(
        user_data: UserCreate, 
        user_id: str, 
        password_hash: str, 
        role: str, 
        sme_id: Optional[str]
    ) -> Tuple[str, Tuple]:
        """Chuẩn bị query và params để tạo user, không commit."""
        query = """
        INSERT INTO `user` (user_id, username, password_hash, email, phone, role, sme_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            user_data.username,
            password_hash,
            user_data.email,
            user_data.phone,
            role,
            sme_id,
            datetime.utcnow()
        )
        return query, params

    # --- Các hàm CRUD (Tự động commit) ---

    @staticmethod
    async def create_user(db: aiomysql.Connection, user_data: UserCreate) -> Optional[UserOut]:
        """
        Tạo User record KHÔNG auto-commit (dành cho transaction management)
        """
        try:
            query = """
            INSERT INTO `user` (user_id, username, password_hash, email, phone, role, sme_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                user_data["user_id"],
                user_data["username"],
                user_data["password_hash"],
                user_data["email"], 
                user_data["phone"],
                user_data["role"],
                user_data["sme_id"],
                user_data["created_at"]
            )
            
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                # SỬA LỖI: KHÔNG commit ở đây
                # await db.commit()  # ← BỎ DÒNG NÀY
            
            # Return created user
            return await CRUDUser.get_by_id(db, user_data["user_id"])
            
        except Exception as e:
            logger.error(f"❌ Create User (no commit) error: {e}")
            return None

    @staticmethod
    async def get_by_id(db: aiomysql.Connection, user_id: str) -> Optional[UserOut]:
        """Lấy user theo user_id"""
        try:
            query = "SELECT * FROM `user` WHERE user_id = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (user_id,))
                row = await cursor.fetchone()
            
            if row:
                return UserOut.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user by ID error: {e}")
            return None

    @staticmethod
    async def get_by_email(db: aiomysql.Connection, email: str) -> Optional[UserOut]:
        """Lấy user theo email"""
        try:
            query = "SELECT * FROM `user` WHERE email = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (email,))
                row = await cursor.fetchone()
            
            if row:
                return UserOut.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user by email error: {e}")
            return None

    @staticmethod
    async def get_by_username(db: aiomysql.Connection, username: str) -> Optional[UserOut]:
        """Lấy user theo username"""
        try:
            query = "SELECT * FROM `user` WHERE username = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (username,))
                row = await cursor.fetchone()
            
            if row:
                return UserOut.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user by username error: {e}")
            return None

    @staticmethod
    async def get_user_with_password_hash_by_username(db: aiomysql.Connection, username: str) -> Optional[UserInDB]:
        """Lấy user (bao gồm password_hash) bằng username (dùng cho Auth)"""
        try:
            query = "SELECT * FROM `user` WHERE username = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (username,))
                row = await cursor.fetchone()
            
            if row:
                return UserInDB.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user (auth) by username error: {e}")
            return None
            
    @staticmethod
    async def get_user_with_password_hash_by_email(db: aiomysql.Connection, email: str) -> Optional[UserInDB]:
        """Lấy user (bao gồm password_hash) bằng email (dùng cho Auth)"""
        try:
            query = "SELECT * FROM `user` WHERE email = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (email,))
                row = await cursor.fetchone()
            
            if row:
                return UserInDB.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user (auth) by email error: {e}")
            return None

    @staticmethod
    async def get_users_by_sme_id(db: aiomysql.Connection, sme_id: str) -> List[UserOut]:
        """Lấy TẤT CẢ user thuộc 1 SME"""
        try:
            query = "SELECT * FROM `user` WHERE sme_id = %s ORDER BY created_at DESC"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (sme_id,))
                rows = await cursor.fetchall()
            
            return [UserOut.model_validate(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Get users by SME ID error: {e}")
            return []

    @staticmethod
    async def update_user(db: aiomysql.Connection, user_id: str, user_data: UserUpdate) -> Optional[UserOut]:
        """Cập nhật user (dynamic update), TỰ ĐỘNG COMMIT."""
        try:
            update_data = user_data.model_dump(exclude_unset=True)
            
            if not update_data:
                logger.info("ℹ️ Không có trường nào để cập nhật user.")
                return await CRUDUser.get_by_id(db, user_id)

            set_clauses: List[str] = []
            params: List[Any] = []

            for key, value in update_data.items():
                if key == "password":
                    set_clauses.append("password_hash = %s")
                    params.append(CRUDUser.hash_password(value))
                else:
                    set_clauses.append(f"`{key}` = %s") # Dùng backtick
                    params.append(value)
            
            params.append(user_id)
            set_statement = ", ".join(set_clauses)
            query = f"UPDATE `user` SET {set_statement} WHERE user_id = %s"

            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, tuple(params))
                await db.commit()
            
            return await CRUDUser.get_by_id(db, user_id)

        except Exception as e:
            logger.error(f"❌ Update User error: {e}")
            await db.rollback()
            return None
    @staticmethod
    async def create_user_from_dict(db: aiomysql.Connection, user_dict: dict) -> Optional[UserOut]:
        """
        Tạo user từ dict data (dành riêng cho user_service).
        Password đã được hash trước đó.
        """
        try:
            query = """
            INSERT INTO `user` (user_id, username, password_hash, email, phone, role, sme_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                user_dict["user_id"],
                user_dict["username"],
                user_dict["password_hash"],
                user_dict["email"],
                user_dict["phone"],
                user_dict["role"],
                user_dict["sme_id"],
                user_dict["created_at"]
            )
            
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                await db.commit()
            
            return await CRUDUser.get_by_id(db, user_dict["user_id"])
            
        except Exception as e:
            logger.error(f"❌ Create User from dict error: {e}")
            await db.rollback()
            return None
    @staticmethod
    async def get_by_username_for_auth(db: aiomysql.Connection, username: str) -> Optional[UserInDB]:
        """Lấy user (bao gồm password_hash) bằng username (dùng cho Auth)"""
        try:
            query = "SELECT * FROM `user` WHERE username = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (username,))
                row = await cursor.fetchone()
            
            if row:
                return UserInDB.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user (auth) by username error: {e}")
            return None
    async def get_by_email_for_auth(db: aiomysql.Connection, email: str) -> Optional[UserInDB]:
        """Lấy user (bao gồm password_hash) bằng email (dùng cho Auth)"""
        try:
            query = "SELECT * FROM `user` WHERE email = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (email,))
                row = await cursor.fetchone()
            
            if row:
                return UserInDB.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user (auth) by email error: {e}")
            return None