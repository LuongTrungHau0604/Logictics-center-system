# app/schemas/user.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Schema cho dữ liệu client gửi lên khi đăng ký
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr  # Đồng bộ hóa kiểu dữ liệu
    phone: Optional[str] = None
    sme_phone: Optional[str] = None  # Thêm sme_phone

# Schema cho dữ liệu client gửi lên khi cập nhật
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None  # Đồng bộ hóa kiểu dữ liệu
    phone: Optional[str] = None
    password: Optional[str] = None  # Mật khẩu mới, nếu có
    role: Optional[str] = None
    sme_id: Optional[str] = None  # Thêm sme_id

# Schema cơ sở, đại diện cho dữ liệu trong DB
class UserBase(BaseModel):
    user_id: str  # Thay đổi từ id: int
    username: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    sme_id: Optional[str] = None  # Thêm sme_id
    created_at: datetime
    # updated_at và is_active đã bị loại bỏ để khớp với DB

    class Config:
        from_attributes = True

# Alias cho User (tương thích với code cũ)
User = UserBase

# Schema cho dữ liệu trả về client (an toàn, không có password_hash)
class UserOut(UserBase):
    """Schema trả về cho client, ẩn thông tin nhạy cảm"""
    pass

# Schema cho dữ liệu internal với password hash
class UserInDB(UserBase):
    password_hash: str  # Đổi từ hashed_password để khớp DB
    
