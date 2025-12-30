# app/crud/crud_sme.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models
from app.schemas import schemas


def create_sme(db: Session, sme: schemas.SMECreate) -> models.SME:
    """
    Tạo SME mới
    """
    db_sme = models.SME(
        sme_id=sme.sme_id,
        business_name=sme.business_name,
        tax_code=sme.tax_code,
        contact_phone=sme.contact_phone,
        email=sme.email,
        address=sme.address,
        latitude=sme.latitude,
        longitude=sme.longitude,
        user_id=sme.user_id,
        status=sme.status
    )
    db.add(db_sme)
    db.commit()
    db.refresh(db_sme)
    return db_sme


def get_sme(db: Session, sme_id: str) -> Optional[models.SME]:
    """
    Lấy 1 SME theo ID
    """
    return db.query(models.SME).filter(models.SME.sme_id == sme_id).first()


def get_sme_by_user(db: Session, user_id: str) -> List[models.SME]:
    """
    Lấy danh sách SME theo user_id
    """
    return db.query(models.SME).filter(models.SME.user_id == user_id).all()


def update_sme_coordinates(db: Session, sme: models.SME, data: schemas.SMEUpdateCoordinates) -> models.SME:
    """
    Quan trọng: Cập nhật kinh độ/vĩ độ cho SME sau khi đã geocode
    """
    if data.latitude is not None:
        sme.latitude = data.latitude
    if data.longitude is not None:
        sme.longitude = data.longitude
    
    db.commit()
    db.refresh(sme)
    return sme


def update_sme(db: Session, sme: models.SME, data: schemas.SMEUpdate) -> models.SME:
    """
    Cập nhật thông tin SME
    """
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sme, field, value)
    
    db.commit()
    db.refresh(sme)
    return sme


def get_smes_without_coordinates(db: Session) -> List[models.SME]:
    """
    Lấy danh sách SME chưa có tọa độ (cần geocode)
    """
    return db.query(models.SME).filter(
        models.SME.latitude.is_(None),
        models.SME.longitude.is_(None),
        models.SME.status == "active"
    ).all()


def get_active_smes(db: Session, skip: int = 0, limit: int = 100) -> List[models.SME]:
    """
    Lấy danh sách SME đang hoạt động
    """
    return db.query(models.SME).filter(
        models.SME.status == "active"
    ).offset(skip).limit(limit).all()


def delete_sme(db: Session, sme_id: str) -> bool:
    """
    Xóa SME (soft delete - chuyển status thành inactive)
    """
    sme = get_sme(db, sme_id)
    if sme:
        sme.status = "inactive"
        db.commit()
        return True
    return False