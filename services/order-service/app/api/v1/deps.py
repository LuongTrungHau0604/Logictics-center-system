# services/order-service/app/api/v1/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import AsyncGenerator
import logging
import aiomysql
import asyncio
# SỬA LỖI: Import PyJWT correctly
try:
    from jose import jwt  # Prefer python-jose
except ImportError:
    import jwt  # Fallback to PyJWT
from datetime import datetime

from app.core.config import settings
from app.schemas.user import UserOut
from app.db.mysql_connection import get_db_pool
from app.services.auth_client import auth_client

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[aiomysql.Connection, None]:
    """
    Dependency lấy database connection và quản lý transaction (commit/rollback).
    """
    db_pool = get_db_pool()
    
    if db_pool is None:
        logger.error("❌ FATAL: DB pool is None. Service startup failed?")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not ready"
        )
        
    logger.debug(f"✅ DB pool available. Status: size={db_pool.size}, free={db_pool.freesize}")

    conn: aiomysql.Connection = None
    
    # === PHẦN 1: LẤY CONNECTION ===
    # Phần này của bạn đã làm rất tốt
    try:
        logger.debug("⏳ Acquiring connection from pool...")
        conn = await asyncio.wait_for(db_pool.acquire(), timeout=5.0)
        logger.debug(f"✅ Connection acquired [ID: {id(conn)}]")

        # Test connection
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
        logger.debug(f"✅ Connection ping successful [ID: {id(conn)}]")

        # Set autocommit
        await conn.autocommit(False)
        logger.debug(f"✅ Autocommit set to False [ID: {id(conn)}]")

    except asyncio.TimeoutError:
        logger.error(f"❌ TIMEOUT: Cannot acquire DB connection after 5s. Pool full? (Free: {db_pool.freesize})")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection timeout"
        )
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR acquiring/testing connection: {e}", exc_info=True)
        if conn:
            db_pool.release(conn)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}"
        )

    # === PHẦN 2: QUẢN LÝ TRANSACTION (YIELD, COMMIT, ROLLBACK) ===
    # Đây là phần được sửa đổi
    try:
        logger.debug(f"🚀 [ID: {id(conn)}] Ready, yielding to endpoint...")
        yield conn
        
        # Nếu endpoint chạy xong mà KHÔNG ném ra lỗi, commit
        logger.debug(f"✅ Endpoint completed successfully. Committing... [ID: {id(conn)}]")
        await conn.commit()
        logger.debug(f"✅ Commit successful [ID: {id(conn)}]")
        
    except Exception as e:
        # Nếu có bất kỳ lỗi nào xảy ra trong endpoint (HTTPException, v.v.)
        logger.warning(f"🔥 Endpoint failed. Rolling back... [ID: {id(conn)}]. Error: {e}", exc_info=True)
        await conn.rollback()
        logger.warning(f"🔥 Rollback successful [ID: {id(conn)}]")
        
        # Rất quan trọng: Ném lỗi ra lại để FastAPI xử lý
        raise e 
        
    finally:
        # Luôn luôn chạy, bất kể thành công hay thất bại
        if conn:
            try:
                logger.debug(f"🔄 Returning [ID: {id(conn)}] to pool...")
                db_pool.release(conn)
                logger.debug(f"✅ Returned [ID: {id(conn)}] to pool. Pool free: {db_pool.freesize}")
            except Exception as release_error:
                logger.warning(f"⚠️ Error returning connection [ID: {id(conn)}] to pool: {release_error}", exc_info=True)

# HTTPBearer security scheme
security = HTTPBearer(
    scheme_name="JWT Token",
    description="Enter your JWT token (without 'Bearer ' prefix)"
)

