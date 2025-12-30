# app/models/barcode.py

from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db.base import Base

class Barcode(Base):
    __tablename__ = "barcode"

    barcode_id = Column(String(50), primary_key=True, index=True)
    code_value = Column(String(255), unique=True, nullable=False, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow)