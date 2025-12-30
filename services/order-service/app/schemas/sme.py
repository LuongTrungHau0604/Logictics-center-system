# app/schemas/sme.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- SCHEMA MỚI CHO BODY REQUEST ---
# Nó khớp với các cột business_name, tax_code, ... trong bảng của bạn
class SMERegisterProfile(BaseModel):
    business_name: str
    tax_code: str
    address: Optional[str] = None
    contact_phone: str
    email: EmailStr

# Schema cho dữ liệu trả về (response)
class SMEOut(BaseModel):
    sme_id: str
    user_id: str
    business_name: Optional[str] = None
    tax_code: Optional[str] = None
    status: str
    created_at: datetime
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True