# app/crud/Base.py

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# (Giả sử bạn có file này để định nghĩa Base của SQLAlchemy)
from app.db.base_class import Base 

logger = logging.getLogger(__name__)

# 1. ĐỊNH NGHĨA CÁC TYPEVAR (BIẾN KIỂU DỮ LIỆU)
# Đây là các "khuôn" cho models.Order, schemas.OrderCreate, v.v.
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# 2. THAY ĐỔI QUAN TRỌNG NHẤT
# Kế thừa từ Generic và truyền các TypeVar vào
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    
    def __init__(self, model: Type[ModelType]):
        """
        Khởi tạo CRUDBase với một model SQLAlchemy.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Lấy một đối tượng bằng ID.
        """
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            raise

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Lấy nhiều đối tượng với phân trang.
        """
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Tạo đối tượng mới (sử dụng flush + refresh).
        """
        try:
            # Chuyển Pydantic schema thành dict
            obj_in_data = obj_in.model_dump()
            
            # Tạo đối tượng model SQLAlchemy
            db_obj = self.model(**obj_in_data)  
            
            db.add(db_obj)
            db.flush() # Gửi lệnh SQL để lấy ID
            db.refresh(db_obj) # Tải lại đối tượng với ID mới
            
            logger.info(f"Flushed new {self.model.__name__}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise # Ném lỗi ra để get_db rollback

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Cập nhật đối tượng (sử dụng flush + refresh).
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True) # Chỉ update các trường được gửi
            
            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])
                    
            db.add(db_obj)
            db.flush()
            db.refresh(db_obj)
            
            logger.info(f"Flushed update for {self.model.__name__}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise # Ném lỗi ra để get_db rollback

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Xóa đối tượng bằng ID.
        """
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.flush() # Xóa ngay lập tức (nhưng chưa commit)
                logger.info(f"Flushed removal for {self.model.__name__} id {id}")
            return obj
        except SQLAlchemyError as e:
            logger.error(f"Error removing {self.model.__name__} id {id}: {e}")
            raise # Ném lỗi ra để get_db rollback