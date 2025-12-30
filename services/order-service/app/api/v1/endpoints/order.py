# services/order-service/app/api/v1/endpoints/order.py

from fastapi import APIRouter, Depends, HTTPException, status
import aiomysql
import logging
from typing import List
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from app.schemas.user import UserOut
from app.schemas.barcode import BarcodeOut
from app.services.order_service import OrderService
from app.api.v1.deps import get_current_user, get_db, get_current_sme_owner
from app.services.barcode_service import BarcodeService
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks # <--- Nhớ import cái này
from app.services.email_service import send_sme_notification_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/create", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner)
):
    """
    Tạo đơn hàng mới cho SME.
    Dependency 'get_db' sẽ tự động commit hoặc rollback.
    """
    logger.info(f"🚀 Creating order for user: {current_user.username} (SME: {current_user.sme_id})")
    
    # Chỉ cần gọi service. 
    # Nếu service ném lỗi (HTTPException, DBError, v.v.),
    # 'get_db' sẽ tự động bắt, rollback, và ném lỗi đó ra.
    new_order = await OrderService.create_order(
        db=db,
        order_data=order_data,
        current_user=current_user
    )
    
    logger.info(f"✅ Order created successfully: {new_order.order_code}")
    return new_order



@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: str,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner)
):
    """
    Lấy chi tiết một đơn hàng
    TODO: Implement khi có CRUD methods
    """
    logger.info(f"📦 Getting order {order_id} for user: {current_user.username}")
    
    # Khi ném HTTPException, 'get_db' cũng sẽ bắt được,
    # rollback (an toàn) và ném lỗi ra.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get order endpoint not implemented yet"
    )

@router.get("/{order_id}/barcode", response_model=BarcodeOut)
async def get_order_barcode(
    order_id: str,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner)
):
    """
    Lấy thông tin barcode của đơn hàng VÀ hình ảnh Base64
    """
    logger.info(f"📱 Getting barcode for order {order_id}")
    
    async with db.cursor(aiomysql.DictCursor) as cursor:
        # 1. Lấy thông tin barcode từ Database
        query = """
            SELECT b.* FROM barcode b
            INNER JOIN orders o ON o.barcode_id = b.barcode_id
            WHERE o.order_id = %s AND o.sme_id = %s
        """
        
        await cursor.execute(query, (order_id, current_user.sme_id))
        result = await cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order or barcode not found"
            )
        
        # 2. 👇 QUAN TRỌNG: Tạo hình ảnh từ code_value
        # Frontend cần chuỗi Base64 này để hiển thị thẻ <img>
        try:
            code_value = result['code_value']
            image_base64 = BarcodeService.generate_barcode_image(code_value)
        except Exception as e:
            logger.error(f"Lỗi khi generate ảnh barcode: {e}")
            raise HTTPException(status_code=500, detail="Error generating barcode image")

        # 3. Trả về Dictionary chứa cả thông tin text và hình ảnh
        return {
            "barcode_id": result['barcode_id'],
            "code_value": code_value,
            "barcode_image": image_base64, # <--- Frontend đang tìm cái này
            "generated_at": result['generated_at']
        }
        
        
@router.get("/shipper/my-pickups")
async def get_my_pickup_tasks(
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Endpoint dành cho SHIPPER xem danh sách các đơn cần đi lấy hàng (PICKUP).
    """
    # Log để debug xem User ID là gì
    logger.info(f"🔍 Pickup Request from Shipper: {current_user.user_id} (Role: {current_user.role})")

    if current_user.role != 'SHIPPER':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Shipper mới có quyền truy cập endpoint này"
        )

    try:
        tasks = await OrderService.get_pickup_tasks_by_shipper(db, current_user.user_id)
        
        # Log kết quả trả về
        logger.info(f"✅ Found {len(tasks)} pickup tasks for shipper {current_user.user_id}")
        return tasks
    except Exception as e:
        logger.error(f"❌ Error fetching pickups: {e}")
        raise HTTPException(status_code=500, detail="Lỗi server khi lấy danh sách pickup")


@router.get("/shipper/my-deliveries")
async def get_my_delivery_tasks(
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Lấy danh sách các đơn cần GIAO (DELIVERY) của Shipper.
    """
    logger.info(f"🔍 Delivery Request from Shipper: {current_user.user_id}")

    if current_user.role != 'SHIPPER':
        raise HTTPException(status_code=403, detail="Chỉ dành cho Shipper")

    try:
        tasks = await OrderService.get_delivery_tasks_by_shipper(db, current_user.user_id)
        
        logger.info(f"✅ Found {len(tasks)} delivery tasks for shipper {current_user.user_id}")
        return tasks
    except Exception as e:
        logger.error(f"❌ Error fetching deliveries: {e}")
        raise HTTPException(status_code=500, detail="Lỗi server khi lấy danh sách delivery")

@router.put("/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner)
):
    """
    Chỉnh sửa thông tin đơn hàng (Chỉ khi PENDING).
    """
    logger.info(f"✏️ Updating order {order_id} by {current_user.username}")
    return await OrderService.update_order(db, order_id, order_data, current_user)

@router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner)
):
    """
    Hủy đơn hàng (Chỉ khi PENDING).
    """
    logger.info(f"❌ Cancelling order {order_id} by {current_user.username}")
    return await OrderService.cancel_order(db, order_id, current_user)

