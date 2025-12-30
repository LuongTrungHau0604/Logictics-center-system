# --- CRUD cho Warehouse ---
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Type, List, Dict, Any
from app import models, schemas
# Thiết lập logger
logger = logging.getLogger(__name__)
from app.crud.Base import CRUDBase
from sqlalchemy import select

class CRUDOrderJourneyLeg(CRUDBase[models.OrderJourneyLeg, Any, Any]):
    
    def create(self, db: Session, *, obj_in: dict) -> models.OrderJourneyLeg:
        """
        Tạo một OrderJourneyLeg mới.
        CHỈ thêm vào session, KHÔNG commit.
        Sử dụng flush + refresh để lấy ID ngay lập tức.
        """
        # Tạo instance từ dict data
        db_obj = models.OrderJourneyLeg(**obj_in)
        
        # Thêm vào session
        db.add(db_obj)
        
        # 🔥 MẤU CHỐT LÀ ĐÂY 🔥
        # flush() => Gửi lệnh SQL đến DB để tạo ID
        # refresh() => Tải lại đối tượng từ DB với ID mới
        # Transaction (giao dịch) vẫn MỞ, chưa commit.
        try:
            db.flush()
            db.refresh(db_obj)
            logger.info(f"Flushed new OrderJourneyLeg: {db_obj.leg_id} for order {obj_in.get('order_id')}")
            return db_obj
        except SQLAlchemyError as e:
            # get_db sẽ tự động rollback khi lỗi này bị ném ra
            logger.error(f"❌ Error flushing OrderJourneyLeg: {e}")
            raise e
    
    def get_by_order_id(self, db: Session, *, order_id: str) -> List[models.OrderJourneyLeg]:
        """
        Lấy tất cả các chặng của một đơn hàng.
        (Bỏ try/except, để get_db xử lý lỗi chung)
        """
        statement = (
            select(models.OrderJourneyLeg)
            .where(models.OrderJourneyLeg.order_id == order_id)
            .order_by(models.OrderJourneyLeg.sequence)
        )
        return db.scalars(statement).all()
    
    def update(self, db: Session, *, db_obj: models.OrderJourneyLeg, obj_in: dict) -> models.OrderJourneyLeg:
        """
        Cập nhật một OrderJourneyLeg.
        CHỈ cập nhật, KHÔNG commit.
        """
        # Update attributes từ dict
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Thêm lại vào session để đánh dấu là 'dirty' (đã thay đổi)
        db.add(db_obj)
        
        try:
            db.flush()
            db.refresh(db_obj)
            logger.info(f"Flushed update for OrderJourneyLeg: {db_obj.leg_id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"❌ Error flushing update for OrderJourneyLeg: {e}")
            raise e

    
crud_order_journey_leg = CRUDOrderJourneyLeg(models.OrderJourneyLeg)