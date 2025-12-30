from pydantic import BaseModel
from typing import Optional, List

class DispatchOrderSummary(BaseModel):
    id: str
    code: str
    from_location: str
    to_location: str
    status: str
    priority: str = "medium"  # Mặc định vì DB chưa có cột này
    total_distance: float
    total_legs: int
    created_at: str

    class Config:
        from_attributes = True