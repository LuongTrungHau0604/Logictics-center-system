// src/services/journeyLegService.ts
import { aiServiceClient } from './api';



export interface JourneyLeg {
  id: number;
  sequence: number;
  leg_type: 'PICKUP' | 'TRANSFER' | 'DELIVERY';
  status: string;
  assigned_shipper_id: string | null;
  // --- THÊM DÒNG NÀY ---
  shipper_full_name?: string | null;
  // ---------------------
  origin_warehouse_id: string | null;
  destination_warehouse_id: string | null;
  estimated_distance?: number;
  created_at: string;
  updated_at?: string;
}

export interface Order {
  order_id: string;
  order_code: string;
  status: string;
  sme_id: string;
  receiver_name: string;
  receiver_address: string;
  created_at: string;
  area_id?: string;
}

export interface Shipper {
  shipper_id: string;
  full_name: string; // Backend trả về full_name từ bảng Employee
  vehicle_type: string;
  status: string;
  area_id: string;
  rating: number;
}

// Payload gửi lên Backend để tạo hành trình 3 chặng
export interface AssignShipperRequest {
  order_id: string;
  shipper_id: string;          // Shipper lấy hàng (Pickup)
  destination_hub_id: string;  // Kho Hub đích (thay cho destination_warehouse_id)
  destination_satellite_id?: string; // (Optional) Kho vệ tinh
}

// Response trả về từ API assign-shipper
export interface AssignShipperResponse {
  success: boolean;
  order_id: string;
  legs: any[]; // Chi tiết 3 legs vừa tạo
}

export const journeyLegService = {
  // 1. Lấy danh sách đơn hàng PENDING
  async getPendingOrders(): Promise<Order[]> {
    try {
      const response = await aiServiceClient.get('/dispatch/pending-orders');
      return response.data;
    } catch (error) {
      console.error('Error fetching pending orders:', error);
      throw error;
    }
  },

  // 2. Lấy danh sách shipper theo area
  async getShippersByArea(areaId: string): Promise<Shipper[]> {
    try {
      const response = await aiServiceClient.get(`/dispatch/shippers/by-area/${areaId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching shippers:', error);
      throw error;
    }
  },

  // 3. Gán shipper cho order (Gọi logic tạo 3 chặng của DispatchService)
  async assignShipperToOrder(data: AssignShipperRequest): Promise<AssignShipperResponse> {
    try {
      console.log('🔍 Sending assign request:', data);
      const response = await aiServiceClient.post('/dispatch/assign-shipper', data);
      console.log('✅ Assign response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Assign shipper error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      throw error;
    }
  },

  // 4. Lấy chi tiết các chặng của đơn hàng
  async getOrderLegs(orderId: string): Promise<JourneyLeg[]> {
    try {
      const response = await aiServiceClient.get(`/dispatch/orders/${orderId}/legs`);
      return response.data;
    } catch (error) {
      console.error('Error fetching order legs:', error);
      throw error;
    }
  },

  // 5. Cập nhật journey leg (nếu cần sửa thủ công sau này)
  async updateJourneyLeg(legId: number, data: Partial<JourneyLeg>): Promise<JourneyLeg> {
    const response = await aiServiceClient.put(`/dispatch/legs/${legId}`, data);
    return response.data;
  },

  // 6. Xóa journey leg
  async deleteJourneyLeg(legId: number): Promise<void> {
    await aiServiceClient.delete(`/dispatch/legs/${legId}`);
  },


  async getAllOrders(): Promise<Order[]> {
    try {
      const response = await aiServiceClient.get('/dispatch/all-orders');
      return response.data;
    } catch (error) {
      console.error('Error fetching all orders:', error);
      throw error;
    }
  }
};