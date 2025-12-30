# sme-service/app/crud/crud_sme.py

from sqlalchemy.orm import Session
from typing import Optional
from .base import CRUDBase
from app.models import SME
from app.schemas.sme import SMERegisterProfile # Đổi schema cho phù hợp
from typing import Any, Dict, Optional, TypeVar, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.base import Base
from app.models import User


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDSME(CRUDBase[SME, SMERegisterProfile, SMERegisterProfile]):
    def get_by_user_id(self, db: Session, *, user_id: str) -> Optional[SME]:
        """
        Tìm hồ sơ SME bằng user_id.
        """
        return db.query(self.model).filter(self.model.user_id == user_id).first()
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Tạo một đối tượng mới từ Pydantic schema."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # --- HÀM MỚI BẠN CẦN THÊM VÀO ĐÂY ---
    def create_with_data(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """
        Tạo một đối tượng mới từ một dictionary.
        Rất hữu ích khi bạn đã chuẩn bị sẵn dữ liệu.
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_multi_with_user_info(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[SME]:
        """
        Lấy danh sách các SME, join với bảng User để lấy thông tin liên quan.
        Hàm này được dùng cho chức năng "Xem danh sách doanh nghiệp" của Admin.
        """
        return (
            db.query(self.model)
            # Nối (JOIN) với bảng User dựa trên điều kiện khóa ngoại
            .join(User, self.model.user_id == User.user_id) 
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    def get_by_sme_id(self, db: Session, *, sme_id: str) -> Optional[SME]:
        """
        Tìm hồ sơ SME bằng sme_id (khóa chính).
        """
        return db.query(self.model).filter(self.model.sme_id == sme_id).first()
crud_sme = CRUDSME(SME)