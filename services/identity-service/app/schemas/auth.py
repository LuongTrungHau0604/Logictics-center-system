from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# 1. (INPUT) Schema cho request body khi login
class LoginRequest(BaseModel):
    """
    Schema cho request body dạng JSON khi đăng nhập.
    """
    username: str
    password: str

# 2. (OUTPUT) Schema cho response khi login thành công
class Token(BaseModel):
    """
    Schema trả về khi đăng nhập thành công.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user_info: Optional[Dict[str, Any]] = None

# 3. (INTERNAL) Schema cho dữ liệu bên trong payload của JWT
class TokenData(BaseModel):
    """
    Schema định nghĩa dữ liệu được lưu trong payload của JWT.
    """
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None

# 4. (OUTPUT) Schema chung cho các response lỗi HTTP
class HTTPError(BaseModel):
    """
    Schema chuẩn cho các thông báo lỗi HTTP.
    """
    detail: str

    class Config:
        json_schema_extra = {
            "example": {"detail": "Nội dung lỗi chi tiết..."},
        }