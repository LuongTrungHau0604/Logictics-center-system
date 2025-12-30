# order-service/app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schema này cần thiết cho định nghĩa của CRUDBase, dù order-service không trực tiếp tạo user.
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    phone: Optional[str] = None

# --- CLASS CÒN THIẾU GÂY RA LỖI ---
# Schema dùng khi cập nhật User. Tất cả các trường đều là tùy chọn (Optional).
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None

# Schema dùng để trả về dữ liệu User (an toàn, không có mật khẩu)
class UserOut(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    created_at: datetime
    sme_id: Optional[str] = None
    

    class Config:
        from_attributes = True # Cho phép Pydantic đọc từ đối tượng SQLAlchemy