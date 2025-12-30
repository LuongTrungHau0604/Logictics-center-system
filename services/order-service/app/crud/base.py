# app/crud/base.py
# CRUD base class - Generic CRUD operations for SQLAlchemy models

from typing import Any, Dict, Generic, TypeVar, Type, Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.base import Base

# Type variables
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD base class with default methods to Create, Read, Update, Delete (CRUD).
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get object by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple objects with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create new object."""
        create_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update an existing object."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Update only provided fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> ModelType:
        """Delete object by ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
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
        Tạo một đối tượng mới từ một dictionary đã được chuẩn bị sẵn.
        Rất hữu ích khi bạn cần thêm các trường tự sinh (như order_id)
        vào dữ liệu từ request body trước khi lưu.
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj