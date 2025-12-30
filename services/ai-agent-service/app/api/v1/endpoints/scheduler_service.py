# app/services/scheduler_tasks.py (hoặc để chung trong file hiện tại nhưng tách hàm ra)
import logging
from app.db.session import SessionLocal
from app import models
from app.services.IntelligentLogisticsAI import IntelligentLogisticsAI

logger = logging.getLogger(__name__)

# Khởi tạo 1 instance AI dùng chung
ai_service = IntelligentLogisticsAI()

async def run_system_wide_optimization():
    """
    Hàm này sẽ được Scheduler gọi định kỳ.
    Nó KHÔNG phụ thuộc vào HTTP Request hay Depends của FastAPI.
    """
    logger.info("⏰ SCHEDULER: Starting periodical system optimization...")
    
    # ⚠️ Quan trọng: Trong Background Task, phải tự tạo DB Session thủ công
    # vì không có Dependency Injection của FastAPI ở đây.
    db = SessionLocal()
    
    try:
        # 1. Lấy tất cả Area
        active_areas = db.query(models.Area).all()
        if not active_areas:
            logger.warning("⏰ SCHEDULER: No active areas found.")
            return

        # 2. Chạy vòng lặp tối ưu
        for area in active_areas:
            try:
                # Gọi AI Agent
                await ai_service.run_logistics_optimization(target_id=area.area_id)
            except Exception as e:
                logger.error(f"❌ SCHEDULER ERROR [Area {area.area_id}]: {e}")
                
        logger.info(f"✅ SCHEDULER: Finished scanning {len(active_areas)} areas.")
        
    except Exception as e:
        logger.error(f"❌ SCHEDULER CRITICAL FAILURE: {e}")
    finally:
        # ⚠️ Rất quan trọng: Phải đóng session sau khi dùng xong
        db.close()