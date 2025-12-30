import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from sqlalchemy.orm import Session
# from datetime import datetime  <-- Không cần nữa vì không lưu log time

# Import DB and Models to fetch all Areas automatically
from app.db.session import get_db 
from app import models 
from app.services.IntelligentLogisticsAI import IntelligentLogisticsAI 

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai", 
    tags=["ai-optimizer"]
)

_ai_instance = None

def get_ai_service():
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = IntelligentLogisticsAI()
    return _ai_instance

# --- Models ---
class AutoOptimizeRequest(BaseModel):
    target_id: Optional[str] = Field(
        None, 
        description="Specific ID (Area/Hub). If empty, runs FULL SYSTEM optimization."
    )
    
    
class IncidentRequest(BaseModel):
    shipper_id: str
    message: str
    latitude: float
    longitude: float

class OptimizationReport(BaseModel):
    status: str
    summary: str
    processed_count: int
    details: List[dict] = []

# --- ⚡ SINGLE ENDPOINT FOR ALL ACTIONS ---
@router.post(
    "/optimize", 
    response_model=OptimizationReport, 
    status_code=status.HTTP_200_OK
)
async def run_optimization(
    request: AutoOptimizeRequest,
    db: Session = Depends(get_db), 
    ai_service: IntelligentLogisticsAI = Depends(get_ai_service)
):
    """
    Master Endpoint:
    - Runs the AI Agent to assign orders and trucks.
    - Updates OrderJourneyLegs and Shipper Status directly in DB via AI Tools.
    - Returns a JSON summary for the Frontend (does NOT save text logs to DB).
    """

    # 🟢 TRƯỜNG HỢP 1: Chạy cụ thể cho 1 Target (Testing/Manual)
    if request.target_id:
        logger.info(f"🤖 AGENT: Targeted Run -> {request.target_id}")
        
        # Gọi Agent: Các hàm Tool bên trong sẽ tự động update DB (Order/Shipper)
        result = await ai_service.run_logistics_optimization(target_id=request.target_id)
        
        return OptimizationReport(
            status=result.get("status"),
            summary=result.get("agent_report", ""),
            processed_count=1,
            details=[result]
        )

    # 🔵 TRƯỜNG HỢP 2: Chạy Tự Động Toàn Hệ Thống (Auto-Pilot)
    else:
        logger.info("🤖 AGENT: Full System Auto-Pilot Initiated...")
        
        # 1. Lấy danh sách Area để quét
        active_areas = db.query(models.Area).all()
        
        if not active_areas:
            return OptimizationReport(
                status="SKIPPED",
                summary="No active areas found in database.",
                processed_count=0
            )

        reports = []
        success_count = 0

        # 2. Vòng lặp chạy Agent cho từng Area
        for area in active_areas:
            area_id = area.area_id
            logger.info(f"   >>> Scanning Area: {area_id}...")
            
            try:
                # Gọi Agent -> Agent tự gọi Tool -> Tool tự Update DB
                step_result = await ai_service.run_logistics_optimization(target_id=area_id)
                
                # Chỉ lưu kết quả vào list để trả về cho Frontend xem ngay lúc đó
                reports.append({
                    "target": area_id,
                    "status": step_result.get("status"),
                    "report_snippet": step_result.get("agent_report", "")[:200] + "..."
                })
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error optimizing {area_id}: {e}")
                reports.append({"target": area_id, "status": "ERROR", "error": str(e)})

        # 3. Trả về kết quả tổng hợp cho Frontend
        return OptimizationReport(
            status="COMPLETED",
            summary=f"Auto-pilot finished. Scanned {len(active_areas)} areas.",
            processed_count=success_count,
            details=reports
        )
        
@router.post(
    "/report-incident",
    response_model=OptimizationReport, # 👈 Trả về đúng format chuẩn
    status_code=status.HTTP_200_OK
)
async def report_incident(
    request: IncidentRequest,
    db: Session = Depends(get_db), # Có thể cần dùng DB sau này
    ai_service: IntelligentLogisticsAI = Depends(get_ai_service) # 👈 Dependency Injection chuẩn
):
    """
    API này nhận tin nhắn từ App Shipper -> Kích hoạt AI Agent xử lý sự cố.
    """
    try:
        # Gọi Agent với mode xử lý sự cố (truyền message + context)
        result = await ai_service.run_logistics_optimization(
            user_message=request.message,
            context_data={
                "shipper_id": request.shipper_id,
                "lat": request.latitude,
                "lon": request.longitude
            }
        )
        
        # Mapping kết quả trả về đúng format OptimizationReport
        return OptimizationReport(
            status=result.get("status", "UNKNOWN"),
            summary=result.get("agent_report", "No report generated"),
            processed_count=1, # Xử lý 1 sự cố
            details=[result]   # Chi tiết full
        )
        
    except Exception as e:
        # Log lỗi nếu cần thiết
        # logger.error(f"Incident Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))