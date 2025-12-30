# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Khởi tạo đối tượng để mã hóa mật khẩu, sử dụng thuật toán bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.JWT_ALGORITHM

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Tạo một JSON Web Token (JWT) mới.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    So sánh mật khẩu thuần túy với mật khẩu đã được mã hóa.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Mã hóa một mật khẩu thuần túy.
    """
    return pwd_context.hash(password)


def verify_token(token: str) -> dict:
    """
    Giải mã và xác thực một JWT.
    Trả về payload nếu token hợp lệ, ngược lại ném ra lỗi.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError as e:
        raise e