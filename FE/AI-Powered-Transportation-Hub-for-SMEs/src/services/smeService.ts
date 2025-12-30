import { apiClient } from './api';

export interface SME {
  sme_id: string;
  business_name: string;
  tax_code: string;
  address: string;
  contact_phone: string;
  email: string;
  website?: string;
  area_id?: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
  status: 'PENDING' | 'ACTIVE' | 'INACTIVE';
}
export interface UpdateSMEProfileRequest {
  business_name?: string;
  tax_code?: string;
  address?: string;
  contact_phone?: string;
  email?: string;
  website?: string;
}

export const smeService = {
  // 1. Lấy danh sách theo trạng thái
  getSmesByStatus: async (status: 'PENDING' | 'ACTIVE' | 'INACTIVE', page: number = 1, limit: number = 10) => {
    const skip = (page - 1) * limit;
    
    const response = await apiClient.get<SME[]>(`/sme/status/${status}`, {
      params: { 
        skip, 
        limit,
        _t: Date.now() // <--- THÊM DÒNG NÀY: Luôn tạo param mới để tránh Cache
      }
    });
    return response.data;
  },

  // 2. Lấy TẤT CẢ doanh nghiệp
  getAllSmes: async (page: number = 1, limit: number = 10) => {
    const skip = (page - 1) * limit;
    const response = await apiClient.get<SME[]>('/sme/', {
      params: { 
        skip, 
        limit,
        _t: Date.now() // <--- THÊM DÒNG NÀY
      }
    });
    return response.data;
  },

  // 3. Update status (Giữ nguyên)
  updateSmeStatus: async (smeId: string, newStatus: 'ACTIVE' | 'INACTIVE') => {
    const response = await apiClient.put<SME>(`/sme/${smeId}/status`, null, {
      params: { new_status: newStatus }
    });
    return response.data;
  },


  getMyProfile: async () => {
    const response = await apiClient.get<SME>('/sme/me/profile');
    return response.data;
  },

  // Cập nhật thông tin
  updateProfile: async (data: UpdateSMEProfileRequest) => {
    const response = await apiClient.put<SME>('/sme/me/profile', data);
    return response.data;
  }
};