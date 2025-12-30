import aiomysql
import logging
from typing import List, Optional, Dict, Any
from app.schemas.shipper import ShipperCreate, ShipperUpdate, ShipperOut, ShipperStatus

logger = logging.getLogger(__name__)

class CRUDShipper:
    
    @staticmethod
    async def create(db: aiomysql.Connection, obj_in: dict) -> Optional[Dict[str, Any]]:
        """
        Tạo mới một Shipper.
        Lưu ý: obj_in phải là dict khớp với cấu trúc bảng shippers.
        """
        try:
            query = """
                INSERT INTO shippers (
                    shipper_id, employee_id, vehicle_type, 
                    status, area_id, rating, created_at
                ) VALUES (
                    %(shipper_id)s, %(employee_id)s, %(vehicle_type)s, 
                    %(status)s, %(area_id)s, %(rating)s, %(created_at)s
                )
            """
            async with db.cursor() as cursor:
                await cursor.execute(query, obj_in)
                # Không commit ở đây nếu đang trong transaction lớn của EmployeeService
            
            return obj_in
        except Exception as e:
            logger.error(f"❌ Error creating shipper: {e}")
            raise e

    @staticmethod
    async def get_by_id(db: aiomysql.Connection, shipper_id: str) -> Optional[ShipperOut]:
        """Lấy thông tin Shipper theo ID, join với Employee để lấy tên."""
        try:
            query = """
                SELECT s.*, e.full_name, e.phone 
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE s.shipper_id = %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (shipper_id,))
                result = await cursor.fetchone()
                
            if result:
                return ShipperOut(**result)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting shipper by id: {e}")
            return None

    @staticmethod
    async def get_by_employee_id(db: aiomysql.Connection, employee_id: str) -> Optional[ShipperOut]:
        """Lấy thông tin Shipper dựa trên Employee ID."""
        try:
            query = """
                SELECT s.*, e.full_name, e.phone 
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE s.employee_id = %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (employee_id,))
                result = await cursor.fetchone()
                
            if result:
                return ShipperOut(**result)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting shipper by employee_id: {e}")
            return None

    @staticmethod
    async def get_multi(
        db: aiomysql.Connection, 
        skip: int = 0, 
        limit: int = 100, 
        area_id: str = None,
        status: str = None
    ) -> List[ShipperOut]:
        """
        Lấy danh sách Shipper có phân trang và lọc.
        """
        try:
            params = []
            query = """
                SELECT s.*, e.full_name, e.phone 
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE 1=1
            """
            
            if area_id:
                query += " AND s.area_id = %s"
                params.append(area_id)
            
            if status:
                query += " AND s.status = %s"
                params.append(status)
                
            query += " ORDER BY s.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, tuple(params))
                results = await cursor.fetchall()
            
            return [ShipperOut(**row) for row in results]
        except Exception as e:
            logger.error(f"❌ Error getting shippers list: {e}")
            return []

    @staticmethod
    async def get_available_shippers_by_area(
        db: aiomysql.Connection, 
        area_id: str, 
        limit: int = 50
    ) -> List[ShipperOut]:
        """
        Lấy danh sách Shipper đang ONLINE trong một khu vực cụ thể.
        Hỗ trợ cho thuật toán Dispatch AI.
        """
        try:
            # Status phải là ONLINE và thuộc area_id
            query = """
                SELECT s.*, e.full_name, e.phone 
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE s.area_id = %s 
                  AND s.status = 'ONLINE'
                LIMIT %s
            """
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (area_id, limit))
                results = await cursor.fetchall()
            
            return [ShipperOut(**row) for row in results]
        except Exception as e:
            logger.error(f"❌ Error getting available shippers: {e}")
            return []

    @staticmethod
    async def update(db: aiomysql.Connection, shipper_id: str, obj_in):
        """
        Hàm update linh hoạt: Chấp nhận cả Dict lẫn Pydantic Model
        """
        try:
            # 1. Chuẩn hóa dữ liệu về dạng Dict
            if isinstance(obj_in, dict):
                update_data = obj_in
            elif hasattr(obj_in, 'model_dump'):
                # Dành cho Pydantic v2
                update_data = obj_in.model_dump(exclude_unset=True)
            elif hasattr(obj_in, 'dict'):
                # Dành cho Pydantic v1 cũ
                update_data = obj_in.dict(exclude_unset=True)
            else:
                raise ValueError("Dữ liệu update không hợp lệ (Phải là Dict hoặc Pydantic Model)")

            # 2. Xây dựng câu SQL động
            fields = []
            values = []
            for k, v in update_data.items():
                fields.append(f"{k} = %s")
                values.append(v)
            
            if not fields:
                return None # Không có gì để update
                
            values.append(shipper_id)
            
            # Cập nhật thời gian updated_at nếu bảng có cột này
            # fields.append("updated_at = NOW()") 
            
            sql = f"UPDATE shippers SET {', '.join(fields)} WHERE shipper_id = %s"
            
            async with db.cursor() as cursor:
                await cursor.execute(sql, tuple(values))
                # Không cần commit ở đây vì Service bên ngoài sẽ quản lý transaction
                return True

        except Exception as e:
            logger.error(f"❌ Error updating shipper {shipper_id}: {e}")
            # QUAN TRỌNG: Phải ném lỗi ra để Service biết mà rollback
            raise e
        
    @staticmethod
    async def get_profile_by_user_id(db: aiomysql.Connection, user_id: str) -> Optional[dict]:
        """
        Lấy profile đầy đủ bằng cách JOIN bảng employees và shippers.
        """
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Thêm e.employee_id vào câu SELECT
            sql = """
                SELECT 
                    e.employee_id,    -- <--- THÊM DÒNG NÀY (Bắt buộc)
                    e.full_name, 
                    e.email, 
                    e.phone, 
                    e.warehouse_id,
                    s.shipper_id, 
                    s.vehicle_type, 
                    s.status, 
                    s.rating, 
                    s.area_id,
                    s.fcm_token,       -- Nên lấy thêm token để debug nếu cần
                    s.current_latitude,
                    s.current_longitude
                FROM employees e
                INNER JOIN shippers s ON e.employee_id = s.employee_id
                WHERE e.user_id = %s
            """
            await cursor.execute(sql, (user_id,))
            result = await cursor.fetchone()
            
            if result:
                # Các trường tính toán thêm (nếu chưa có trong DB thì giả lập hoặc query count riêng)
                result['total_deliveries'] = 156 
                result['success_rate'] = 98.5
                
            return result
        
    @staticmethod
    async def get_by_user_id(db: aiomysql.Connection, user_id: str):
        """
        Tìm Shipper thông qua User ID (Join bảng employees).
        """
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                # JOIN bảng shippers với employees để tìm user_id
                sql = """
                    SELECT s.* FROM shippers s
                    INNER JOIN employees e ON s.employee_id = e.employee_id
                    WHERE e.user_id = %s
                """
                await cursor.execute(sql, (user_id,))
                result = await cursor.fetchone()
                return result
        except Exception as e:
            logger.error(f"❌ Error getting shipper by user_id: {e}")
            return None