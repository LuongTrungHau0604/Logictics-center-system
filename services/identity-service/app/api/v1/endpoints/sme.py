import httpx
import logging
import aiomysql
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

# --- Schemas ---
from app.schemas.sme import SMEOut, SMEUpdate
from app.schemas.user import UserCreate, UserOut

# --- Services ---
from app.services.sme_service import SmeService

# --- Dependencies ---
from app.api.v1.deps import (
    get_db, 
    get_current_user, 
    get_current_admin_user,
    get_current_sme_owner
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["SME Management"])

# --- Admin Endpoints ---

@router.get(
    "/", 
    response_model=List[SMEOut],
    dependencies=[Depends(get_current_admin_user)]
)
async def get_all_smes(
    db: aiomysql.Connection = Depends(get_db),
    skip: int = Query(0, ge=0),
    # SỬA: Tăng le=200 lên le=2000 hoặc 5000 tùy nhu cầu
    limit: int = Query(100, ge=1, le=2000) 
):
    """
    Lấy danh sách TẤT CẢ SME (Phân trang, Chỉ Admin).
    """
    logger.info("Admin đang lấy danh sách tất cả SME")
    return await SmeService.get_all_smes(db, skip=skip, limit=limit)

@router.get(
    "/status/{status_name}", 
    response_model=List[SMEOut],
    dependencies=[Depends(get_current_admin_user)]
)
async def get_smes_by_status(
    status_name: str = Path(..., description="Trạng thái (PENDING, ACTIVE, INACTIVE)"),
    db: aiomysql.Connection = Depends(get_db),
    skip: int = Query(0, ge=0),
    # SỬA: Tăng le=200 lên le=2000 để Frontend lấy được danh sách lớn đếm số liệu
    limit: int = Query(100, ge=1, le=2000)
):
    """
    Lấy danh sách SME theo trạng thái (PENDING, ACTIVE...) (Chỉ Admin).
    """
    if status_name.upper() not in ["PENDING", "ACTIVE", "INACTIVE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trạng thái phải là PENDING, ACTIVE, hoặc INACTIVE"
        )
    logger.info(f"Admin đang lấy danh sách SME với status: {status_name.upper()}")
    return await SmeService.get_smes_by_status(db, status_name.upper(), skip, limit)

@router.put(
    "/{sme_id}/status", 
    response_model=SMEOut,
    dependencies=[Depends(get_current_admin_user)] # Chỉ Admin
)
async def approve_or_reject_sme(
    sme_id: str,
    new_status: str = Query(..., regex="^(ACTIVE|INACTIVE)$"), # Chỉ cho phép 2 giá trị này
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Duyệt (ACTIVE) hoặc Từ chối (INACTIVE) một SME (Chỉ Admin).
    """
    logger.info(f"Admin đang đổi status SME {sme_id} thành {new_status}")
    
    # Dùng SMEUpdate để chỉ cập nhật 1 trường 'status'
    update_data = SMEUpdate(status=new_status)
    
    # Không cần httpx client vì chỉ đổi status, không geocode
    async with httpx.AsyncClient() as client:
        updated_sme = await SmeService.update_sme_details(
            db=db,
            http_client=client, # Vẫn truyền vào
            sme_id=sme_id,
            sme_data=update_data
        )
    
    if not updated_sme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy SME {sme_id}"
        )
    return updated_sme


# --- SME Owner / User Endpoints ---

@router.get(
    "/details/{sme_id}", 
    response_model=SMEOut
)
async def get_my_sme_details(
    sme_id: str,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết của SME (bao gồm danh sách user).
    Chỉ user thuộc SME đó, hoặc Admin mới thấy.
    """
    if current_user.role != "ADMIN" and current_user.sme_id != sme_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem SME này."
        )
        
    sme = await SmeService.get_sme_details(db, sme_id)
    
    if not sme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy SME {sme_id}"
        )
    return sme

@router.put(
    "/details/{sme_id}",
    response_model=SMEOut
)
async def update_my_sme_details(
    sme_id: str,
    sme_data: SMEUpdate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner) # Chỉ Owner
):
    """
    SME Owner tự cập nhật thông tin công ty mình (vd: đổi địa chỉ).
    """
    if current_user.sme_id != sme_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ có thể cập nhật SME của mình."
        )
        
    # Ngăn Owner tự duyệt (chỉ Admin mới được đổi status)
    if sme_data.status is not None:
        logger.warning(f"SME Owner {current_user.user_id} cố gắng đổi status (bị cấm)")
        sme_data.status = None 

    async with httpx.AsyncClient() as client:
        updated_sme = await SmeService.update_sme_details(
            db=db,
            http_client=client,
            sme_id=sme_id,
            sme_data=sme_data
        )
    
    if not updated_sme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy SME {sme_id}"
        )
    return updated_sme

@router.post(
    "/{sme_id}/users", 
    response_model=UserOut
)
async def create_sme_user(
    sme_id: str,
    user_data: UserCreate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_user) # Owner hoặc Admin
):
    """
    Tạo một User (SME_USER) mới cho SME.
    Chỉ SME_OWNER của SME đó, hoặc ADMIN mới được phép.
    """
    # Phân quyền
    is_admin = current_user.role == "ADMIN"
    is_owner_of_this_sme = (
        current_user.role == "SME_OWNER" and 
        current_user.sme_id == sme_id
    )
    
    if not (is_admin or is_owner_of_this_sme):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Admin hoặc Chủ SME mới có quyền thêm user."
        )

    logger.info(f"Đang tạo SME_USER mới cho SME {sme_id} bởi {current_user.user_id}")
    
    # SmeService sẽ tự gán role="SME_USER" và sme_id
    new_user = await SmeService.create_sme_user(
        db=db,
        sme_id=sme_id,
        user_data=user_data,
        current_user=current_user
    )
    
    return new_user

# --- SME Owner Self-Management Endpoints (MỚI THÊM) ---

@router.get("/me/profile", response_model=SMEOut)
async def get_my_profile(
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner) # Chỉ SME Owner
):
    """
    Lấy thông tin profile của chính SME đang đăng nhập.
    """
    if not current_user.sme_id:
        raise HTTPException(status_code=404, detail="User không liên kết với SME nào.")
        
    sme = await SmeService.get_sme_details(db, current_user.sme_id)
    if not sme:
        raise HTTPException(status_code=404, detail="SME Profile not found")
    return sme

@router.put("/me/profile", response_model=SMEOut)
async def update_my_profile(
    sme_data: SMEUpdate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_sme_owner) # Chỉ SME Owner
):
    """
    SME tự cập nhật thông tin của mình (Tên, địa chỉ, sđt...).
    """
    if not current_user.sme_id:
        raise HTTPException(status_code=404, detail="User không liên kết với SME nào.")

    # Ngăn đổi status
    if sme_data.status is not None:
        sme_data.status = None 

    async with httpx.AsyncClient() as client:
        updated_sme = await SmeService.update_sme_details(
            db=db,
            http_client=client,
            sme_id=current_user.sme_id,
            sme_data=sme_data
        )
        
    if not updated_sme:
        raise HTTPException(status_code=404, detail="Update failed")
        
    return updated_sme