# app/schemas/sme_registration.py

from pydantic import BaseModel, EmailStr
from typing import Optional
# (Không cần import UserCreate/SMECreate nữa)

class SmeOwnerRegistration(BaseModel):
    """
    Schema "phẳng" cho request đăng ký SME Owner.
    Chỉ yêu cầu một bộ email/phone duy nhất.
    """
    
    # --- Dữ liệu User (Owner) ---
    username: str
    password: str
    
    # --- Dữ liệu SME (Doanh nghiệp) ---
    business_name: str
    tax_code: str
    address: Optional[str] = None
    
    # --- Dữ liệu chung (Dùng cho cả User và SME) ---
    email: EmailStr
    phone: Optional[str] = None
