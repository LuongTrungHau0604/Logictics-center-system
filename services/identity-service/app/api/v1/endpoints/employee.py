import logging
import aiomysql
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Body
from pydantic import BaseModel, Field
from app.api.v1.deps import get_current_user 

# --- Schemas ---
from app.schemas.employee import EmployeeOut, EmployeeCreate, EmployeeUpdate
from app.schemas.user import UserOut

# --- Services ---
from app.services.employee_service import EmployeeService

# --- Dependencies ---
from app.api.v1.deps import (
    get_db, 
    get_current_user, 
    get_current_admin_user,
    # get_current_sme_owner (nếu cần)
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Employee Management"])

class CreateStaffRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    full_name: str
    email: str
    phone: str
    role: str = Field(..., description="SHIPPER or WAREHOUSE_STAFF")
    warehouse_id: str
    dob: Optional[str] = None
    vehicle_type: Optional[str] = "MOTORBIKE" # Chỉ dùng cho Shipper
# --- Helper Schema cho Request Body ---
# Class này dùng để gom dữ liệu khi tạo Quản lý kho (gồm thông tin nhân viên + tài khoản login)
class WarehouseManagerRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    employee_data: EmployeeCreate

# --- Endpoints ---

@router.post(
    "/warehouse-manager", 
    response_model=EmployeeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)] # Chỉ Admin mới được tạo quản lý kho
)
async def create_warehouse_manager(
    request_data: WarehouseManagerRequest,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_admin_user)
):
    """
    Tạo mới một Warehouse Manager (Nhân viên quản lý kho).
    Bao gồm việc tạo User login và thông tin Employee.
    """
    logger.info(f"Admin {current_user.user_id} đang tạo Warehouse Manager mới: {request_data.username}")
    
    return await EmployeeService.create_warehouse_manager(
        db=db,
        employee_data=request_data.employee_data,
        username=request_data.username,
        password=request_data.password
    )



@router.get(
    "/{employee_id}", 
    response_model=EmployeeOut,
    dependencies=[Depends(get_current_user)] # User đăng nhập là xem được (có thể siết quyền thêm)
)
async def get_employee_detail(
    employee_id: str = Path(..., description="ID nhân viên (EMP-...)"),
    db: aiomysql.Connection = Depends(get_db)
):
    """
    Xem chi tiết thông tin một nhân viên.
    """
    # Lưu ý: Logic lấy chi tiết bạn cần thêm vào EmployeeService/CRUDEmployee tương tự như get_all
    # Ở đây tôi gọi trực tiếp CRUD hoặc Service tùy bạn cài đặt
    from app.crud.crud_employee import CRUDEmployee # Import cục bộ để tránh vòng lặp nếu cần
    
    employee = await CRUDEmployee.get_by_id(db, employee_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên có ID {employee_id}"
        )
    return employee

@router.put(
    "/{employee_id}",
    response_model=EmployeeOut,
    dependencies=[Depends(get_current_admin_user)] # Chỉ Admin mới được sửa
)
async def update_employee(
    employee_id: str,
    employee_update: EmployeeUpdate,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_admin_user)
):
    """
    Cập nhật thông tin nhân viên.
    """
    logger.info(f"Admin {current_user.user_id} cập nhật nhân viên {employee_id}")
    
    from app.crud.crud_employee import CRUDEmployee
    
    # Kiểm tra tồn tại
    existing_emp = await CRUDEmployee.get_by_id(db, employee_id)
    if not existing_emp:
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

    updated_emp = await CRUDEmployee.update(db, employee_id, employee_update)
    return updated_emp

@router.post(
    "/staff",
    response_model=EmployeeOut,
    status_code=status.HTTP_201_CREATED,
    # SỬA LỖI TẠI ĐÂY: Thay đổi người gác cổng
    dependencies=[Depends(get_current_user)] 
)
async def create_staff(
    request_data: CreateStaffRequest,
    db: aiomysql.Connection = Depends(get_db),
    # SỬA LỖI TẠI ĐÂY: Lấy user hiện tại (Admin hoặc Manager đều được)
    current_user: UserOut = Depends(get_current_user)
):
    """
    Tạo nhân viên kho hoặc Shipper.
    """
    employee_data = EmployeeCreate(
        full_name=request_data.full_name,
        email=request_data.email,
        phone=request_data.phone,
        role=request_data.role,
        dob=request_data.dob,
        warehouse_id=request_data.warehouse_id
    )
    
    return await EmployeeService.create_staff(
        db=db,
        employee_data=employee_data,
        username=request_data.username,
        password=request_data.password,
        vehicle_type=request_data.vehicle_type,
        current_user=current_user
    )

@router.get(
    "/", 
    response_model=List[EmployeeOut],
    dependencies=[Depends(get_current_user)] # Mở cho User login
)
async def get_all_employees(
    role: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None), # Nhận param từ frontend (nếu có)
    db: aiomysql.Connection = Depends(get_db),
    skip: int = Query(0),
    limit: int = Query(100),
    current_user: UserOut = Depends(get_current_user)
):
    """
    Lấy danh sách nhân viên.
    - Admin: Thấy hết (hoặc theo warehouse_id gửi lên).
    - Manager: Chỉ thấy nhân viên thuộc kho của mình (Service sẽ tự filter).
    """
    return await EmployeeService.get_all_employees(
        db=db, 
        skip=skip, 
        limit=limit, 
        role=role,
        warehouse_id=warehouse_id,
        current_user=current_user # Truyền user để check quyền
    )
    


@router.post(
    "/dispatch", 
    response_model=EmployeeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)]
)
async def create_dispatch(
    request_data: WarehouseManagerRequest,
    db: aiomysql.Connection = Depends(get_db),
    current_user: UserOut = Depends(get_current_admin_user)
):
    """
    Tạo mới một Dispatch (Nhân viên điều phối).
    """
    logger.info(f"Admin {current_user.user_id} đang tạo Dispatch mới: {request_data.username}")
    
    return await EmployeeService.create_dispatch(
        db=db,
        employee_data=request_data.employee_data,
        username=request_data.username,
        password=request_data.password
    )