def decode_token_locally(token: str) -> dict:
    """
    DEBUG ONLY: Decode token locally để xem payload với proper error handling
    """
    try:
        logger.debug("🔍 Attempting to decode token locally...")
        
        # SỬA LỖI: Handle different JWT libraries
        try:
            # Try with python-jose first
            from jose import jwt as jose_jwt
            payload = jose_jwt.get_unverified_claims(token)
            logger.debug(f"🔍 Token payload (jose): {payload}")
        except ImportError:
            # Fallback to PyJWT
            import jwt as pyjwt
            payload = pyjwt.decode(token, options={"verify_signature": False})
            logger.debug(f"🔍 Token payload (PyJWT): {payload}")
        except Exception as jwt_error:
            logger.error(f"❌ Error with jose/PyJWT: {jwt_error}")
            # Try manual base64 decode as last resort
            import base64
            import json
            try:
                # Split token parts
                parts = token.split('.')
                if len(parts) >= 2:
                    # Decode payload (second part)
                    payload_part = parts[1]
                    # Add padding if needed
                    payload_part += '=' * (4 - len(payload_part) % 4)
                    decoded_bytes = base64.b64decode(payload_part)
                    payload = json.loads(decoded_bytes.decode('utf-8'))
                    logger.debug(f"🔍 Token payload (manual): {payload}")
                else:
                    logger.error("❌ Invalid token format for manual decode")
                    return {}
            except Exception as manual_error:
                logger.error(f"❌ Manual decode failed: {manual_error}")
                return {}
        
        # Check expiration
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            current_datetime = datetime.utcnow()
            
            logger.debug(f"🕐 Current time (UTC): {current_datetime}")
            logger.debug(f"🕐 Token expires (UTC): {exp_datetime}")
            logger.debug(f"🕐 Token expired: {current_datetime > exp_datetime}")
            
            # Calculate time difference
            time_diff = exp_datetime - current_datetime
            if time_diff.total_seconds() > 0:
                logger.debug(f"🕐 Token valid for: {time_diff}")
            else:
                logger.warning(f"🕐 Token expired by: {-time_diff}")
        else:
            logger.warning("🕐 No expiration field found in token")
            
        return payload
        
    except Exception as e:
        logger.error(f"❌ Error decoding token locally: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserOut:
    """
    Validate JWT token via Identity Service với detailed debugging
    """
    logger.info("=" * 80)
    logger.info("🔑 Starting token validation process...")
    
    try:
        # Extract token từ credentials
        token = credentials.credentials
        logger.info(f"🔑 Token received (length: {len(token)})")
        logger.info(f"🔑 Token first 100 chars: {token[:100]}...")
        logger.info(f"🔑 Token last 50 chars: ...{token[-50:]}")
        
        # DEBUG: Decode token locally để xem payload
        logger.info("🔍 Decoding token locally for debugging...")
        token_payload = decode_token_locally(token)
        
        if token_payload:
            logger.info(f"✅ Token payload decoded successfully")
            logger.info(f"🔍 Subject (sub): {token_payload.get('sub', 'N/A')}")
            logger.info(f"🔍 User ID: {token_payload.get('user_id', 'N/A')}")
            logger.info(f"🔍 Role: {token_payload.get('role', 'N/A')}")
            logger.info(f"🔍 SME ID: {token_payload.get('sme_id', 'N/A')}")
        else:
            logger.warning("⚠️ Could not decode token locally")
        
        # Check basic token format
        if not token or len(token) < 50:
            logger.error("❌ Token too short or empty")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token has 3 parts (header.payload.signature)
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.error(f"❌ Token format invalid. Parts count: {len(token_parts)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ Token format valid (3 parts)")
        
        # Log Identity Service URL
        logger.info(f"🌐 Identity Service URL: {settings.IDENTITY_SERVICE_URL}")
        logger.info(f"🌐 Full validation URL: {settings.IDENTITY_SERVICE_URL}/auth/users/me")
        
        # Gọi Identity Service để validate token
        logger.info("📞 Calling Identity Service for token validation...")
        user = await auth_client.validate_token_and_get_user(token)
        
        if user is None:
            logger.error("❌ Token validation failed - Identity Service returned None")
            logger.error("💡 Possible issues:")
            logger.error("   1. Token expired")
            logger.error("   2. Identity Service is down")
            logger.error("   3. Token signature invalid")
            logger.error("   4. User not found in Identity Service")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ Token validated successfully!")
        logger.info(f"✅ User: {user.username}")
        logger.info(f"✅ Role: {user.role}")
        logger.info(f"✅ SME ID: {user.sme_id}")
        logger.info("=" * 80)
        
        return user
        
    except HTTPException as e:
        logger.error(f"❌ HTTP Exception during validation: {e.detail}")
        logger.error("=" * 80)
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during token validation: {e}")
        logger.error("❌ Exception type:", type(e).__name__)
        logger.error("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during authentication: {str(e)}"
        )

async def get_current_sme_owner(
    current_user: UserOut = Depends(get_current_user)
) -> UserOut:
    """Dependency requiring SME_OWNER or ADMIN role"""
    
    logger.info(f"🔐 Checking SME Owner permissions for user: {current_user.username}")
    logger.info(f"🔐 User role: {current_user.role}")
    
    if current_user.role not in ["SME_OWNER", "ADMIN"]:
        logger.warning(f"❌ Insufficient permissions for user {current_user.username} (Role: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SME Owner or Admin access required. Current role: {current_user.role}"
        )
    
    logger.info(f"✅ SME Owner access granted for user: {current_user.username}")
    return current_user