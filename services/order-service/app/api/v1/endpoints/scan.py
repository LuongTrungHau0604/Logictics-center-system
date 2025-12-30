# app/api/endpoints/scan.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_db, get_current_user # Giả định bạn có deps lấy DB và User
import aiomysql
from app.schemas.scan import ScanRequest
from app.schemas.user import UserOut # Schema user của bạn
from app.services.JourneyService import JourneyService # Import service bạn vừa viết

router = APIRouter()

@router.post("/scan", summary="Quét Barcode cập nhật hành trình")
async def scan_barcode_endpoint(
    payload: ScanRequest,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    API này dùng cho Shipper App hoặc Warehouse App.
    Khi quét, nó sẽ tự động tìm đơn hàng và cập nhật chặng (Leg) phù hợp.
    """
    
    # 1. Xác định role của người quét (Dựa vào thông tin user đăng nhập)
    # Giả sử trong UserOut hoặc DB user có trường 'role'
    # Bạn cần điều chỉnh logic này khớp với model User thực tế của bạn
    user_role = getattr(current_user, 'role', 'SHIPPER') # Mặc định là SHIPPER nếu không có field role
    user_id = current_user.user_id # Hoặc current_user.user_id
    
    # 2. Gọi Service xử lý
    try:
        result = await JourneyService.process_scan(
            db=db,
            code_value=payload.code_value,
            user_id=user_id,
            user_role=user_role,
            warehouse_id=payload.current_warehouse_id
        )
        return result
        
    except Exception as e:
        # Log lỗi ở đây nếu cần
        raise e