import aiomysql
import logging
from datetime import datetime
from fastapi import HTTPException, status
from app.services.barcode_service import BarcodeService

logger = logging.getLogger(__name__)

class JourneyService:

    @staticmethod
    async def process_scan(
        db: aiomysql.Connection, 
        code_value: str, 
        user_id: str,       
        user_role: str,     
        warehouse_id: str = None,
        username: str = ""
    ):
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # 0. === QUAN TRỌNG: Lấy Shipper ID nếu user là SHIPPER ===
            current_shipper_id = None
            if user_role == 'SHIPPER':
                await cursor.execute("""
                    SELECT s.shipper_id 
                    FROM shippers s 
                    JOIN employees e ON s.employee_id = e.employee_id 
                    WHERE e.user_id = %s
                """, (user_id,))
                shipper_data = await cursor.fetchone()
                
                if not shipper_data:
                    raise HTTPException(status_code=403, detail="Tài khoản Shipper chưa được liên kết hồ sơ")
                
                current_shipper_id = shipper_data['shipper_id']
                logger.info(f"🔍 User {user_id} mapped to Shipper ID: {current_shipper_id}")

            # 1. Tìm Barcode
            barcode_info = await BarcodeService.get_barcode_by_code(db, code_value)
            if not barcode_info:
                raise HTTPException(status_code=404, detail="Barcode không tồn tại")
            
            # 2. Lấy Order
            query_order = "SELECT order_id, status FROM orders WHERE barcode_id = %s"
            await cursor.execute(query_order, (barcode_info.barcode_id,))
            order = await cursor.fetchone()
            
            if not order:
                raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

            order_id = order['order_id']

            # 3. Lấy danh sách Legs
            query_legs = "SELECT * FROM order_journey_legs WHERE order_id = %s ORDER BY sequence ASC"
            await cursor.execute(query_legs, (order_id,))
            legs = await cursor.fetchall()

            if not legs:
                raise HTTPException(status_code=400, detail="Đơn hàng chưa có lộ trình")

            # 4. Logic State Machine
            target_leg = None
            action_type = None
            
            for leg in legs:
                # Tìm chặng đang dở dang
                if leg['status'] == 'IN_PROGRESS':
                    target_leg = leg
                    action_type = 'FINISH' 
                    break
                # Tìm chặng chưa bắt đầu
                elif leg['status'] == 'PENDING':
                    target_leg = leg
                    action_type = 'START' 
                    break
            
            if not target_leg:
                return {"message": "Đơn hàng đã hoàn tất", "order_status": "COMPLETED"}

            # 5. === LOGIC MỚI: GÁN TỰ ĐỘNG SHIPPER ===
            
            # Nếu là SHIPPER và chặng này chưa có người nhận (assigned_shipper_id is NULL)
            if user_role == 'SHIPPER' and target_leg['assigned_shipper_id'] is None:
                logger.info(f"🚀 Auto-assigning Leg {target_leg['id']} ({target_leg['leg_type']}) to Shipper {current_shipper_id}")
                
                # Update DB ngay
                await cursor.execute("""
                    UPDATE order_journey_legs 
                    SET assigned_shipper_id = %s 
                    WHERE id = %s
                """, (current_shipper_id, target_leg['id']))
                
                # Update biến local để logic bên dưới chạy đúng
                target_leg['assigned_shipper_id'] = current_shipper_id

            # 6. Validate Quyền (So sánh với Shipper ID)
            if user_role == 'SHIPPER':
                # SỬA LỖI: So sánh với current_shipper_id thay vì user_id
                if str(target_leg['assigned_shipper_id']) != str(current_shipper_id):
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Chặng này thuộc về shipper khác ({target_leg['assigned_shipper_id']}). Bạn ({current_shipper_id}) không thể thao tác."
                    )
            
            # Logic Warehouse Staff (Giữ nguyên)
            if user_role == 'WAREHOUSE_STAFF':
                if target_leg['leg_type'] == 'PICKUP' and target_leg['status'] == 'PENDING':
                    raise HTTPException(status_code=400, detail="Shipper chưa lấy hàng, kho không thể nhập!")

            # 7. Update Status
            new_order_status = order['status']
            now = datetime.utcnow()

            if action_type == 'START':
                await cursor.execute("""
                    UPDATE order_journey_legs 
                    SET status = 'IN_PROGRESS', started_at = %s, updated_at = %s
                    WHERE id = %s
                """, (now, now, target_leg['id']))
                
                if target_leg['leg_type'] in ['PICKUP', 'TRANSFER', 'DELIVERY']:
                    new_order_status = 'IN_TRANSIT'

            elif action_type == 'FINISH':
                await cursor.execute("""
                    UPDATE order_journey_legs 
                    SET status = 'COMPLETED', completed_at = %s, updated_at = %s
                    WHERE id = %s
                """, (now, now, target_leg['id']))
                
                if target_leg['leg_type'] in ['PICKUP', 'TRANSFER']:
                    new_order_status = 'AT_WAREHOUSE'
                elif target_leg['leg_type'] == 'DELIVERY':
                    new_order_status = 'COMPLETED'

            # 8. Update Order Master
            await cursor.execute("""
                UPDATE orders 
                SET status = %s, updated_at = %s
                WHERE order_id = %s
            """, (new_order_status, now, order_id))
            
            await db.commit()
            
            msg = f"Đã cập nhật trạng thái: {new_order_status}"
            if user_role == 'SHIPPER' and action_type == 'START':
                msg = f"Bạn đã nhận chặng {target_leg['leg_type']} thành công!"

            return {
                "status": "success",
                "message": msg,
                "scan_type": action_type,
                "leg_type": target_leg['leg_type'],
                "new_order_status": new_order_status
            }