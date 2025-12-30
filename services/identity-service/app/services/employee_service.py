import aiomysql
import logging
from fastapi import HTTPException, status
from app.crud.crud_employee import CRUDEmployee
from app.crud.crud_user import CRUDUser  # Import CRUDUser
from app.crud.crud_warehouse import CRUDWarehouse
from app.crud.crud_shipper import CRUDShipper
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.core.security import get_password_hash
from datetime import datetime
from app.schemas.user import UserOut
import uuid
logger = logging.getLogger(__name__)

class EmployeeService:
    """
    Logic nghiệp vụ cho Employee.
    """

    @staticmethod
    async def create_warehouse_manager(
        db: aiomysql.Connection,
        employee_data: EmployeeCreate,
        username: str,
        password: str
    ) -> EmployeeOut:
        """
        Tạo một Quản lý kho (Warehouse Manager).
        Quy trình: Validations -> Start Transaction -> Create User -> Create Employee -> Commit.
        """
        # 1. Validate
        # Kiểm tra email trong bảng Employee
        if await CRUDEmployee.get_by_email(db, employee_data.email):
            raise HTTPException(status_code=400, detail="Email nhân viên đã tồn tại")
        
        # Kiểm tra email trong bảng User
        if await CRUDUser.get_by_email(db, employee_data.email):
            raise HTTPException(status_code=400, detail="Email User đã tồn tại")

        try:
            # Bắt đầu Transaction
            await db.begin()

            # 2. Chuẩn bị dữ liệu User
            user_id = CRUDUser.generate_user_id()
            hashed_pw = get_password_hash(password)
            
            user_in = {
                "user_id": user_id,
                "username": username,
                "email": employee_data.email,
                "phone": employee_data.phone,
                "role": "WAREHOUSE_MANAGER", # Role login
                "password_hash": hashed_pw,
                "created_at": datetime.utcnow(),
                "sme_id": None # Nhân viên hệ thống không thuộc SME
            }
            
            # --- BƯỚC QUAN TRỌNG: TẠO USER TRƯỚC ---
            # Phải insert vào bảng 'user' trước để thỏa mãn khóa ngoại
            created_user = await CRUDUser.create_user(db, user_in)
            
            if not created_user:
                raise Exception("Không thể tạo bản ghi User")
            
            logger.info(f"✅ Đã tạo User {user_id} cho Warehouse Manager")

            # 3. Tạo Employee Record
            # Gán cứng role trong bảng employee và liên kết user_id
            employee_data.role = "WAREHOUSE_MANAGER"
            
            # Insert vào bảng 'employees' với user_id vừa tạo ở trên
            new_employee = await CRUDEmployee.create(db, employee_data, user_id)
            
            if not new_employee:
                raise Exception("Không thể tạo bản ghi Employee")

            logger.info(f"✅ Đã tạo Employee {new_employee['employee_id']}")

            # 4. Commit Transaction (Lưu tất cả vào DB)
            await db.commit()
            
            return EmployeeOut(**new_employee)

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback() # Rollback nếu có bất kỳ lỗi nào xảy ra
            logger.error(f"❌ Lỗi tạo Warehouse Manager: {e}")
            # Kiểm tra lỗi trùng lặp Username nếu CRUDUser chưa bắt
            if "Duplicate entry" in str(e) and "username" in str(e):
                 raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
            
            raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

    
    @staticmethod
    async def create_staff(
        db: aiomysql.Connection,
        employee_data: EmployeeCreate,
        username: str,
        password: str,
        current_user: UserOut, # Thông tin người đang thực hiện tạo
        vehicle_type: str = "MOTORBIKE"
    ) -> EmployeeOut:
        """
        Tạo nhân viên (Warehouse Staff hoặc Shipper).
        """
        
        # --- 1. PHÂN QUYỀN & GÁN KHO TỰ ĐỘNG ---
        # Lấy thông tin nhân viên của người tạo (Manager/Admin)
        creator_emp = await CRUDEmployee.get_by_user_id(db, current_user.user_id)
        
        # Nếu người tạo là WAREHOUSE_MANAGER, bắt buộc nhân viên mới phải thuộc kho của họ
        if creator_emp and creator_emp.get('role') == 'WAREHOUSE_MANAGER':
            manager_warehouse_id = creator_emp.get('warehouse_id')
            if not manager_warehouse_id:
                raise HTTPException(status_code=403, detail="Manager account is not assigned to any warehouse.")
            
            # Ghi đè warehouse_id bằng kho của Manager
            employee_data.warehouse_id = manager_warehouse_id
            logger.info(f"🔒 Auto-assigning staff to Manager's warehouse: {manager_warehouse_id}")

        # --- 2. VALIDATE DATA ---
        if await CRUDEmployee.get_by_email(db, employee_data.email):
            raise HTTPException(status_code=400, detail="Email nhân viên đã tồn tại")
        
        if await CRUDUser.get_by_email(db, employee_data.email):
            raise HTTPException(status_code=400, detail="Email User đã tồn tại")

        if not employee_data.warehouse_id:
             raise HTTPException(status_code=400, detail="Warehouse ID is required")
        
        # Lấy thông tin kho (để lấy area_id cho shipper)
        warehouse = await CRUDWarehouse.get_by_id(db, employee_data.warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="Kho hàng không tồn tại")

        try:
            await db.begin() # Bắt đầu Transaction

            # --- 3. TẠO USER ACCOUNT ---
            user_id = CRUDUser.generate_user_id()
            hashed_pw = get_password_hash(password)
            
            user_in = {
                "user_id": user_id,
                "username": username,
                "email": employee_data.email,
                "phone": employee_data.phone,
                "role": employee_data.role, # Role login khớp với role nhân viên
                "password_hash": hashed_pw,
                "created_at": datetime.utcnow(),
                "sme_id": None 
            }
            await CRUDUser.create_user(db, user_in)

            # --- 4. TẠO EMPLOYEE RECORD ---
            new_employee = await CRUDEmployee.create(db, employee_data, user_id)
            if not new_employee:
                raise Exception("Failed to create employee record")

            # --- 5. TẠO SHIPPER RECORD (Nếu cần) ---
            if employee_data.role == "SHIPPER":
                shipper_id = f"SHP-{uuid.uuid4().hex[:8].upper()}"
                
                # Lấy area_id từ kho (Sửa lỗi subscriptable bằng cách dùng dot notation)
                area_id_val = warehouse.area_id 
                
                shipper_data = {
                    "shipper_id": shipper_id,
                    "employee_id": new_employee["employee_id"],
                    "vehicle_type": vehicle_type,
                    "status": "ONLINE",  # Mặc định là ONLINE khi tạo
                    "area_id": area_id_val, # Gán khu vực hoạt động theo kho
                    "rating": 5.0, 
                    "created_at": datetime.utcnow()
                }
                await CRUDShipper.create(db, shipper_data)
                logger.info(f"🚚 Shipper {shipper_id} created for Area {area_id_val}")

            await db.commit()
            return EmployeeOut(**new_employee)

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error creating staff: {e}")
            if "Duplicate entry" in str(e) and "username" in str(e):
                 raise HTTPException(status_code=400, detail="Username already exists")
            raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")

    @staticmethod
    async def get_all_employees(
        db: aiomysql.Connection, 
        current_user: UserOut,
        skip: int = 0, 
        limit: int = 100,
        role: str = None,
        warehouse_id: str = None 
    ):
        # Logic phân quyền xem danh sách
        creator_emp = await CRUDEmployee.get_by_user_id(db, current_user.user_id)
        
        final_warehouse_id = warehouse_id
        # Nếu là Manager, chỉ được xem nhân viên kho mình
        if creator_emp and creator_emp.get('role') == 'WAREHOUSE_MANAGER':
            final_warehouse_id = creator_emp.get('warehouse_id')

        await db.commit()
        return await CRUDEmployee.get_multi_with_warehouse(
            db, skip, limit, 
            role_filter=role, 
            warehouse_filter=final_warehouse_id
        )
        
    # employee_service.py - Thêm method mới hoặc cập nhật create_staff

    @staticmethod
    async def create_dispatch(
        db: aiomysql.Connection,
        employee_data: EmployeeCreate,
        username: str,
        password: str
    ) -> EmployeeOut:
        """
        Tạo nhân viên Điều phối (DISPATCH).
        Tương tự Warehouse Manager nhưng role là DISPATCH.
        """
        # 1. Validate
        if await CRUDEmployee.get_by_email(db, employee_data.email):
            raise HTTPException(status_code=400, detail="Email nhân viên đã tồn tại")
        
        if await CRUDUser.get_by_email(db, employee_data.email):
            raise HTTPException(status_code=400, detail="Email User đã tồn tại")

        try:
            await db.begin()

            # 2. Tạo User
            user_id = CRUDUser.generate_user_id()
            hashed_pw = get_password_hash(password)
            
            user_in = {
                "user_id": user_id,
                "username": username,
                "email": employee_data.email,
                "phone": employee_data.phone,
                "role": "DISPATCH",
                "password_hash": hashed_pw,
                "created_at": datetime.utcnow(),
                "sme_id": None
            }
            
            created_user = await CRUDUser.create_user(db, user_in)
            
            if not created_user:
                raise Exception("Không thể tạo bản ghi User")
            
            logger.info(f"✅ Đã tạo User {user_id} cho Dispatch")

            # 3. Tạo Employee Record
            employee_data.role = "DISPATCH"
            new_employee = await CRUDEmployee.create(db, employee_data, user_id)
            
            if not new_employee:
                raise Exception("Không thể tạo bản ghi Employee")

            logger.info(f"✅ Đã tạo Employee Dispatch {new_employee['employee_id']}")

            await db.commit()
            
            return EmployeeOut(**new_employee)

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Lỗi tạo Dispatch: {e}")
            if "Duplicate entry" in str(e) and "username" in str(e):
                raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
            
            raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
    