# app/db/session.py
from fastapi import HTTPException, status
from app.db.mysql_connection import get_db_pool 
import aiomysql
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[aiomysql.Connection, None]:
    """
    Dependency trả về connection (để controller tự quản lý transaction).
    """
    pool = get_db_pool()
    
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection pool is not initialized."
        )

    # Lấy connection từ pool
    async with pool.acquire() as conn:
        yield conn 
        # Connection sẽ tự trả về pool sau khi request xong