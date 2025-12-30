# services/identity-service/app/schemas/token.py

from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserOut

class Token(BaseModel):
    """
    Schema cho response khi login thành công.
    Gửi về cho client.
    """
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    """
    Schema cho dữ liệu được lưu trữ bên trong JWT token (payload).
    """
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    sme_id: Optional[str] = None
