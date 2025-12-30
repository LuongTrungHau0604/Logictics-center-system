import logging
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import aiomysql
from app import models
from app.crud.Base import CRUDBase
from app.schemas import Shipper as ShipperSchema

# Thiết lập logger
logger = logging.getLogger(__name__)

class CRUDShipper(CRUDBase):
    def create(self, db: Session, *, obj_in: ShipperSchema.ShipperCreate) -> models.Shipper:
        """
        Tạo Shipper mới.
        """
        try:
            # Chuyển đổi dữ liệu đầu vào thành dict
            obj_in_data = obj_in.model_dump()
            
            # Tạo đối tượng model
            db_obj = models.Shipper(**obj_in_data)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating Shipper: {e}")
            raise

    def get(self, db: Session, id: str) -> Optional[models.Shipper]:
        """
        Lấy thông tin Shipper theo shipper_id.
        """
        try:
            statement = select(self.model).where(self.model.shipper_id == id)
            return db.scalars(statement).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting Shipper by ID {id}: {e}")
            return None

    def get_available_shippers_by_area(
        self, 
        db: Session, 
        area_id: str, 
        vehicle_type: models.VehicleType = models.VehicleType.MOTORBIKE, 
        limit: int = 50
    ) -> List[models.Shipper]:
        """
        Tìm Shipper đang ONLINE trong khu vực.
        Hàm này hỗ trợ Agent tìm Shipper để gán đơn.
        """
        logger.info(f"Finding available {vehicle_type} in area: {area_id}")
        try:
            statement = (
                select(models.Shipper)
                .where(
                    models.Shipper.status == models.ShipperStatus.ONLINE,
                    models.Shipper.area_id == area_id,
                    models.Shipper.vehicle_type == vehicle_type
                )
                # Eager load Employee (lấy tên) và Area (fallback vị trí)
                .options(
                    joinedload(models.Shipper.employee),
                    joinedload(models.Shipper.area) 
                )
                .limit(limit)
            )
            
            results = db.scalars(statement).all()
            return results

        except SQLAlchemyError as e:
            logger.error(f"Error finding shippers: {e}")
            return []
        
    @staticmethod
    async def get_profile_by_user_id(db: aiomysql.Connection, user_id: str) -> Optional[dict]:
        """
        Lấy profile đầy đủ của Shipper bằng cách JOIN bảng employees và shippers.
        Cập nhật: Lấy thêm tọa độ thực tế và token để phục vụ App.
        """
        async with db.cursor(aiomysql.DictCursor) as cursor:
            sql = """
                SELECT 
                    e.employee_id,      -- [QUAN TRỌNG] Phải có để khớp với Schema
                    e.full_name, 
                    e.email, 
                    e.phone, 
                    e.warehouse_id,
                    s.shipper_id, 
                    s.vehicle_type, 
                    s.status, 
                    s.rating, 
                    s.area_id,
                    s.fcm_token,            -- [MỚI] Token thông báo
                    s.current_latitude,     -- [MỚI] Vĩ độ
                    s.current_longitude,    -- [MỚI] Kinh độ
                    s.last_location_update  -- [MỚI] Thời gian cập nhật cuối
                FROM employees e
                INNER JOIN shippers s ON e.employee_id = s.employee_id
                WHERE e.user_id = %s
            """
            await cursor.execute(sql, (user_id,))
            result = await cursor.fetchone()
            
            if result:
                # Giả lập dữ liệu thống kê (hoặc query COUNT từ bảng orders nếu cần)
                result['total_deliveries'] = 156 
                result['success_rate'] = 98.5
                
            return result

    @staticmethod
    async def update(db: aiomysql.Connection, shipper_id: str, obj_in):
        """
        Hàm update linh hoạt dùng cho ShipperService (Async).
        """
        try:
            # 1. Chuẩn hóa dữ liệu về dạng Dict
            if isinstance(obj_in, dict):
                update_data = obj_in
            elif hasattr(obj_in, 'model_dump'):
                update_data = obj_in.model_dump(exclude_unset=True)
            elif hasattr(obj_in, 'dict'):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                raise ValueError("Dữ liệu update không hợp lệ")

            # 2. Xây dựng câu SQL động
            fields = []
            values = []
            for k, v in update_data.items():
                fields.append(f"{k} = %s")
                values.append(v)
            
            if not fields:
                return None
                
            values.append(shipper_id)
            
            sql = f"UPDATE shippers SET {', '.join(fields)} WHERE shipper_id = %s"
            
            async with db.cursor() as cursor:
                await cursor.execute(sql, tuple(values))
                return True

        except Exception as e:
            logger.error(f"❌ Error updating shipper {shipper_id}: {e}")
            raise e

# Khởi tạo instance
crud_shipper = CRUDShipper(models.Shipper)