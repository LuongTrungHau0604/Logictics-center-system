from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status
from app.crud.Area import area as crud_area
from app.schemas import Area as AreaSchema
from app import models

class AreaService:
    @staticmethod
    def get_all_areas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Area]:
        return crud_area.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    def get_area_by_id(db: Session, area_id: str) -> models.Area:
        area = crud_area.get(db, area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Area not found with id {area_id}"
            )
        return area

    @staticmethod
    def create_area(db: Session, area_in: AreaSchema.AreaCreate) -> models.Area:
        # Logic validate thêm nếu cần (VD: check trùng tên)
        return crud_area.create(db, obj_in=area_in)

    @staticmethod
    def update_area(
        db: Session, area_id: str, area_in: AreaSchema.AreaUpdate
    ) -> models.Area:
        area = crud_area.get(db, area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Area not found"
            )
        return crud_area.update(db, db_obj=area, obj_in=area_in)

    @staticmethod
    def delete_area(db: Session, area_id: str):
        area = crud_area.get(db, area_id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Area not found"
            )
        return crud_area.remove(db, area_id=area_id)