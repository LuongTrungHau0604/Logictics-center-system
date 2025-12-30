from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from app import models
from app.schemas import Area as AreaSchema

class CRUDArea:
    def get(self, db: Session, area_id: str) -> Optional[models.Area]:
        return db.query(models.Area).filter(models.Area.area_id == area_id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Area]:
        return db.query(models.Area).order_by(models.Area.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: AreaSchema.AreaCreate) -> models.Area:
        # Tạo dict từ Pydantic model
        db_obj = models.Area(
            area_id=f"AREA-{uuid.uuid4().hex[:8].upper()}",
            name=obj_in.name,
            type=obj_in.type,
            status=obj_in.status,
            description=obj_in.description,
            radius_km=obj_in.radius_km,
            center_latitude=obj_in.center_latitude,
            center_longitude=obj_in.center_longitude,
            created_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: models.Area, obj_in: AreaSchema.AreaUpdate
    ) -> models.Area:
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # Cập nhật thời gian update
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, area_id: str) -> models.Area:
        obj = db.query(models.Area).get(area_id)
        db.delete(obj)
        db.commit()
        return obj

area = CRUDArea()