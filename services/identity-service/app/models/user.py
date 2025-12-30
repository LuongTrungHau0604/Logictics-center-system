from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

# --- Model chính (Khớp với DB) ---
class User(BaseModel):
    user_id: Optional[str] = None
    username: str
    password_hash: str
    email: EmailStr
    phone: Optional[str] = None
    role: str  # Ví dụ: "SME_OWNER", "SME_USER", "ADMIN"
    sme_id: Optional[str] = None  # <--- THÊM VÀO
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Tạo User từ dict (database row)"""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert User thành dict để insert vào database"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "sme_id": self.sme_id  # <--- THÊM VÀO
        }

# --- Model để tạo User ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone: Optional[str] = None
    role: str = "SME_USER"  # <--- Đổi default (hoặc "SME_OWNER" tùy logic)
    sme_phone : Optional[str] = None
    sme_id: Optional[str] = None  # <--- THÊM VÀO (Cần thiết khi tạo SME_USER)

# --- Model để cập nhật User ---
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    sme_id: Optional[str] = None  # <--- THÊM VÀO
    # <--- XÓA status

# --- Model để trả về cho Client ---
class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    phone: Optional[str] = None
    role: str
    sme_id: Optional[str] = None  # <--- THÊM VÀO
    created_at: datetime

    class Config:
        from_attributes = True