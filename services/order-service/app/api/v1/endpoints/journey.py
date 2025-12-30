from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import aiomysql
import logging

from app.api.v1.deps import get_db, get_current_user
from app.schemas.user import UserOut
from app.services.JourneyService import JourneyService

router = APIRouter(prefix="/journey", tags=["Journey"])
logger = logging.getLogger(__name__)

# Schema cho dữ liệu gửi lên
class JourneyScanRequest(BaseModel):
    code_value: str

@router.post("/scan")
async def scan_package_journey(
    scan_data: JourneyScanRequest,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Endpoint xử lý quét mã hành trình (Universal Scan Endpoint).
    Hỗ trợ 2 Roles:
    1. SHIPPER: Quét để xác nhận lấy hàng (PICKUP -> IN_TRANSIT) hoặc giao hàng.
    2. WAREHOUSE_STAFF: Quét để xác nhận hàng đã về kho (IN_TRANSIT -> ARRIVED_AT_WAREHOUSE).
    
    Logic rẽ nhánh nằm trong JourneyService.process_scan dựa trên `current_user.role`.
    """
    logger.info(f"📲 User {current_user.username} ({current_user.role}) quét mã: {scan_data.code_value}")

    # Kiểm tra quyền: Chỉ cho phép Shipper và Warehouse Staff
    allowed_roles = ["SHIPPER", "WAREHOUSE_STAFF"]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {current_user.role} không có quyền thực hiện quét mã hành trình."
        )

    try:
        # Gọi Service để xử lý logic dựa trên Role
        result = await JourneyService.process_scan(
            db=db,
            code_value=scan_data.code_value,
            user_id=current_user.user_id,
            user_role=current_user.role, 
            # Truyền thêm username để log hoặc tạo thông báo nếu cần
        )
        return result

    except HTTPException as e:
        # Re-raise lỗi HTTP đã định nghĩa trong Service (vd: 404 không tìm thấy đơn, 400 sai trạng thái)
        raise e
    except Exception as e:
        logger.error(f"Lỗi hệ thống khi xử lý quét hành trình: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống khi xử lý quét mã"
        )