# app/models/user.py

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "user"

    # Khóa chính của bảng này là 'user_id'
    user_id = Column(String(30), primary_key=True, index=True)
    
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    role = Column(String(50), nullable=False)
    status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Mối quan hệ logic ngược lại
    sme = relationship("SME", back_populates="user", uselist=False)