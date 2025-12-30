import logging
import aiomysql
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.mysql_connection import get_db_pool
from app.services.auth_service import AuthService
from app.schemas.user import UserOut
from app.core.config import settings
import asyncio

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[aiomysql.Connection, None]:
    """
    Database dependency đã được cấu trúc lại để không "nuốt" lỗi nghiệp vụ.
    """
    pool = get_db_pool()
    
    if pool is None:
        logger.error("❌ Database pool not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database pool not initialized"
        )
    
    connection = None
    try:
        try:
            connection = await asyncio.wait_for(
                pool.acquire(), 
                timeout=5.0
            )
            
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                await cursor.fetchone()
                
            await connection.autocommit(False)
            logger.debug(f"✅ DB connection acquired (pool: {pool.freesize}/{pool.size})")

        except asyncio.TimeoutError:
            logger.error("❌ Database connection timeout on acquire")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection timeout"
            )
        except Exception as e:
            logger.error(f"❌ Database connection error on acquire: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection failed: {str(e)}"
            )

        yield connection
        
    finally:
        if connection:
            try:
                pool.release(connection)
                logger.debug("🔄 DB connection released back to pool")
            except Exception as release_error:
                logger.warning(f"⚠️ Failed to release connection, but this will not mask the original error: {release_error}")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_str}/auth/login")

async def get_current_user(
    db: aiomysql.Connection = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> UserOut:
    """
    Dependency để lấy user hiện tại từ token với detailed logging.
    """
    logger.debug("🔑 Token validation started...")
    logger.debug(f"🔑 Token (first 50 chars): {token[:50]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        user = await AuthService.get_user_from_token(db, token)
        if user is None:
            logger.warning("❌ Token validation failed - user not found or token invalid")
            raise credentials_exception
        
        logger.info(f"✅ Token validated for user: {user.username} (Role: {user.role})")
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions (401, 403, etc.)
        raise
    except Exception as e:
        logger.error(f"❌ Token validation error: {e}")
        raise credentials_exception

async def get_current_admin_user(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """Require ADMIN role"""
    if current_user.role != "ADMIN":
        logger.warning(f"❌ Admin access denied for user: {current_user.username} (Role: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin access required"
        )
    return current_user

async def get_current_sme_owner(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """Require SME_OWNER role"""
    if current_user.role != "SME_OWNER":
        logger.warning(f"❌ SME Owner access denied for user: {current_user.username} (Role: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="SME Owner access required"
        )
    return current_user

# SỬA LỖI: Thêm dependency cho flexible role checking
async def get_current_active_user(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """
    Get current active user without role restriction.
    This is used by /auth/users/me endpoint.
    """
    logger.debug(f"✅ Active user access for: {current_user.username}")
    return current_user

