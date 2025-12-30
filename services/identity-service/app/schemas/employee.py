from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

# --- Base Schema (Các trường chung) ---
class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    dob: Optional[date] = None
    role: str = Field(..., description="Vai trò: WAREHOUSE_MANAGER, SHIPPER, STAFF...")
    phone: str = Field(..., max_length=20)
    email: EmailStr
    warehouse_id: Optional[str] = Field(None, description="ID kho mà nhân viên này quản lý hoặc làm việc")

# --- Schema dùng để tạo mới (Input) ---
class EmployeeCreate(EmployeeBase):
    # user_id thường được tạo từ bảng User trước, sau đó link sang đây
    # hoặc có thể để optional nếu logic của bạn tạo Employee độc lập
    pass 

# --- Schema dùng để cập nhật (Input) ---
class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None  # ACTIVE, INACTIVE, SUSPENDED
    warehouse_id: Optional[str] = None

# --- Schema dữ liệu trả về (Output) ---
class EmployeeOut(EmployeeBase):
    employee_id: str
    user_id: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # Cho phép map từ dict hoặc object ORM