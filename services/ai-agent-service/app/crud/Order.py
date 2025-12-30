import logging
from typing import List, Type
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from typing import Optional
from app import models
from app.schemas import Order
from app.crud.Base import CRUDBase


logger = logging.getLogger(__name__)

class CRUDOrder(CRUDBase[models.Order, Order.OrderCreate, Order.OrderUpdate]):

    # 🔥 SỬA 1: ĐƠN GIẢN HÓA HÀM CREATE
    # (Bỏ logic flush/gán ngược active_leg_id và bỏ try/except)
    def create_order_with_legs(
        self, db: Session, *, obj_in: Order.OrderCreate
    ) -> models.Order:
        """
        Phiên bản ĐƠN GIẢN HÓA sau khi bỏ active_leg_id.
        Không còn cần logic db.flush() phức tạp.
        Lỗi (exceptions) sẽ được ném ra để get_db xử lý rollback.
        """
        logger.info("Creating order with legs (simplified logic)...")
        
        # 1. Tạo Legs
        # (Giả định Pydantic schema obj_in.legs đã chứa
        #  các trường mới như origin_sme_id, destination_is_receiver)
        db_legs = [
            models.OrderJourneyLeg(**leg.model_dump())
            for leg in obj_in.legs
        ]
        
        # 2. Tạo Order
        # (Không còn trường active_leg_id)
        db_order = models.Order(
            **obj_in.model_dump(exclude={"legs"}),
            all_legs=db_legs 
        )
        
        # 3. Add (SQLAlchemy's cascade sẽ add cả legs)
        db.add(db_order)
        
        # 4. Flush và Refresh để đảm bảo object trả về có ID
        # (Điều này là tùy chọn, nhưng hữu ích nếu endpoint
        #  cần trả về ID ngay lập tức)
        db.flush()
        db.refresh(db_order)
        
        logger.info(f"Order {db_order.order_id} created and refreshed (no active_leg).")
        return db_order


    # 🔥 SỬA 2: BỎ TRY/EXCEPT ĐỂ NÉM LỖI RA NGOÀI
    def get_pending_orders_by_area(
        self, 
        db: Session, 
        area_id: str, 
        limit: int = 50
    ) -> List[models.Order]:
        """
        Fetches PENDING orders and JOINS with SME to get pickup coordinates.
        """
        logger.info(f"Finding pending orders within area_id: {area_id}")
        
        statement = (
            select(models.Order)
            # 🔥 CRITICAL: Load SME data so we can get Latitude/Longitude later
            .options(joinedload(models.Order.sme)) 
            .where(
                models.Order.status == models.OrderStatus.PENDING,
                models.Order.area_id == area_id,
                models.Order.area_id.isnot(None),
                models.Order.area_id != '',
                models.Order.receiver_latitude.isnot(None),
                models.Order.receiver_longitude.isnot(None)
            )
            .limit(limit)
        )
        
        orders_in_area = db.scalars(statement).all()
        
        logger.info(f"✅ Found {len(orders_in_area)} PENDING orders in area '{area_id}'")
        return orders_in_area

    def get(self, db: Session, id: str) -> Optional[models.Order]:
        """
        Ghi đè hàm 'get' để sử dụng 'order_id' thay vì 'id'.
        """
        # (Giả sử khóa chính của bạn là 'order_id')
        statement = select(self.model).where(self.model.order_id == id)
        return db.scalars(statement).first()

# Khởi tạo CRUD
crud_order = CRUDOrder(models.Order)