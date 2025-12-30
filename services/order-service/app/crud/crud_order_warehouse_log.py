# app/crud/crud_order_warehouse_log.py

import aiomysql
from typing import List, Optional
from datetime import datetime
import logging

from app.schemas.order_warehouse_log import OrderWarehouseLogCreate, OrderWarehouseLogOut

logger = logging.getLogger(__name__)

class CRUDOrderWarehouseLog:
    """CRUD operations cho OrderWarehouseLog"""
    
    @staticmethod
    async def create_log(
        db: aiomysql.Connection,
        log_data: OrderWarehouseLogCreate,
        scanned_by: Optional[str] = None
    ) -> OrderWarehouseLogOut:
        """
        Tạo log mới khi scan barcode.
        
        Args:
            db: Database connection
            log_data: Dữ liệu log cần tạo
            scanned_by: User ID của người scan
            
        Returns:
            OrderWarehouseLogOut: Log vừa tạo
        """
        try:
            import uuid
            log_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            async with db.cursor(aiomysql.DictCursor) as cursor:
                query = """
                    INSERT INTO order_warehouse_logs 
                    (log_id, order_id, warehouse_id, scanned_by, scanned_at, action, note, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                await cursor.execute(query, (
                    log_id,
                    log_data.order_id,
                    log_data.warehouse_id,
                    scanned_by or log_data.scanned_by,
                    now,
                    log_data.action,
                    log_data.note,
                    now
                ))
                
                await db.commit()
                
                # Lấy lại record vừa tạo
                await cursor.execute(
                    "SELECT * FROM order_warehouse_logs WHERE log_id = %s",
                    (log_id,)
                )
                result = await cursor.fetchone()
                
                return OrderWarehouseLogOut.model_validate(result)
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo warehouse log: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_order_history(
        db: aiomysql.Connection,
        order_id: str
    ) -> List[OrderWarehouseLogOut]:
        """
        Lấy toàn bộ lịch sử di chuyển của đơn hàng.
        
        Args:
            db: Database connection
            order_id: ID đơn hàng
            
        Returns:
            List[OrderWarehouseLogOut]: Danh sách logs theo thời gian
        """
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                query = """
                    SELECT * FROM order_warehouse_logs 
                    WHERE order_id = %s 
                    ORDER BY scanned_at DESC
                """
                
                await cursor.execute(query, (order_id,))
                results = await cursor.fetchall()
                
                return [OrderWarehouseLogOut.model_validate(row) for row in results]
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy lịch sử đơn hàng {order_id}: {e}")
            raise
    
    @staticmethod
    async def get_warehouse_logs(
        db: aiomysql.Connection,
        warehouse_id: str,
        limit: int = 50
    ) -> List[OrderWarehouseLogOut]:
        """
        Lấy danh sách đơn hàng đã qua kho.
        
        Args:
            db: Database connection
            warehouse_id: ID kho
            limit: Số lượng records trả về
            
        Returns:
            List[OrderWarehouseLogOut]: Danh sách logs
        """
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                query = """
                    SELECT * FROM order_warehouse_logs 
                    WHERE warehouse_id = %s 
                    ORDER BY scanned_at DESC
                    LIMIT %s
                """
                
                await cursor.execute(query, (warehouse_id, limit))
                results = await cursor.fetchall()
                
                return [OrderWarehouseLogOut.model_validate(row) for row in results]
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy logs của kho {warehouse_id}: {e}")
            raise

# Singleton instance
crud_order_warehouse_log = CRUDOrderWarehouseLog()
