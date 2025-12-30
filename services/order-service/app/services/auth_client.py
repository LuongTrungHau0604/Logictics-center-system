import httpx
import logging
from typing import Optional
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.user import UserOut

logger = logging.getLogger(__name__)

class AuthClient:
    """
    Client để gọi Identity Service để validate token và lấy user info
    """
    
    def __init__(self):
        # Đảm bảo URL không có dấu gạch chéo ở cuối để ghép chuỗi cho chuẩn
        self.identity_service_url = str(settings.IDENTITY_SERVICE_URL).rstrip("/")
        self.timeout = 10.0
        logger.info(f"🔧 AuthClient initialized with URL: {self.identity_service_url}")
    
    async def validate_token_and_get_user(self, token: str) -> Optional[UserOut]:
        """
        Gọi Identity Service để validate token và lấy thông tin user
        """
        logger.info("🚀 Starting Identity Service validation...")
        
        try:
            # --- CẬP NHẬT QUAN TRỌNG: Đường dẫn API chuẩn ---
            # Identity Service structure: /api/v1 + /auth + /users/me
            validation_url = f"{self.identity_service_url}/auth/users/me"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "Order-Service/1.0"
            }
            
            logger.info(f"📤 Request URL: {validation_url}")
            # logger.debug(f"📤 Token: {token[:20]}...") 
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    validation_url,
                    headers=headers
                )
                
                logger.info(f"📥 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"✅ Token validated successfully for user: {user_data.get('username')}")
                    
                    # Convert response to UserOut schema
                    # LƯU Ý: UserOut của Order Service phải giống UserOut của Identity Service
                    try:
                        user = UserOut(**user_data)
                        return user
                    except Exception as schema_error:
                        logger.error(f"❌ Schema validation failed: {schema_error}")
                        logger.error(f"❌ Data received: {user_data}")
                        return None
                        
                elif response.status_code == 401:
                    logger.warning(f"❌ Token invalid or expired (401)")
                    return None
                    
                elif response.status_code == 403:
                    logger.warning(f"❌ Insufficient permissions (403)")
                    return None
                    
                elif response.status_code == 404:
                    logger.error(f"❌ Endpoint not found (404). Check URL: {validation_url}")
                    return None
                    
                else:
                    logger.error(f"❌ Identity Service Error: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.ConnectError:
            logger.critical(f"❌ Cannot connect to Identity Service at {self.identity_service_url}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Identity Service unavailable"
            )
            
        except httpx.TimeoutException:
            logger.error("❌ Identity Service connection timed out")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Identity Service timeout"
            )
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in AuthClient: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )

# Singleton instance
auth_client = AuthClient()