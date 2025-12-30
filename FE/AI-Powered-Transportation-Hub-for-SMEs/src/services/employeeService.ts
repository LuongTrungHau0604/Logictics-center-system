import { apiClient } from './api';

// 1. Định nghĩa các Interface dữ liệu (giống Schema Backend)

// Dữ liệu trả về (Output)
export interface Employee {
  employee_id: string;
  full_name: string;
  dob?: string | null; // Date string "YYYY-MM-DD"
  role: string;        // "WAREHOUSE_MANAGER", "SHIPPER", "STAFF"...
  phone: string;
  email: string;
  status: string;      // "ACTIVE", "INACTIVE"
  user_id?: string | null;
  warehouse_id?: string | null;
  created_at: string;
}

// Dữ liệu tạo mới nhân viên (Input cơ bản)
export interface EmployeeCreate {
  full_name: string;
  dob?: string;
  role: string;
  phone: string;
  email: string;
  warehouse_id?: string;
}

// Dữ liệu cập nhật nhân viên
export interface EmployeeUpdate {
  full_name?: string;
  dob?: string;
  role?: string;
  phone?: string;
  status?: string;
  warehouse_id?: string;
}

// Dữ liệu Request body để tạo Warehouse Manager (Gộp User + Employee)
export interface WarehouseManagerRequest {
  username: string;
  password: string;
  employee_data: EmployeeCreate;
}

export interface CreateStaffRequest {
  username: string;
  password: string;
  full_name: string;
  email: string;
  phone: string;
  role: 'WAREHOUSE_STAFF' | 'SHIPPER';
  warehouse_id: string;
  dob?: string;
  vehicle_type?: 'MOTORBIKE' | 'TRUCK' | 'VAN';
}

// 2. Service Object
export const employeeService = {
  
  
  
  
  // --- A. LẤY DANH SÁCH (GET) ---

  // Lấy danh sách nhân viên (Có lọc theo Role, Phân trang, Chống cache)
  

  // Lấy chi tiết một nhân viên
  getEmployeeById: async (employeeId: string) => {
    const response = await apiClient.get<Employee>(`/employees/${employeeId}`, {
      params: { _t: Date.now() }
    });
    return response.data;
  },

  // --- B. TẠO MỚI (POST) ---

  // Tạo Quản lý kho (Tạo cả User login + Employee info)
  createWarehouseManager: async (data: WarehouseManagerRequest) => {
    const response = await apiClient.post<Employee>('/employees/warehouse-manager', data);
    return response.data;
  },

  createStaff: async (data: CreateStaffRequest) => {
    const response = await apiClient.post<Employee>('/employees/staff', data);
    return response.data;
  },

  // Lấy danh sách (hỗ trợ filter warehouse)
  getAllEmployees: async (role?: string, warehouseId?: string, page: number = 1, limit: number = 10) => {
    const skip = (page - 1) * limit;
    const params: any = { skip, limit, _t: Date.now() };
    
    if (role && role !== 'ALL') params.role = role;
    if (warehouseId) params.warehouse_id = warehouseId;

    const response = await apiClient.get<Employee[]>('/employees/', { params });
    return response.data;
  },
  // --- C. CẬP NHẬT (PUT) ---

  // Cập nhật thông tin nhân viên
  updateEmployee: async (employeeId: string, data: EmployeeUpdate) => {
    const response = await apiClient.put<Employee>(`/employees/${employeeId}`, data);
    return response.data;
  },

  // employeeService.ts - Thêm method

  createDispatch: async (data: WarehouseManagerRequest) => {
    const response = await apiClient.post<Employee>('/employees/dispatch', data);
    return response.data;
  }
};