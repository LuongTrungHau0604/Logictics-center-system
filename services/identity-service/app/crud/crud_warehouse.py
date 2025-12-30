import aiomysql
import logging
import uuid
from typing import List, Optional, Dict, Any
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseOut

logger = logging.getLogger(__name__)

class CRUDWarehouse:
    
    @staticmethod
    async def create(db: aiomysql.Connection, obj_in: WarehouseCreate) -> Optional[Dict[str, Any]]:
        """
        Tạo mới một kho hàng.
        """
        try:
            warehouse_id = f"WH-{uuid.uuid4().hex[:8].upper()}"
            
            query = """
                INSERT INTO warehouses (
                    warehouse_id, name, address, type, 
                    capacity_limit, current_load, area_id, 
                    status, contact_phone, latitude, longitude, 
                    created_at
                ) VALUES (
                    %(warehouse_id)s, %(name)s, %(address)s, %(type)s, 
                    %(capacity_limit)s, %(current_load)s, %(area_id)s, 
                    %(status)s, %(contact_phone)s, %(latitude)s, %(longitude)s, 
                    NOW()
                )
            """
            
            # Convert Pydantic model to dict
            data = obj_in.model_dump()
            data['warehouse_id'] = warehouse_id
            # Ensure current_load has a default value if None
            if data.get('current_load') is None:
                data['current_load'] = 0
            
            async with db.cursor() as cursor:
                await cursor.execute(query, data)
                await db.commit()
            
            # Trả về dữ liệu vừa tạo (để frontend dùng ngay nếu cần)
            data['created_at'] = datetime.utcnow() # Giả lập giá trị trả về
            return data
            
        except Exception as e:
            logger.error(f"❌ Error creating warehouse: {e}")
            await db.rollback()
            raise e

    @staticmethod
    async def get_by_id(db: aiomysql.Connection, warehouse_id: str) -> Optional[WarehouseOut]:
        """Lấy thông tin kho theo ID."""
        try:
            query = "SELECT * FROM warehouses WHERE warehouse_id = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (warehouse_id,))
                result = await cursor.fetchone()
                
            if result:
                return WarehouseOut(**result)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting warehouse by id: {e}")
            return None

    @staticmethod
    async def get_multi(
        db: aiomysql.Connection, 
        skip: int = 0, 
        limit: int = 100, 
        area_id: str = None,
        status: str = None,
        type: str = None
    ) -> List[WarehouseOut]:
        """
        Lấy danh sách kho có phân trang và lọc.
        """
        try:
            params = []
            query = "SELECT * FROM warehouses WHERE 1=1"
            
            if area_id:
                query += " AND area_id = %s"
                params.append(area_id)
            
            if status:
                query += " AND status = %s"
                params.append(status)
                
            if type:
                query += " AND type = %s"
                params.append(type)
                
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, tuple(params))
                results = await cursor.fetchall()
            
            return [WarehouseOut(**row) for row in results]
        except Exception as e:
            logger.error(f"❌ Error getting warehouses list: {e}")
            return []

    @staticmethod
    async def update(
        db: aiomysql.Connection, 
        warehouse_id: str, 
        obj_in: WarehouseUpdate
    ) -> Optional[WarehouseOut]:
        """
        Cập nhật thông tin kho.
        """
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            if not update_data:
                return await CRUDWarehouse.get_by_id(db, warehouse_id)

            set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
            values = list(update_data.values())
            values.append(warehouse_id)

            query = f"UPDATE warehouses SET {set_clause}, updated_at = NOW() WHERE warehouse_id = %s"

            async with db.cursor() as cursor:
                await cursor.execute(query, tuple(values))
                await db.commit()

            return await CRUDWarehouse.get_by_id(db, warehouse_id)
        except Exception as e:
            logger.error(f"❌ Error updating warehouse: {e}")
            await db.rollback()
            return None

    @staticmethod
    async def delete(db: aiomysql.Connection, warehouse_id: str) -> bool:
        """Xóa kho (cần cẩn trọng, thường chỉ nên đổi status sang INACTIVE)."""
        try:
            query = "DELETE FROM warehouses WHERE warehouse_id = %s"
            async with db.cursor() as cursor:
                await cursor.execute(query, (warehouse_id,))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting warehouse: {e}")
            await db.rollback()
            return False