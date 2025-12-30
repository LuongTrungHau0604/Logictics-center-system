from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from app.db.session import get_db
from app.services.LogisticsAgentService import LogisticsAgentService, process_logistics_route
from app import models

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response schemas
class RouteRequest(BaseModel):
    business_address: str = Field(..., min_length=1, description="Địa chỉ doanh nghiệp")
    receiver_address: str = Field(..., min_length=1, description="Địa chỉ người nhận")
    required_capacity: int = Field(..., gt=0, description="Sức chứa yêu cầu")

class RouteResponse(BaseModel):
    status: str
    message: str
    business_coords: dict = None
    receiver_coords: dict = None
    warehouse: dict = None
    pickup_distance_km: float = None
    delivery_distance_km: float = None
    total_distance_km: float = None
    route_summary: dict = None


@router.post(
    "/orders/{order_id}/calculate-route", 
    response_model=RouteResponse,
    summary="Nút bấm: Tự động tính route cho 1 Order ID"
)
async def calculate_route_for_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint này hoạt động như một 'nút bấm'. 
    Nó lấy `order_id`, tự động tra cứu địa chỉ Doanh nghiệp (SME) 
    và địa chỉ Người nhận (Receiver) từ CSDL, sau đó
    chạy logic tính toán của `process_logistics_route`.
    """
    logger.info(f"Received auto-route request for Order ID: {order_id}")

    # 1. Lấy Order và thông tin SME liên quan
    order = db.get(models.Order, order_id)
    
    if not order:
        logger.error(f"Order {order_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    # 2. Lấy địa chỉ Doanh nghiệp (từ SME của Order)
    if not order.sme or not order.sme.address:
        logger.error(f"Order {order_id} has no SME or SME address.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Order is not associated with a valid business (SME) address"
        )
    business_address = order.sme.address
    
    # 3. Lấy địa chỉ Người nhận (từ Order)
    if not order.receiver_address:
        logger.error(f"Order {order_id} has no receiver address.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Order has no receiver address"
        )
    receiver_address = order.receiver_address
    
    # 4. Xác định sức chứa (Default là 1 cho 1 đơn hàng)
    # (Nếu bạn muốn dùng trọng lượng, hãy dùng: int(order.weight) or 1)
    required_capacity = 1 
    
    logger.info(f"Auto-fetching data for Order {order_id}:")
    logger.info(f"  -> Business: {business_address}")
    logger.info(f"  -> Receiver: {receiver_address}")
    logger.info(f"  -> Capacity: {required_capacity}")

    # 5. Gọi service (giống như endpoint cũ của bạn)
    try:
        result = await process_logistics_route(
            db=db,
            business_address=business_address,
            receiver_address=receiver_address,
            required_capacity=required_capacity
        )
        
        logger.info(f"Auto-route calculation completed: Status={result['status']}")
        
        # Kiểm tra nếu Geocoding hoặc tìm kho thất bại
        if result.get("status") != "SUCCESS":
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=result.get("message", "Failed to calculate route")
            )

        return RouteResponse(**result)
        
    except Exception as e:
        # Bắt lỗi từ HTTPException ở trên hoặc lỗi 500
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error in auto-route endpoint for {order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi tính toán tuyến đường: {str(e)}"
        )
@router.post("/calculate-route", response_model=RouteResponse)
async def calculate_route(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint tính toán tuyến đường logistics tối ưu.
    
    Args:
        request: RouteRequest chứa thông tin địa chỉ và capacity
        db: Database session
        
    Returns:
        RouteResponse: Kết quả tính toán tuyến đường
    """
    try:
        logger.info(f"Received route calculation request: {request.business_address} -> {request.receiver_address}")
        
        # Sử dụng utility function để xử lý
        result = await process_logistics_route(
            db=db,
            business_address=request.business_address,
            receiver_address=request.receiver_address,
            required_capacity=request.required_capacity
        )
        
        logger.info(f"Route calculation completed: Status={result['status']}")
        
        return RouteResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in calculate_route endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi tính toán tuyến đường: {str(e)}"
        )

# Alternative endpoint nếu bạn muốn dùng trực tiếp LogisticsAgentService
@router.post("/calculate-route-v2", response_model=RouteResponse)
async def calculate_route_v2(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint tính toán tuyến đường sử dụng trực tiếp LogisticsAgentService.
    """
    try:
        logger.info(f"Received route calculation request v2: {request.business_address} -> {request.receiver_address}")
        
        # Sử dụng trực tiếp LogisticsAgentService
        async with LogisticsAgent() as agent:
            result = await agent.process_route_request(
                db=db,
                business_address=request.business_address,
                receiver_address=request.receiver_address,
                required_capacity=request.required_capacity
            )
        
        logger.info(f"Route calculation v2 completed: Status={result['status']}")
        
        return RouteResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in calculate_route_v2 endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server khi tính toán tuyến đường: {str(e)}"
        )

@router.get("/test")
async def test_logistics_agent(db: Session = Depends(get_db)):
    """Test endpoint cho LogisticsAgentService"""
    try:
        test_result = await process_logistics_route(
            db=db,
            business_address="469 Đ. Nguyễn Hữu Thọ, Tân Hưng, Quận 7, Thành phố Hồ Chí Minh, Việt Nam",
            receiver_address="504 Huỳnh Tấn Phát, Bình Thuận, Quận 7, Thành phố Hồ Chí Minh 008428, Việt Nam",
            required_capacity=10
        )
        
        return {
            "status": "success",
            "message": "LogisticsAgentService working correctly",
            "test_result": test_result
        }
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return {
            "status": "error",
            "message": f"LogisticsAgentService test failed: {str(e)}"
        }