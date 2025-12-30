# app/models/sme.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class SME(Base):
    __tablename__ = "sme"

    sme_id = Column(String(50), primary_key=True, index=True)
    business_name = Column(String(255), nullable=True)
    tax_code = Column(String(50), unique=True, nullable=True)
    address = Column(Text, nullable=True)
    contact_phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    status = Column(String(50), default="PENDING_APPROVAL")
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- DÂY NỐI QUAN TRỌNG NHẤT ---
    # Cột 'user_id' trong bảng 'sme' này là khóa ngoại,
    # tham chiếu đến cột 'user_id' của bảng 'user'.
    user_id = Column(String(30), ForeignKey("user.user_id"), unique=True, nullable=False)
    
    # Mối quan hệ logic
    user = relationship("User", back_populates="sme")