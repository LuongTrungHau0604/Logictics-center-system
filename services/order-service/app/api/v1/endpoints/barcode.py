# app/api/v1/endpoints/barcode.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import aiomysql
import logging

from app.api.v1.deps import get_db, get_current_user
from app.schemas.user import UserOut
from app.schemas.barcode import BarcodeOut
from app.schemas.order_warehouse_log import (
    BarcodeScanRequest,
    BarcodeScanResponse,
    OrderWarehouseLogCreate,
    OrderWarehouseLogOut
)
from app.schemas.barcode import ScanActionType


from app.services.barcode_service import BarcodeService
from app.crud.crud_order_warehouse_log import crud_order_warehouse_log

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/barcodes", tags=["barcodes"])

@router.post("/scan", response_model=BarcodeScanResponse)
async def scan_barcode(
    scan_data: BarcodeScanRequest,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Endpoint xử lý quét mã đa năng:
    - PICKUP_CONFIRM: Shipper lấy hàng
    - WAREHOUSE_IN: Nhập kho
    - WAREHOUSE_OUT: Xuất kho
    - DELIVERY_START: Shipper đi giao
    - DELIVERY_COMPLETE: Giao thành công
    """
    logger.info(f"🔔 SCAN EVENT: User {current_user.username} - Action {scan_data.action} - Code {scan_data.code_value}")

    # 1. Tìm Order & Shipper Profile (Nếu user là shipper)
    async with db.cursor(aiomysql.DictCursor) as cursor:
        # Lấy thông tin Order từ Barcode
        await cursor.execute("""
            SELECT o.*, b.barcode_id 
            FROM orders o
            JOIN barcode b ON o.barcode_id = b.barcode_id
            WHERE b.code_value = %s
        """, (scan_data.code_value,))
        order = await cursor.fetchone()
        
        if not order:
            raise HTTPException(status_code=404, detail="Barcode không tồn tại hoặc không gắn với đơn hàng nào")

        # Lấy Shipper ID nếu user hiện tại là Shipper
        shipper_id = None
        if current_user.role == "SHIPPER":
            await cursor.execute("""
                SELECT s.shipper_id FROM shippers s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE e.user_id = %s
            """, (current_user.user_id,))
            shipper_row = await cursor.fetchone()
            if shipper_row:
                shipper_id = shipper_row['shipper_id']

    # 2. Xử lý Logic theo từng Action
    async with db.cursor(aiomysql.DictCursor) as cursor:
        order_id = order['order_id']
        message = ""
        log_created_id = None

        # --- CASE 1: PICKUP_CONFIRM (Shipper lấy hàng) ---
        if scan_data.action == ScanActionType.PICKUP_CONFIRM:
            # Cập nhật chặng PICKUP -> IN_PROGRESS
            await cursor.execute("""
                UPDATE order_journey_legs 
                SET status = 'IN_PROGRESS', started_at = NOW()
                WHERE order_id = %s AND leg_type = 'PICKUP' AND status = 'PENDING'
            """, (order_id,))
            
            if cursor.rowcount > 0:
                 message = "Đã xác nhận lấy hàng thành công."
                 await cursor.execute("UPDATE orders SET status = 'IN_TRANSIT' WHERE order_id = %s", (order_id,))
            else:
                 message = "⚠️ Cảnh báo: Không tìm thấy chặng lấy hàng (Có thể đã lấy rồi)."

        # --- CASE 2: WAREHOUSE_IN (Nhập kho) ---
        elif scan_data.action == ScanActionType.WAREHOUSE_IN:
            if not scan_data.warehouse_id:
                raise HTTPException(status_code=400, detail="Thiếu warehouse_id khi nhập kho")

            # Kết thúc chặng trước đó (Pickup hoặc Transfer) -> COMPLETED
            # Logic: Tìm chặng nào có Destination là kho này và đang IN_PROGRESS
            await cursor.execute("""
                UPDATE order_journey_legs 
                SET status = 'COMPLETED', completed_at = NOW()
                WHERE order_id = %s 
                  AND status = 'IN_PROGRESS' 
                  AND destination_warehouse_id = %s
            """, (order_id, scan_data.warehouse_id))
            
            if cursor.rowcount > 0:
                message = f"Đã nhập kho {scan_data.warehouse_id} thành công."
                # Cập nhật vị trí hiện tại của đơn hàng
                await cursor.execute("UPDATE orders SET status = 'AT_WAREHOUSE' WHERE order_id = %s", (order_id,))
            else:
                # Fallback: Nếu không tìm thấy chặng cụ thể, có thể do shipper bấm nhầm hoặc logic lỏng
                # Vẫn cho nhập kho nhưng cảnh báo
                message = f"Đã ghi nhận nhập kho (Không tìm thấy chặng vận chuyển tương ứng)."
                await cursor.execute("UPDATE orders SET status = 'AT_WAREHOUSE' WHERE order_id = %s", (order_id,))

        # --- CASE 3: WAREHOUSE_OUT (Xuất kho lên xe tải) ---
        elif scan_data.action == ScanActionType.WAREHOUSE_OUT:
            if not scan_data.warehouse_id:
                raise HTTPException(status_code=400, detail="Thiếu warehouse_id khi xuất kho")

            # Kích hoạt chặng tiếp theo (TRANSFER) có Origin là kho này -> IN_PROGRESS
            await cursor.execute("""
                UPDATE order_journey_legs 
                SET status = 'IN_PROGRESS', started_at = NOW()
                WHERE order_id = %s 
                  AND status = 'PENDING'
                  AND origin_warehouse_id = %s
                  AND leg_type = 'TRANSFER'
            """, (order_id, scan_data.warehouse_id))
            
            if cursor.rowcount > 0:
                message = "Đã xuất kho, bắt đầu trung chuyển."
                await cursor.execute("UPDATE orders SET status = 'IN_TRANSIT' WHERE order_id = %s", (order_id,))
            else:
                message = "Không tìm thấy chặng trung chuyển tiếp theo."

        # --- CASE 4: DELIVERY_START (Shipper nhận đơn đi giao) ---
        elif scan_data.action == ScanActionType.DELIVERY_START:
            if not shipper_id:
                raise HTTPException(status_code=400, detail="User không phải Shipper")

            # Tìm chặng DELIVERY (Leg cuối) đang PENDING và gán Shipper này vào
            # Đồng thời chuyển sang IN_PROGRESS
            await cursor.execute("""
                UPDATE order_journey_legs 
                SET status = 'IN_PROGRESS', 
                    started_at = NOW(), 
                    assigned_shipper_id = %s 
                WHERE order_id = %s AND leg_type = 'DELIVERY' AND status = 'PENDING'
            """, (shipper_id, order_id))

            if cursor.rowcount > 0:
                message = "Nhận đơn thành công. Bắt đầu đi giao."
                await cursor.execute("UPDATE orders SET status = 'DELIVERING' WHERE order_id = %s", (order_id,))
            else:
                message = "Không tìm thấy chặng giao hàng khả dụng (Hoặc đã có người nhận)."

        # --- CASE 5: DELIVERY_COMPLETE (Giao thành công) ---
        elif scan_data.action == ScanActionType.DELIVERY_COMPLETE:
             # Kết thúc chặng DELIVERY -> COMPLETED
             await cursor.execute("""
                UPDATE order_journey_legs 
                SET status = 'COMPLETED', completed_at = NOW()
                WHERE order_id = %s AND leg_type = 'DELIVERY' AND status = 'IN_PROGRESS'
            """, (order_id,))
             
             if cursor.rowcount > 0:
                 message = "Giao hàng thành công!"
                 # Update đơn hàng tổng thành COMPLETED
                 await cursor.execute("UPDATE orders SET status = 'COMPLETED' WHERE order_id = %s", (order_id,))
             else:
                 message = "Chưa nhận đơn hoặc đã hoàn thành trước đó."

       
        
        await db.commit()

    return BarcodeScanResponse(
        success=True,
        message=message,
        order_id=order["order_id"],
        order_code=order["order_code"],
        action=scan_data.action,
        current_warehouse=scan_data.warehouse_id,
        log_id=log_created_id
    )


@router.get("/order/{order_id}/history", response_model=List[OrderWarehouseLogOut])
async def get_order_tracking_history(
    order_id: str,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    **Lấy lịch sử di chuyển của đơn hàng qua các kho.**
    
    Trả về danh sách các điểm check-in/check-out theo thứ tự thời gian.
    
    **Params:**
    - order_id: ID đơn hàng
    
    **Returns:**
    - List of OrderWarehouseLogOut
    """
    try:
        history = await crud_order_warehouse_log.get_order_history(db, order_id)
        return history
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy lịch sử đơn hàng {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử đơn hàng"
        )


@router.get("/warehouse/{warehouse_id}/logs", response_model=List[OrderWarehouseLogOut])
async def get_warehouse_scan_logs(
    warehouse_id: str,
    limit: int = 50,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    **Lấy danh sách đơn hàng đã quét tại kho.**
    
    Dùng cho nhân viên kho xem lịch sử các đơn hàng đã xử lý.
    
    **Params:**
    - warehouse_id: ID kho
    - limit: Số lượng records (default 50)
    
    **Returns:**
    - List of OrderWarehouseLogOut
    """
    try:
        logs = await crud_order_warehouse_log.get_warehouse_logs(db, warehouse_id, limit)
        return logs
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy logs của kho {warehouse_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy logs của kho"
        )


@router.get("/{code_value}/image")
async def get_barcode_image(
    code_value: str,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    **Tạo hình ảnh barcode để in/hiển thị.**
    
    Trả về base64 image có thể dùng trong HTML/PDF.
    
    **Params:**
    - code_value: Mã barcode
    
    **Returns:**
    - Base64 encoded PNG image
    """
    try:
        # Verify barcode tồn tại
        exists = await BarcodeService.verify_barcode(db, code_value)
        
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barcode không tồn tại"
            )
        
        # Generate image
        image_base64 = BarcodeService.generate_barcode_image(code_value)
        
        return {
            "code_value": code_value,
            "image": image_base64
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi tạo hình ảnh barcode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo hình ảnh barcode"
        )
