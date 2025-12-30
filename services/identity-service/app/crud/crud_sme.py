import uuid
import logging
import aiomysql
from datetime import datetime
from typing import Optional, List, Any

# --- Import các Schemas (Pydantic models) ---
from app.schemas.sme import SMECreate, SMEUpdate, SMEOut

logger = logging.getLogger(__name__)

class CRUDSme:
    """
    Lớp chứa các phương thức static để tương tác với bảng 'sme'.
    """

    @staticmethod
    def generate_sme_id() -> str:
        return uuid.uuid4().hex[:30]

    @staticmethod
    async def create_sme(db: aiomysql.Connection, sme_data: dict) -> Optional[SMEOut]:
        """
        Tạo SME record KHÔNG auto-commit (Giữ nguyên như bạn đã sửa).
        Đã thêm trường 'status' để khắc phục lỗi tự động ACTIVE.
        """
        try:
            # 1. Thêm cột 'status' vào danh sách cột
            query = """
            INSERT INTO sme (
                sme_id, business_name, tax_code, address, 
                contact_phone, email, latitude, longitude, 
                area_id, created_at, status
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 2. Thêm giá trị status vào params
            # Dùng .get("status", "PENDING") để đảm bảo nếu dict thiếu key thì vẫn là PENDING
            params = (
                sme_data["sme_id"],
                sme_data["business_name"], 
                sme_data["tax_code"],
                sme_data["address"],
                sme_data["contact_phone"],
                sme_data["email"],
                sme_data.get("latitude"), 
                sme_data.get("longitude"),
                sme_data.get("area_id"), 
                sme_data["created_at"],
                sme_data.get("status", "PENDING") # <--- DÒNG QUAN TRỌNG NHẤT
            )
            
            async with db.cursor() as cursor:
                await cursor.execute(query, params)
                # Không commit ở đây để Service quản lý Transaction (User + SME)
            
            return await CRUDSme.get_sme_by_id(db, sme_data["sme_id"])
                
        except Exception as e:
            logger.error(f"❌ Create SME (no commit) error: {e}")
            return None

    # --- CÁC HÀM GET (ĐÃ SỬA LỖI SELECT) ---

    @staticmethod
    async def get_sme_by_id(db: aiomysql.Connection, sme_id: str) -> Optional[SMEOut]:
        try:
            # SỬA LỖI: Thay 'ST_AsText(coordinates) as coordinates' bằng 'latitude, longitude'
            query = """
                SELECT 
                    sme_id, business_name, tax_code, address, 
                    latitude, longitude, 
                    contact_phone, email, status, created_at, area_id
                FROM sme 
                WHERE sme_id = %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (sme_id,))
                row = await cursor.fetchone()
            
            if row:
                return SMEOut.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get SME by ID error: {e}")
            return None

    @staticmethod
    async def get_sme_by_tax_code(db: aiomysql.Connection, tax_code: str) -> Optional[SMEOut]:
        try:
            # SỬA LỖI: Select latitude, longitude
            query = """
                SELECT 
                    sme_id, business_name, tax_code, address, 
                    latitude, longitude,
                    contact_phone, email, status, created_at, area_id
                FROM sme 
                WHERE tax_code = %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (tax_code,))
                row = await cursor.fetchone()
            
            if row:
                return SMEOut.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get SME by tax code error: {e}")
            return None

    @staticmethod
    async def get_all_smes(db: aiomysql.Connection, skip: int = 0, limit: int = 100) -> List[SMEOut]:
        try:
            await db.commit() 
            # SỬA LỖI: Select latitude, longitude
            query = """
                SELECT 
                    sme_id, business_name, tax_code, address, 
                    latitude, longitude,
                    contact_phone, email, status, created_at, area_id
                FROM sme 
                ORDER BY created_at DESC LIMIT %s OFFSET %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (limit, skip))
                rows = await cursor.fetchall()
            
            return [SMEOut.model_validate(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Get all SMEs error: {e}")
            return []

    @staticmethod
    async def get_smes_by_status(db: aiomysql.Connection, status: str, skip: int = 0, limit: int = 100) -> List[SMEOut]:
        try:
            await db.commit() 
            # SỬA LỖI: Select latitude, longitude
            query = """
                SELECT 
                    sme_id, business_name, tax_code, address, 
                    latitude, longitude,
                    contact_phone, email, status, created_at, area_id
                FROM sme 
                WHERE status = %s 
                ORDER BY created_at DESC LIMIT %s OFFSET %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (status, limit, skip))
                rows = await cursor.fetchall()
            
            return [SMEOut.model_validate(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Get SMEs by status error: {e}")
            return []
        
    @staticmethod
    async def get_by_phone(db: aiomysql.Connection, phone: str) -> Optional[SMEOut]:
        try:
            # SỬA LỖI: Select latitude, longitude
            query = """
                SELECT 
                    sme_id, business_name, tax_code, address, 
                    latitude, longitude,
                    contact_phone, email, status, created_at, area_id
                FROM sme 
                WHERE contact_phone = %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (phone,))
                row = await cursor.fetchone()
            
            if row:
                return SMEOut.model_validate(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Get SME by phone error: {e}")
            return None

    # --- CÁC HÀM UPDATE & DELETE (ĐÃ SỬA LOGIC) ---

    @staticmethod
    async def update_sme(db: aiomysql.Connection, sme_id: str, sme_data: SMEUpdate) -> Optional[SMEOut]:
        """
        Cập nhật thông tin SME. Đã loại bỏ logic ST_GeomFromText.
        """
        update_dict = sme_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            return await CRUDSme.get_sme_by_id(db, sme_id)

        update_fields = []
        params = []
        
        for field, value in update_dict.items():
            # SỬA LỖI: Nếu field là latitude hoặc longitude thì update bình thường
            # Không còn check 'coordinates' nữa vì model đã thay đổi
            update_fields.append(f"{field} = %s")
            params.append(value)
        
        if not update_fields:
             return await CRUDSme.get_sme_by_id(db, sme_id)

        params.append(sme_id)
        
        query = f"""
            UPDATE sme 
            SET {', '.join(update_fields)}
            WHERE sme_id = %s
        """
        
        try:
            async with db.cursor() as cursor:
                await cursor.execute(query, params)
                await db.commit()
            
            return await CRUDSme.get_sme_by_id(db, sme_id)
        except Exception as e:
            logger.error(f"❌ Update SME error: {e}")
            return None

    @staticmethod
    async def delete_sme(db: aiomysql.Connection, sme_id: str) -> bool:
        try:
            query = "DELETE FROM sme WHERE sme_id = %s"
            async with db.cursor() as cursor:
                await cursor.execute(query, (sme_id,))
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Delete SME error: {e}")
            await db.rollback()
            return False