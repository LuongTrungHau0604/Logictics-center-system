# app/models/sme.py

from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import column_property
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
class SME(Base):
    __tablename__ = "sme"

    sme_id = Column(String(50), primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    tax_code = Column(String(50), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=True)
    
    # --- THÊM MỚI ---
    # Thêm cột coordinates. Dùng Text để lưu WKT Point "POINT(lng lat)"
    # hoặc "lat,lng" cho linh hoạt.
    coordinates = Column(Text, nullable=True)
    
    contact_phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # --- THAY ĐỔI STATUS ---
    # Đổi từ String(50) sang Enum để khớp với DB
    # và đổi default "PENDING_APPROVAL" -> "PENDING"
    status = Column(
        Enum('ACTIVE', 'INACTIVE', 'PENDING', name='sme_status_enum'), 
        default="PENDING", 
        nullable=False
    ) 
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Mối quan hệ 1-Nhiều (1 SME có nhiều Users) ---
    # "users" (số nhiều) là một thuộc tính "virtual" (ảo) của Python.
    # Nó cho phép bạn truy cập sme_instance.users để lấy
    # danh sách TẤT CẢ các user thuộc SME này.
    #
    # 'back_populates="sme"' nói rằng: "Ở phía bên kia (model User),
    # hãy tìm thuộc tính có tên 'sme' để hoàn thiện mối quan hệ 2 chiều."
    users = relationship("User", back_populates="sme", lazy="dynamic")
    
    # --- ĐÃ XÓA ---
    # user_id = Column(String(30), ForeignKey("user.user_id"), ...)
    # Lý do: Khóa ngoại phải nằm ở bảng "user" (phía "Nhiều")
    # để cho phép nhiều user cùng thuộc 1 SME.