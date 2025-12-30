from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import aiomysql
import logging
import random
import datetime
from app.api.v1.deps import get_db
import httpx

router = APIRouter(prefix="/tracking", tags=["public-tracking"])
logger = logging.getLogger(__name__)

# GIẢ LẬP REDIS (Lưu trong RAM khi chạy Dev)
# Cấu trúc: { "ORDER123_0901234567": { "code": "123456", "expires": timestamp } }
DEV_OTP_STORE = {} 
DISPATCH_SERVICE_URL = "http://ai_agent_service:8002/api/v1/dispatch"

class TrackingInitRequest(BaseModel):
    order_code: str = Field(..., min_length=5)
    phone_number: str = Field(..., min_length=9, max_length=15)

class TrackingVerifyRequest(TrackingInitRequest):
    otp: str = Field(..., min_length=6, max_length=6)

# Schema trả về thông tin đơn hàng (như cũ)
class PublicOrderInfo(BaseModel):
    order_code: str
    status: str
    receiver_name: str
    receiver_phone: str # Thêm cái này để hiển thị lại
    receiver_address: str
    weight: float       # <--- Thêm
    dimensions: str | None = None # <--- Thêm
    note: str | None = None       # <--- Thêm
    updated_at: str
    journey: list = []

@router.post("/request-otp")
async def request_tracking_otp(
    request: TrackingInitRequest,
    db: aiomysql.Connection = Depends(get_db)
):
    """Bước 1: Kiểm tra đơn hàng và gửi OTP (Dev: In ra console)"""
    async with db.cursor(aiomysql.DictCursor) as cursor:
        # Check xem đơn hàng có tồn tại với SĐT này không
        query = "SELECT order_id FROM orders WHERE order_code = %s AND receiver_phone = %s"
        await cursor.execute(query, (request.order_code, request.phone_number))
        order = await cursor.fetchone()
        
        if not order:
            # Fake delay một chút để chống brute-force user enumeration
            raise HTTPException(status_code=404, detail="Thông tin không chính xác")

        # Sinh OTP ngẫu nhiên
        otp_code = f"{random.randint(100000, 999999)}"
        
        # Lưu vào bộ nhớ tạm (Hết hạn sau 5 phút)
        key = f"{request.order_code}_{request.phone_number}"
        DEV_OTP_STORE[key] = {
            "code": otp_code,
            "expires": datetime.datetime.now() + datetime.timedelta(minutes=5)
        }

        # --- MÔI TRƯỜNG DEV ---
        print(f"\n========================================")
        print(f"🔑 OTP CHO ĐƠN {request.order_code}: {otp_code}")
        print(f"========================================\n")
        # ----------------------

        return {"message": "Mã xác thực đã được gửi (Check Console Server)"}

@router.post("/verify-track", response_model=PublicOrderInfo)
async def verify_tracking_otp(
    request: TrackingVerifyRequest,
    db: aiomysql.Connection = Depends(get_db)
):
    """Bước 2: Xác thực OTP và trả về dữ liệu"""
    
    # 1. Kiểm tra OTP
    key = f"{request.order_code}_{request.phone_number}"
    stored_data = DEV_OTP_STORE.get(key)

    if not stored_data:
        raise HTTPException(status_code=400, detail="Vui lòng yêu cầu gửi lại mã OTP")
    
    if datetime.datetime.now() > stored_data["expires"]:
        del DEV_OTP_STORE[key]
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")
        
    if stored_data["code"] != request.otp:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác")

    # Xóa OTP sau khi dùng xong (One-time use)
    del DEV_OTP_STORE[key]

   # --- 2. LẤY THÔNG TIN ORDER (DB LOCAL) ---
    async with db.cursor(aiomysql.DictCursor) as cursor:
        query = """
            SELECT 
                order_id, order_code, status, 
                receiver_name, receiver_phone, receiver_address, 
                weight, dimensions, note, updated_at
            FROM orders 
            WHERE order_code = %s AND receiver_phone = %s
        """
        await cursor.execute(query, (request.order_code, request.phone_number))
        order = await cursor.fetchone()
        
        if not order:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")
        
    # --- 3. GỌI API SANG DISPATCH SERVICE ĐỂ LẤY JOURNEY ---
    # Vì dữ liệu nằm ở service khác, ta phải request sang đó
    journey_logs = [] # Khởi tạo mặc định để tránh lỗi NameError
    
    try:
        # order['order_id'] là ID để query bên dispatch
        order_id = order['order_id'] 
        
        async with httpx.AsyncClient() as client:
            # Gọi endpoint: GET /dispatch/orders/{order_id}/legs
            # Timeout ngắn (vd 5s) để nếu service kia chết thì không treo tracking
            response = await client.get(
                f"{DISPATCH_SERVICE_URL}/orders/{order_id}/legs",
                timeout=5.0
            )
            
            if response.status_code == 200:
                journey_logs = response.json()
                logger.info(f"✅ Fetched {len(journey_logs)} legs from Dispatch Service")
            else:
                logger.warning(f"⚠️ Failed to fetch journey: {response.status_code}")
                
    except Exception as e:
        # Nếu Dispatch Service chết hoặc lỗi mạng, ta vẫn trả về thông tin đơn hàng
        # nhưng journey sẽ rỗng. Không được để crash app.
        logger.error(f"❌ Error calling Dispatch Service: {e}")
        journey_logs = []

    # --- 4. TRẢ VỀ KẾT QUẢ GỘP ---
    return {
        "order_code": order['order_code'],
        "status": order['status'],
        "receiver_name": order['receiver_name'],
        "receiver_phone": order['receiver_phone'],
        "receiver_address": order['receiver_address'],
        "weight": float(order['weight']) if order['weight'] else 0,
        "dimensions": order['dimensions'],
        "note": order['note'],
        "updated_at": str(order['updated_at']),
        "journey": journey_logs # <--- Biến này giờ đã được define chắc chắn
    }