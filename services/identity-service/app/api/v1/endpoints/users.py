import logging
import aiomysql
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import aiomysql

from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.user_service import UserService
from app.api.v1.deps import get_current_user, get_current_admin_user, get_db
from fastapi import Path
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/{user_id}", 
    response_model=UserOut,
    dependencies=[Depends(get_current_admin_user)] # Chỉ Admin
)
async def get_user_by_id(
    user_id: str = Path(..., description="ID của user cần lấy"),
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Lấy thông tin của một user bất kỳ bằng ID (Chỉ Admin).
    """
    logger.info(f"Admin đang lấy thông tin user: {user_id}")
    user = await UserService.get_user_details(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    return user

@router.put("/user/me", response_model=UserOut)
async def update_current_user_profile(
    user_data: UserUpdate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    User tự cập nhật thông tin profile của chính mình.
    (ví dụ: đổi mật khẩu, số điện thoại).
    """
    logger.info(f"User {current_user.user_id} đang cập nhật profile")
    
    # user_data.sme_id sẽ bị bỏ qua bởi CRUDUser
    # (Trừ khi chúng ta thêm logic cấm user tự đổi sme_id)
    if user_data.role is not None and user_data.role != current_user.role:
        logger.warning(f"User {current_user.user_id} cố gắng đổi role (bị cấm)")
        user_data.role = None # Ngăn user tự đổi role
        
    if user_data.sme_id is not None and user_data.sme_id != current_user.sme_id:
        logger.warning(f"User {current_user.user_id} cố gắng đổi sme_id (bị cấm)")
        user_data.sme_id = None # Ngăn user tự đổi SME
        
    updated_user = await UserService.update_user_profile(
        db, user_id=current_user.user_id, user_data=user_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cập nhật thất bại"
        )
        
    return updated_user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: aiomysql.Connection = Depends(get_db)
):
    
    """
    Đăng ký người dùng bình thường.
    
    Nếu cung cấp `sme_phone`, hệ thống sẽ tự động tìm kiếm
    doanh nghiệp (SME) tương ứng và gán người dùng này vào
    doanh nghiệp đó với vai trò `SME_USER`.
    
    - **username**: Tên đăng nhập (unique)
    - **password**: Mật khẩu
    - **email**: Email (unique)
    - **phone**: Số điện thoại cá nhân (optional)
    - **role**: Vai trò (USER hoặc SME_USER, sẽ tự động gán SME_USER nếu có sme_phone)
    - **sme_phone**: SĐT của doanh nghiệp (optional, để liên kết với SME)
    """
    try:
        # Chỉ cần truyền 'user_data' trực tiếp
        new_user = await UserService.register_regular_user(db, user_data) 
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi đăng ký: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=UserOut)
async def get_user_profile(
    user_id: str,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Lấy thông tin profile user theo ID.
    """
    user = await UserService.get_user_details(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    return user

@router.put("/profile/{user_id}", response_model=UserOut)
async def update_user_profile(
    user_id: str,
    user_data: UserUpdate,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Cập nhật thông tin profile user.
    """
    updated_user = await UserService.update_user_profile(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể cập nhật user"
        )
    return updated_user

@router.get("/check-availability")
async def check_user_availability(
    username: str = None,
    email: str = None,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Kiểm tra username hoặc email đã được sử dụng chưa.
    """
    if not username and not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần cung cấp username hoặc email"
        )
    
    exists = await UserService.check_user_exists(db, username, email)
    
    return {
        "username": username,
        "email": email,
        "available": not exists,
        "message": "Có thể sử dụng" if not exists else "Đã được sử dụng"
    }

@router.get("/by-username/{username}", response_model=UserOut)
async def get_user_by_username(
    username: str,
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Lấy user theo username (dùng internal).
    """
    user = await UserService.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    return user