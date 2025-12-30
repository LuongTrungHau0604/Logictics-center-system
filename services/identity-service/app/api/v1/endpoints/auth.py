import httpx
import logging
import aiomysql
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# --- Schemas ---
from app.schemas.user import UserOut
from app.schemas.SME_Registration import SmeOwnerRegistration
from app.schemas.token import Token
from app.core.config import settings
# --- Services ---
from app.services.auth_service import AuthService
from app.services.sme_service import SmeService

# --- Dependencies ---
from app.api.v1.deps import get_db, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

@router.post("/register-sme-owner", response_model=UserOut)
async def register_sme_owner(
    reg_data: SmeOwnerRegistration,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Endpoint để đăng ký SME Owner với proper connection management
    """
    logger.info(f"🚀 Bắt đầu đăng ký SME Owner cho tax_code: {reg_data.tax_code}")
    
    # SỬA LỖI: Tạo HTTP client trong context manager
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # SỬA LỖI: Explicit transaction management
            await db.begin()
            
            # Business logic validation và processing
            user = await SmeService.register_sme_owner(
                db=db,
                http_client=client,
                reg_data=reg_data
            )
            
            # SỬA LỖI: Explicit commit chỉ khi thành công
            await db.commit()
            
            logger.info(f"✅ Đăng ký SME Owner thành công: {user.user_id}")
            return user
            
        except HTTPException as he:
            # Business logic errors - ROLLBACK transaction
            logger.warning(f"⚠️ Business logic error: {he.detail}")
            
            try:
                await db.rollback()
                logger.debug("🔄 Transaction rolled back successfully")
            except Exception as rollback_error:
                logger.error(f"❌ Rollback failed: {rollback_error}")
            
            # Re-raise HTTPException với original status code và message
            raise he
            
        except aiomysql.Error as db_error:
            # Database specific errors
            logger.error(f"❌ Database error during SME registration: {db_error}")
            
            try:
                await db.rollback()
                logger.debug("🔄 Transaction rolled back due to DB error")
            except Exception as rollback_error:
                logger.error(f"❌ Rollback failed: {rollback_error}")
            
            # Map specific MySQL errors
            error_msg = str(db_error)
            if "Duplicate entry" in error_msg:
                if "tax_code" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Tax code already registered"
                    )
                elif "email" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT, 
                        detail="Email already registered"
                    )
            
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database operation failed"
            )
                
        except Exception as e:
            # Unexpected errors
            logger.error(f"❌ Unexpected error during SME registration: {e}", exc_info=True)
            
            try:
                await db.rollback()
                logger.debug("🔄 Transaction rolled back due to unexpected error")
            except Exception as rollback_error:
                logger.error(f"❌ Rollback failed: {rollback_error}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: aiomysql.Connection = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login endpoint"""
    try:
        logger.info(f"🔐 Login attempt for: {form_data.username}")
        
        user = await AuthService.authenticate_user(
            db, 
            username=form_data.username, 
            password=form_data.password
        )
        
        if not user:
            logger.warning(f"❌ Authentication failed for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ User authenticated: {user.username} (Role: {user.role})")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.user_id), # CHÚ Ý: sub nên là String của ID (chuẩn JWT)
            "username": user.username, # Thêm username vào claim phụ
            "role": user.role,
            "sme_id": user.sme_id,
        }
        
        access_token = AuthService.create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "sme_id": user.sme_id,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
        
        logger.info(f"✅ Login successful for: {user.username}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

# SỬA LỖI: THÊM ENDPOINT này để Order Service có thể validate token
@router.get("/users/me", response_model=UserOut)
async def get_current_user_info(
    current_user: UserOut = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    This endpoint is used by other services to validate tokens and get user info.
    """
    logger.info(f"📋 Token validation request for user: {current_user.username}")
    logger.debug(f"📋 User details: {current_user.username} (Role: {current_user.role}, SME: {current_user.sme_id})")
    
    return current_user

# THÊM: Debug endpoint để test token validation
@router.get("/debug/token-info")
async def debug_token_info(
    current_user: UserOut = Depends(get_current_user)
):
    """
    Debug endpoint để test token validation
    """
    return {
        "message": "Token is valid",
        "user": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "sme_id": current_user.sme_id,
        },
        "timestamp": "2024-12-11T10:30:00Z"
    }