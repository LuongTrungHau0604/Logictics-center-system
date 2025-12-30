# app/schemas/sme.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Import schema UserOut để lồng (nest) vào SMEOut
try:
    from .user import UserOut
except ImportError:
    from app.schemas.user import UserOut

# --- Schema cơ sở cho SME ---
class SMEBase(BaseModel):
    business_name: str
    tax_code: str
    address: Optional[str] = None
    
    # --- THAY ĐỔI: Tách coordinates thành 2 trường float ---
    # Bỏ trường coordinates: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Thêm area_id vì logic đăng ký đã có gán area
    area_id: Optional[str] = None
    
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None

# --- Schema cho việc TẠO MỚI SME ---
class SMECreate(SMEBase):
    business_name: str
    tax_code: str

# --- Schema cho việc CẬP NHẬT SME ---
class SMEUpdate(BaseModel):
    business_name: Optional[str] = None
    tax_code: Optional[str] = None
    address: Optional[str] = None
    
    # --- THAY ĐỔI: Update riêng lẻ ---
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_id: Optional[str] = None
    
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None 

# --- Schema cho dữ liệu TRẢ VỀ (response) ---
class SMEOut(SMEBase):
    # Các trường latitude, longitude, area_id đã được kế thừa từ SMEBase
    sme_id: str
    status: str
    created_at: datetime
    
    users: List[UserOut] = []

    class Config:
        from_attributes = True