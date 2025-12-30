# app/services/order_service.py

import httpx
import aiomysql
import logging
import uuid
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
from app.core.config import settings
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from app.schemas.user import UserOut
from app.crud.crud_order import CRUDOrder
from app.services.barcode_service import BarcodeService
from app.services.area_service import AreaService
from app.core.firebase import push_notification_to_firebase # <--- 1. IMPORT HÀM GỬI FIREBASE

logger = logging.getLogger(__name__)

# --- Helper Function để gọi Geocoding Service ---

async def call_geocoding_service(address: str) -> tuple[float, float]:
    """
    Gọi đến AI-Agent-Service để lấy tọa độ.
    """
    geocode_url = f"{settings.AI_AGENT_SERVICE_URL}/geocoding/geocode"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                geocode_url, 
                json={"address": address},
                timeout=10.0
            )
        
        response.raise_for_status() 
        
        data = response.json()
        
        if not data.get("is_valid") or not data.get("is_vietnam"):
             logger.warning(f"Địa chỉ không hợp lệ hoặc ngoài VN: {address}")
             raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail=f"Địa chỉ không hợp lệ hoặc nằm ngoài lãnh thổ VN: {address}"
             )
             
        return data["latitude"], data["longitude"]

    except httpx.HTTPStatusError as e:
        if e.response.status_code == status.HTTP_404_NOT_FOUND:
            logger.error(f"Geocoding 404: Không tìm thấy tọa độ cho: {address}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Không thể tìm thấy tọa độ cho địa chỉ: {address}"
            )
        logger.error(f"Lỗi HTTP khi gọi Geocoding: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Dịch vụ Geocoding đang gặp sự cố"
        )
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi gọi Geocoding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Lỗi hệ thống khi xử lý địa chỉ"
        )

# --- Order Service chính ---

