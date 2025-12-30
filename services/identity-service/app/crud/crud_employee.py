from venv import logger
import aiomysql
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

class CRUDEmployee:
    
    @staticmethod
    def generate_employee_id() -> str:
        """Tạo ID nhân viên, ví dụ: EMP-UUID"""
        return f"EMP-{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    async def get_by_id(db: aiomysql.Connection, employee_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin nhân viên theo ID"""
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM employees WHERE employee_id = %s", 
                (employee_id,)
            )
            return await cursor.fetchone()

    @staticmethod
    async def get_by_user_id(db: aiomysql.Connection, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin Employee dựa trên User ID (từ token đăng nhập).
        """
        try:
            query = "SELECT * FROM employees WHERE user_id = %s"
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (user_id,))
                result = await cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"❌ Error getting employee by user_id: {e}")
            return None

    @staticmethod
    async def get_by_email(db: aiomysql.Connection, email: str) -> Optional[Dict[str, Any]]:
        """Kiểm tra email đã tồn tại trong bảng employees chưa"""
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM employees WHERE email = %s", 
                (email,)
            )
            return await cursor.fetchone()

    @staticmethod
    async def create(
        db: aiomysql.Connection, 
        obj_in: EmployeeCreate, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Tạo mới nhân viên.
        Lưu ý: user_id thường được lấy sau khi tạo tài khoản ở bảng User.
        """
        employee_id = CRUDEmployee.generate_employee_id()
        created_at = datetime.utcnow()
        status = "ACTIVE" # Mặc định khi tạo là Active

        query = """
            INSERT INTO employees (
                employee_id, full_name, dob, role, phone, 
                email, status, user_id, created_at, warehouse_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            employee_id, 
            obj_in.full_name, 
            obj_in.dob, 
            obj_in.role, 
            obj_in.phone, 
            obj_in.email, 
            status, 
            user_id, 
            created_at, 
            obj_in.warehouse_id
        )

        try:
            async with db.cursor() as cursor:
                await cursor.execute(query, params)
                # Lưu ý: Transaction commit thường được gọi ở tầng Service hoặc Controller
            
            # Trả về thông tin vừa tạo (giả lập select lại để nhanh)
            return {
                "employee_id": employee_id,
                "full_name": obj_in.full_name,
                "dob": obj_in.dob,
                "role": obj_in.role,
                "phone": obj_in.phone,
                "email": obj_in.email,
                "status": status,
                "user_id": user_id,
                "created_at": created_at,
                "warehouse_id": obj_in.warehouse_id
            }
        except Exception as e:
            print(f"❌ Error creating employee: {e}")
            return None

    @staticmethod
    async def get_multi(
        db: aiomysql.Connection, 
        skip: int = 0, 
        limit: int = 100,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách nhân viên (có phân trang và lọc theo Role)"""
        query = "SELECT * FROM employees"
        params = []

        if role_filter:
            query += " WHERE role = %s"
            params.append(role_filter)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])

        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, tuple(params))
            return await cursor.fetchall()

    @staticmethod
    async def get_multi_with_warehouse(
        db: aiomysql.Connection, 
        skip: int = 0, 
        limit: int = 100, 
        role_filter: str = None,
        warehouse_filter: str = None # <-- QUAN TRỌNG: Filter theo kho
    ) -> List[Dict[str, Any]]:
        """
        Lấy danh sách nhân viên có phân trang và lọc.
        """
        try:
            query = "SELECT * FROM employees WHERE 1=1"
            params = []

            if role_filter:
                query += " AND role = %s"
                params.append(role_filter)
            
            # --- THÊM LOGIC LỌC KHO ---
            if warehouse_filter:
                query += " AND warehouse_id = %s"
                params.append(warehouse_filter)
            # --------------------------

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, tuple(params))
                results = await cursor.fetchall()
            
            return results
        except Exception as e:
            logger.error(f"❌ Error fetching employees: {e}")
            return []
    @staticmethod
    async def update(
        db: aiomysql.Connection, 
        employee_id: str, 
        obj_in: EmployeeUpdate
    ) -> Optional[Dict[str, Any]]:
        """Cập nhật thông tin nhân viên (Dynamic Update)"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if not update_data:
            return await CRUDEmployee.get_by_id(db, employee_id)

        set_clauses = []
        params = []
        
        for field, value in update_data.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)
        
        params.append(employee_id)
        query = f"UPDATE employees SET {', '.join(set_clauses)} WHERE employee_id = %s"

        async with db.cursor() as cursor:
            await cursor.execute(query, tuple(params))
            # Service sẽ lo commit
        
        return await CRUDEmployee.get_by_id(db, employee_id)