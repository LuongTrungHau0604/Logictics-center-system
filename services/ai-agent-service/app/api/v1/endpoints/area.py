from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import Area as AreaSchema
from app.services.areaService import AreaService

router = APIRouter(tags=["Area Management"])

@router.get("/", response_model=List[AreaSchema.Area])
def read_areas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả khu vực.
    """
    return AreaService.get_all_areas(db, skip=skip, limit=limit)

@router.post("/", response_model=AreaSchema.Area, status_code=status.HTTP_201_CREATED)
def create_area(
    area_in: AreaSchema.AreaCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo mới một khu vực.
    """
    return AreaService.create_area(db, area_in)

@router.get("/{area_id}", response_model=AreaSchema.Area)
def read_area(
    area_id: str,
    db: Session = Depends(get_db)
):
    """
    Xem chi tiết khu vực.
    """
    return AreaService.get_area_by_id(db, area_id)

@router.put("/{area_id}", response_model=AreaSchema.Area)
def update_area(
    area_id: str,
    area_in: AreaSchema.AreaUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin khu vực.
    """
    return AreaService.update_area(db, area_id, area_in)

@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(
    area_id: str,
    db: Session = Depends(get_db)
):
    """
    Xóa khu vực.
    """
    AreaService.delete_area(db, area_id)
    
