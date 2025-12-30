# File này không cần thiết nữa với PyMySQL
# Tạo base CRUD class đơn giản

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from app.db.mysql_connection import mysql_db

ModelType = TypeVar("ModelType")

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], table_name: str):
        self.model = model
        self.table_name = table_name
    
    async def get(self, id: Any) -> Optional[ModelType]:
        """Get by ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        result = await mysql_db.execute_query(query, (id,))
        if result:
            return self.model.from_dict(result[0])
        return None
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records"""
        query = f"SELECT * FROM {self.table_name} LIMIT %s OFFSET %s"
        result = await mysql_db.execute_query(query, (limit, skip))
        return [self.model.from_dict(row) for row in result]
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create new record"""
        columns = ', '.join(obj_in.keys())
        placeholders = ', '.join(['%s'] * len(obj_in))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        await mysql_db.execute_insert(query, tuple(obj_in.values()))
        return self.model.from_dict(obj_in)