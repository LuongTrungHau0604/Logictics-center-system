from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class TokenPayLoad(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    sme_id: Optional[str] = None
    exp: datetime