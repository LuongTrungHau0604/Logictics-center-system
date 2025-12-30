from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config import settings

# --- 1. Define Model cho User (để dùng dấu chấm .role, .user_id) ---
class TokenData(BaseModel):
    user_id: int 
    role: str

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_token(
    subject: str,
    expires_delta: timedelta,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Tạo JWT token với custom claims"""
    payload = {"sub": subject, "exp": datetime.utcnow() + expires_delta}
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu thô và mật khẩu đã băm"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Băm mật khẩu"""
    return pwd_context.hash(password)

def create_refresh_token(data: dict) -> str:
    """Tạo refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Xác thực JWT token và trả về payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# --- 2. Thêm hàm get_current_user ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency dùng để bảo vệ API.
    Nó sẽ lấy token, verify và trả về thông tin user (user_id, role).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Dùng hàm verify_token có sẵn để lấy payload
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Lấy thông tin từ payload (Giả sử lúc tạo token bạn đã lưu 'sub' và 'role')
    user_id_str: str = payload.get("sub")
    role: str = payload.get("role")

    if user_id_str is None or role is None:
        raise credentials_exception
        
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    # Trả về object để bên Shipper.py có thể gọi current_user.role
    return TokenData(user_id=user_id, role=role)