@router.get("/", response_model=List[OrderOut])
async def get_orders(
    db: aiomysql.Connection = Depends(get_db),
    # Thay đổi dependency từ get_current_sme_owner -> get_current_user
    # Để cho phép cả Admin và SME truy cập endpoint này
    current_user: UserOut = Depends(get_current_user) 
):
    """
    Lấy danh sách đơn hàng.
    - Nếu là ADMIN: Trả về toàn bộ đơn hàng hệ thống.
    - Nếu là SME_OWNER: Trả về đơn hàng của SME đó.
    """
    logger.info(f"📋 Getting orders for user: {current_user.username} (Role: {current_user.role})")
    
    # 1. Logic cho ADMIN
    if current_user.role == 'ADMIN':
        logger.info("👑 Admin requesting all orders.")
        return await OrderService.get_all_orders_for_admin(db)

    # 2. Logic cho SME OWNER
    elif current_user.role == 'SME_OWNER':
        if not current_user.sme_id:
            logger.warning(f"SME User {current_user.username} không có SME ID.")
            return []
        logger.info(f"🏢 SME Owner requesting orders for SME: {current_user.sme_id}")
        return await OrderService.get_orders_by_sme(db, current_user)

    # 3. Các role khác (Shipper, Staff...) -> Từ chối hoặc trả rỗng
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem danh sách tổng hợp đơn hàng."
        )
# --- THÊM ĐOẠN NÀY VÀO CUỐI FILE orders.py ---

@router.get("/{order_id}/barcode") 
async def get_order_barcode_image(
    order_id: str,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Lấy hình ảnh Barcode (Base64). 
    Dùng JSONResponse để trả về field 'image' mà không bị Pydantic lọc mất.
    """
    try:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # 1. Tìm code_value từ bảng orders
            query = """
                SELECT b.code_value, b.barcode_id
                FROM orders o
                JOIN barcode b ON o.barcode_id = b.barcode_id
                WHERE o.order_id = %s
            """
            await cursor.execute(query, (order_id,))
            result = await cursor.fetchone()
            
            code_value = ""
            
            # 2. Logic tạo mới nếu chưa có (Fallback)
            if not result:
                # Kiểm tra xem order có tồn tại không trước khi tạo barcode
                await cursor.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
                if not await cursor.fetchone():
                     raise HTTPException(status_code=404, detail="Order not found")

                # Tạo barcode mới
                new_barcode = await BarcodeService.create_barcode_for_order(db, order_id)
                await db.commit()
                code_value = new_barcode.code_value
            else:
                code_value = result['code_value']

            # 3. Tạo ảnh Base64
            image_base64 = BarcodeService.generate_barcode_image(code_value)

            # 4. Trả về JSONResponse (Bypass Pydantic validation)
            return JSONResponse(content={
                "order_id": order_id,
                "code_value": code_value,
                "image": image_base64  # Field quan trọng nhất
            })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating barcode: {e}") # Log lỗi ra console để debug
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

@router.put("/shipper/complete-delivery/{order_id}")
async def complete_delivery(
    order_id: str,
    background_tasks: BackgroundTasks, # <--- Inject BackgroundTasks
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Shipper xác nhận đã giao hàng xong.
    Update Order Status -> COMPLETED -> Gửi mail cho SME.
    """
    logger.info(f"✅ Shipper {current_user.user_id} completing delivery for Order {order_id}")

    if current_user.role != 'SHIPPER':
        raise HTTPException(status_code=403, detail="Chỉ Shipper mới có quyền này")

    # Gọi Service
    result = await OrderService.complete_delivery_task(db, order_id, current_user.user_id)
    
    # 🚀 Kích hoạt Background Task gửi Email
    email_info = result.get("email_info")
    if email_info and email_info.get("email"):
        background_tasks.add_task(
            send_sme_notification_email,
            sme_email=email_info["email"],
            sme_name=email_info["business_name"],
            order_code=email_info["order_code"]
        )
        logger.info(f"📨 Đã xếp lịch gửi mail cho SME: {email_info['email']}")

    return result