class OrderService:
    @staticmethod
    async def create_order(
        db: aiomysql.Connection, 
        order_data: OrderCreate, 
        current_user: UserOut
    ) -> OrderOut:
    
        logger.info(f"Bắt đầu tạo đơn hàng cho SME: {current_user.sme_id}")
        
        try:
            # === 1. Lấy SME ID và thông tin SME ===
            sme_id = current_user.sme_id
            if not sme_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tài khoản của bạn không thuộc doanh nghiệp nào."
                )

            # === 1.1. Lấy thông tin SME từ database ===
            # SỬA LỖI: Select latitude, longitude trực tiếp thay vì ST_X/ST_Y(coordinates)
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT 
                        sme_id, 
                        business_name, 
                        address, 
                        area_id, 
                        longitude, 
                        latitude,
                        status  
                    FROM sme 
                    WHERE sme_id = %s
                """, (sme_id,))
                sme_info = await cursor.fetchone()
                
                if not sme_info:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Không tìm thấy thông tin SME với ID: {sme_id}"
                    )
                
                if sme_info['status'] != 'ACTIVE':
                    # Nếu là PENDING hoặc INACTIVE/LOCKED thì chặn luôn
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Tài khoản doanh nghiệp chưa được kích hoạt hoặc đang bị khóa. Vui lòng liên hệ Admin."
                    )
                area_id = sme_info.get('area_id')
                sme_latitude = sme_info.get('latitude')
                sme_longitude = sme_info.get('longitude')
                
                if not area_id:
                    logger.warning(f"⚠️ SME ID {sme_id} không có area_id, sử dụng fallback.")
                    area_id = "DEFAULT_AREA" 
                    
            # === 2. Geocode RECEIVER address ===
            receiver_latitude, receiver_longitude = await call_geocoding_service(order_data.receiver_address)
            logger.info(f"📍 Receiver coordinates: ({receiver_latitude:.6f}, {receiver_longitude:.6f})")

            # === 3. Tạo Barcode ===
            order_id = str(uuid.uuid4())
            barcode = await BarcodeService.create_barcode_for_order(db, order_id)
            barcode_id = barcode.barcode_id
            
            logger.info(f"📱 Barcode được tạo: {barcode.code_value}")
            
            # === 4. Chuẩn bị dữ liệu order ===
            order_code = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
            order_db_data = order_data.model_dump()
            
            # Update các trường vào dict để Insert
            order_db_data.update({
                "order_id": order_id,
                "order_code": order_code,
                "barcode_id": barcode_id,
                "sme_id": sme_id,
                
                # Lưu lat/lon riêng biệt (Decimal)
                "receiver_latitude": receiver_latitude, 
                "receiver_longitude": receiver_longitude, 
                
                "status": "PENDING",
                "area_id": area_id,
                "active_leg_id": None, # Cột này có thể không có trong bảng Orders mới của bạn, hãy kiểm tra lại CRUDOrder
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            # === 5. Lưu order vào DB ===
            # Lưu ý: CRUDOrder.create_order cần phải được cập nhật câu INSERT tương ứng
            created_order = await CRUDOrder.create_order(db, order_db_data)
            
            if not created_order:
                raise HTTPException(status_code=500, detail="Không thể lưu đơn hàng.")
            await db.commit()
            logger.info(f"✅ Đơn hàng {order_code} đã được lưu vào DB.")
            
            
            logger.info("🔔 [NOTI DEBUG] >>> Bắt đầu logic gửi thông báo...") 

            try:
                async with db.cursor(aiomysql.DictCursor) as cursor:
                    # Log xem đang làm gì
                    logger.info("🔔 [NOTI DEBUG] Đang query tìm Admin trong DB...")
                    
                    # 1. Tìm User ID của Admin
                    await cursor.execute("""
                        SELECT user_id FROM user WHERE role = 'ADMIN' LIMIT 1
                    """)
                    admin_row = await cursor.fetchone()
                    
                    if admin_row:
                        admin_id = admin_row['user_id']
                        logger.info(f"🔔 [NOTI DEBUG] Tìm thấy Admin ID: {admin_id} -> Gọi Firebase ngay!")
                        
                        # 2. Gọi hàm gửi (Hàm này giờ đã có log bên trong)
                        push_notification_to_firebase(
                            user_id=admin_id,
                            title="📦 Đơn hàng mới!",
                            message=f"SME {sme_info['business_name']} vừa tạo đơn mới: {order_code}",
                            type="INFO"
                        )
                    else:
                        logger.warning("⚠️ [NOTI DEBUG] Query trả về RỖNG! Không có nhân viên nào có role='ADMIN'.")

            except Exception as e:
                logger.error(f"❌ [NOTI DEBUG] Lỗi văng ra trong block thông báo: {e}")
            
            logger.info("🔔 [NOTI DEBUG] <<< Kết thúc logic gửi thông báo.")
            # === 6. Log kết quả ===
            logger.info(f"✅ Đơn hàng {order_code} được tạo thành công:")
            # Handle trường hợp sme_latitude/longitude có thể là None
            sme_lat_log = f"({sme_latitude:.6f}, {sme_longitude:.6f})" if sme_latitude and sme_longitude else "(No Coords)"
            logger.info(f"   📍 SME: {sme_info['business_name']} {sme_lat_log}")
            logger.info(f"   📍 Receiver: {order_data.receiver_address} ({receiver_latitude:.6f}, {receiver_longitude:.6f})")
            logger.info(f"   🗺️ Area: {area_id}")
            
            return OrderOut.model_validate(created_order)
            
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Lỗi khi tạo đơn hàng: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi CSDL: {str(e)}"
            )

    @staticmethod
    async def get_orders_by_sme(
        db: aiomysql.Connection, 
        current_user: UserOut
    ) -> List[OrderOut]:

        """
        Lấy tất cả các đơn hàng thuộc về một SME.
        """
        sme_id = current_user.sme_id
        logger.info(f"Đang lấy danh sách đơn hàng cho SME ID: {sme_id}")

        if not sme_id:
            return []
        
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                # SELECT * vẫn hoạt động tốt vì bảng orders đã có cột receiver_latitude/longitude
                query = """
                    SELECT * FROM orders 
                    WHERE sme_id = %s 
                    ORDER BY created_at DESC
                """
                await cursor.execute(query, (sme_id,))
                order_rows = await cursor.fetchall()
            
            orders = [OrderOut.model_validate(row) for row in order_rows]
            
            logger.info(f"Tìm thấy {len(orders)} đơn hàng cho SME {sme_id}")
            return orders
        
        except Exception as e:
            logger.error(f"Lỗi CSDL khi lấy đơn hàng cho SME {sme_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể truy xuất danh sách đơn hàng: {str(e)}"
            )

    @staticmethod
    async def get_pickup_tasks_by_shipper(
        db: aiomysql.Connection, 
        user_id: str 
    ) -> List[dict]:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # --- SỬA LẠI LOGIC MAPPING ---
            # Join bảng shippers và employees để tìm shipper_id từ user_id
            await cursor.execute("""
                SELECT s.shipper_id, e.full_name
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE e.user_id = %s
            """, (user_id,))
            
            shipper_row = await cursor.fetchone()
            
            if not shipper_row:
                logger.warning(f"⚠️ User {user_id} có role SHIPPER nhưng chưa được tạo profile trong bảng 'shippers' hoặc 'employees'")
                return []
            
            actual_shipper_id = shipper_row['shipper_id']
            logger.info(f"🔄 Mapping: User '{user_id}' -> Employee -> Shipper '{actual_shipper_id}' ({shipper_row['full_name']})")

            # --- Query chính (dùng actual_shipper_id) ---
            query = """
                SELECT 
                    o.*, 
                    l.status as leg_status,
                    l.id as leg_id,
                    l.assigned_shipper_id,
                    s.business_name as sender_name,
                    s.contact_phone as sender_phone,
                    s.address as pickup_address
                FROM orders o
                INNER JOIN order_journey_legs l ON o.order_id = l.order_id
                LEFT JOIN sme s ON o.sme_id = s.sme_id
                WHERE l.assigned_shipper_id = %s
                  AND l.leg_type = 'PICKUP'
                  AND l.status != 'CANCELLED'
                ORDER BY l.created_at DESC
            """
            await cursor.execute(query, (actual_shipper_id,))
            tasks = await cursor.fetchall()
            
            logger.info(f"✅ Found {len(tasks)} pickup tasks for Shipper ID {actual_shipper_id}")
            return tasks

    @staticmethod
    async def get_delivery_tasks_by_shipper(
        db: aiomysql.Connection, 
        user_id: str
    ):
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # --- SỬA LẠI LOGIC MAPPING ---
            await cursor.execute("""
                SELECT s.shipper_id, e.full_name
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE e.user_id = %s
            """, (user_id,))
            
            shipper_row = await cursor.fetchone()
            
            if not shipper_row:
                logger.warning(f"⚠️ User {user_id} không tìm thấy profile Shipper")
                return []
            
            actual_shipper_id = shipper_row['shipper_id']
            logger.info(f"🔄 Mapping: User '{user_id}' -> Employee -> Shipper '{actual_shipper_id}'")

            # --- Query chính ---
            query = """
                SELECT 
                    l.id as leg_id,
                    l.status as leg_status, 
                    l.leg_type,             
                    o.order_id,
                    o.order_code,
                    o.receiver_name,
                    o.receiver_phone,
                    o.receiver_address as delivery_address, 
                    o.receiver_latitude,   -- <--- MỚI
                    o.receiver_longitude,  -- <--- MỚI
                    o.weight,
                    o.note
                FROM order_journey_legs l
                JOIN orders o ON l.order_id = o.order_id
                WHERE l.assigned_shipper_id = %s 
                AND l.leg_type = 'DELIVERY'
                ORDER BY l.created_at DESC
            """
            await cursor.execute(query, (actual_shipper_id,))
            tasks = await cursor.fetchall()
            
            logger.info(f"✅ Found {len(tasks)} delivery tasks for Shipper ID {actual_shipper_id}")
            return tasks
        
    

    @staticmethod
    async def update_order(
        db: aiomysql.Connection,
        order_id: str,
        update_data: OrderUpdate,
        current_user: UserOut
    ) -> OrderOut:
        sme_id = current_user.sme_id
        
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                # 1. Kiểm tra đơn hàng tồn tại và thuộc về SME này, và status là PENDING
                await cursor.execute("""
                    SELECT * FROM orders 
                    WHERE order_id = %s AND sme_id = %s
                """, (order_id, sme_id))
                order = await cursor.fetchone()

                if not order:
                    raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại hoặc không thuộc quyền quản lý.")
                
                if order['status'] != 'PENDING':
                    raise HTTPException(status_code=400, detail="Chỉ có thể chỉnh sửa đơn hàng khi đang ở trạng thái PENDING.")

                # 2. Thực hiện Update (Chỉ update các trường có giá trị)
                # Lọc các trường không None
                fields_to_update = update_data.model_dump(exclude_unset=True)
                if not fields_to_update:
                    return OrderOut.model_validate(order) # Không có gì thay đổi

                fields_to_update['updated_at'] = datetime.utcnow()

                set_clause = ", ".join([f"{k} = %s" for k in fields_to_update.keys()])
                values = list(fields_to_update.values())
                values.append(order_id) # Cho WHERE clause

                query = f"UPDATE orders SET {set_clause} WHERE order_id = %s"
                await cursor.execute(query, tuple(values))
                await db.commit()

                # 3. Lấy lại thông tin mới nhất
                await cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
                updated_order = await cursor.fetchone()
                
                return OrderOut.model_validate(updated_order)

        except Exception as e:
            logger.error(f"Lỗi update đơn hàng: {e}")
            await db.rollback()
            if isinstance(e, HTTPException): raise e
            raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

    @staticmethod
    async def cancel_order(
        db: aiomysql.Connection,
        order_id: str,
        current_user: UserOut
    ):
        sme_id = current_user.sme_id
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                # 1. Kiểm tra quyền và trạng thái
                await cursor.execute("SELECT status FROM orders WHERE order_id = %s AND sme_id = %s", (order_id, sme_id))
                order = await cursor.fetchone()

                if not order:
                    raise HTTPException(status_code=404, detail="Đơn hàng không tìm thấy.")
                
                if order['status'] != 'PENDING':
                    raise HTTPException(status_code=400, detail="Không thể hủy đơn hàng đã được xử lý hoặc đang vận chuyển.")

                # 2. Cập nhật trạng thái sang CANCELLED
                await cursor.execute("""
                    UPDATE orders 
                    SET status = 'CANCELLED', updated_at = %s 
                    WHERE order_id = %s
                """, (datetime.utcnow(), order_id))
                
                await db.commit()
                return {"message": "Đơn hàng đã được hủy thành công."}

        except Exception as e:
            logger.error(f"Lỗi hủy đơn hàng: {e}")
            await db.rollback()
            if isinstance(e, HTTPException): raise e
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi hủy đơn.")
    # app/services/order_service.py

    @staticmethod
    async def get_all_orders_for_admin(
        db: aiomysql.Connection
    ) -> List[OrderOut]:
        """
        Lấy tất cả đơn hàng trong hệ thống (Dành cho Admin).
        """
        try:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                # Query lấy tất cả đơn hàng, sắp xếp mới nhất lên đầu
                query = """
                    SELECT * FROM orders 
                    ORDER BY created_at DESC
                """
                await cursor.execute(query)
                order_rows = await cursor.fetchall()
            
            # Validate và chuyển đổi sang Pydantic model
            orders = [OrderOut.model_validate(row) for row in order_rows]
            return orders
        
        except Exception as e:
            logger.error(f"Lỗi CSDL khi lấy toàn bộ đơn hàng: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể truy xuất danh sách đơn hàng hệ thống: {str(e)}"
            )


    @staticmethod
    async def complete_delivery_task(
        db: aiomysql.Connection,
        order_id: str,
        user_id: str
    ):
        """
        Shipper xác nhận giao hàng thành công.
        """
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # A. Lấy Shipper ID từ User ID (Giữ nguyên logic cũ)
            await cursor.execute("""
                SELECT s.shipper_id 
                FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE e.user_id = %s
            """, (user_id,))
            shipper_row = await cursor.fetchone()
            
            if not shipper_row:
                raise HTTPException(status_code=403, detail="Không tìm thấy thông tin Shipper.")
            
            shipper_id = shipper_row['shipper_id']

            # B. Kiểm tra nhiệm vụ (Giữ nguyên logic cũ)
            await cursor.execute("""
                SELECT id FROM order_journey_legs 
                WHERE order_id = %s 
                  AND assigned_shipper_id = %s 
                  AND leg_type = 'DELIVERY'
                  AND status IN ('PENDING', 'IN_PROGRESS')
            """, (order_id, shipper_id))
            
            leg_row = await cursor.fetchone()
            if not leg_row:
                raise HTTPException(status_code=404, detail="Không tìm thấy nhiệm vụ giao hàng.")

            try:
                # C. Cập nhật trạng thái (Giữ nguyên logic cũ)
                await cursor.execute("""
                    UPDATE order_journey_legs 
                    SET status = 'COMPLETED', updated_at = NOW()
                    WHERE id = %s
                """, (leg_row['id'],))

                await cursor.execute("""
                    UPDATE orders 
                    SET status = 'COMPLETED', updated_at = NOW()
                    WHERE order_id = %s
                """, (order_id,))

                # === 🆕 PHẦN MỚI: LẤY THÔNG TIN SME ĐỂ GỬI MAIL ===
                # Chúng ta cần email, business_name của SME và order_code
                await cursor.execute("""
                    SELECT 
                        s.email, 
                        s.business_name, 
                        o.order_code 
                    FROM orders o
                    JOIN sme s ON o.sme_id = s.sme_id
                    WHERE o.order_id = %s
                """, (order_id,))
                
                sme_info = await cursor.fetchone()
                
                await db.commit()

                # Trả về data bao gồm thông tin SME để Controller xử lý Background Task
                return {
                    "message": "Giao hàng thành công", 
                    "order_id": order_id,
                    "email_info": sme_info if sme_info else None # Gửi kèm info ra ngoài
                }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Lỗi hoàn thành đơn: {e}")
                raise HTTPException(status_code=500, detail="Lỗi hệ thống khi cập nhật trạng thái.")