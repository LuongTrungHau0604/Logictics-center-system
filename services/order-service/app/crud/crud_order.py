import aiomysql
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class CRUDOrder:
    
    @staticmethod
    async def create_order(db: aiomysql.Connection, order_data: dict) -> Dict[str, Any]:
        """Tạo đơn hàng mới trong database."""
        # KHÔNG try...except, KHÔNG commit/rollback để Service quản lý transaction
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Lưu ý: Đã loại bỏ 'active_leg_id' vì không có trong schema bạn cung cấp
            query = """
                INSERT INTO orders (
                    order_id, order_code, sme_id, 
                    receiver_name, receiver_phone, receiver_address,
                    receiver_latitude, receiver_longitude,
                    weight, dimensions, note,
                    status, area_id,
                    barcode_id,
                    created_at, updated_at
                ) VALUES (
                    %(order_id)s, %(order_code)s, %(sme_id)s,
                    %(receiver_name)s, %(receiver_phone)s, %(receiver_address)s,
                    %(receiver_latitude)s, %(receiver_longitude)s,
                    %(weight)s, %(dimensions)s, %(note)s,
                    %(status)s, %(area_id)s,
                    %(barcode_id)s,
                    %(created_at)s, %(updated_at)s
                )
            """
            
            logger.info(f"📝 Executing INSERT for order: {order_data.get('order_code')}")
            await cursor.execute(query, order_data)
            
            # Lấy lại order vừa tạo để trả về.
            await cursor.execute(
                "SELECT * FROM orders WHERE order_id = %s",
                (order_data['order_id'],)
            )
            result = await cursor.fetchone()
            
            if not result:
                logger.error(f"❌ CRITICAL: Order {order_data['order_id']} not found after INSERT!")
                raise Exception(f"Order {order_data['order_id']} not found after INSERT")
                
            logger.info(f"✅ Order {result['order_code']} staged for commit.")
            return result
            

    @staticmethod
    async def get_order_by_id(db: aiomysql.Connection, order_id: str) -> Optional[Dict[str, Any]]:
        """Lấy một đơn hàng bằng order_id."""
        sql = "SELECT * FROM orders WHERE order_id = %s"
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(sql, (order_id,))
            result = await cursor.fetchone()
        return result

    @staticmethod
    async def get_orders_by_sme_id(
        db: aiomysql.Connection, 
        sme_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách đơn hàng thuộc một SME."""
        sql = "SELECT * FROM orders WHERE sme_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(sql, (sme_id, limit, skip))
            results = await cursor.fetchall()
        return results

    @staticmethod
    async def update_order(
        db: aiomysql.Connection, 
        order_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Cập nhật đơn hàng. update_data là dict chỉ chứa các trường cần cập nhật.
        """
        if not update_data:
            return await CRUDOrder.get_order_by_id(db, order_id)

        # Tự động tạo câu lệnh SET
        set_clause = ", ".join([f"`{k}` = %s" for k in update_data.keys()])
        values = list(update_data.values())
        
        # Thêm updated_at tự động (dùng hàm của MySQL)
        set_clause += ", updated_at = UTC_TIMESTAMP()"
        
        # Thêm order_id vào cuối list values cho mệnh đề WHERE
        values.append(order_id)
        
        sql = f"UPDATE orders SET {set_clause} WHERE order_id = %s"
        
        async with db.cursor() as cursor:
            await cursor.execute(sql, tuple(values))
        
        logger.info(f"✅ Order {order_id} staged for update commit.")
        
        # Trả về dữ liệu đã được cập nhật
        return await CRUDOrder.get_order_by_id(db, order_id)

# Tạo instance để sử dụng chung (nếu cần)
crud_order = CRUDOrder()