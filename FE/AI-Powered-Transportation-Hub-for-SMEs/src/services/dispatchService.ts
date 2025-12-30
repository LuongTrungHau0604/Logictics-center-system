import { aiServiceClient } from './api';

// --- Interfaces (Giữ nguyên các interface hiển thị) ---
export interface DispatchOrder {
  id: string;
  code: string;
  from_location: string;
  to_location: string;
  status: string;
  priority: string;
  total_distance: number;
  total_legs: number;
  created_at: string;
}

export interface OrderJourneyLeg {
  id: number;
  sequence: number;
  leg_type: 'PICKUP' | 'TRANSFER' | 'DELIVERY';
  status: string;
  assigned_shipper_id: string | null;
  origin_warehouse_id: string | null;
  destination_warehouse_id: string | null;
  origin_sme_id?: string | null;
  destination_is_receiver?: boolean;
  estimated_distance: number;
  created_at: string;
}

// --- ⚠️ UPDATE: Interface này đã thay đổi để khớp với Backend mới ---
// Backend trả về: { status, summary, processed_count, details }
export interface OptimizationResponse {
  status: string;
  summary: string;          // Trước đây là agent_report
  processed_count: number;  // Trước đây là orders_processed
  details: any[];
}

// Tăng timeout lên 10 phút vì chạy Auto-Pilot toàn hệ thống sẽ lâu hơn chạy đơn lẻ
const LONG_TIMEOUT = 10 * 60 * 1000;

export const dispatchService = {
  // --- 1. Lấy dữ liệu hiển thị (Giữ nguyên) ---
  async getDispatchSummary(): Promise<DispatchOrder[]> {
    try {
      const response = await aiServiceClient.get('/dispatch/summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching dispatch summary:', error);
      throw error;
    }
  },

  async getOrderDetails(orderId: string): Promise<OrderJourneyLeg[]> {
    try {
      const response = await aiServiceClient.get(`/dispatch/orders/${orderId}/legs`);
      return response.data;
    } catch (error) {
      console.error('Error fetching order details:', error);
      throw error;
    }
  },

  // --- 2. 🚀 THE MASTER BUTTON (Auto-Pilot Mode) ---
  // Hàm này sẽ kích hoạt chế độ tự động quét toàn bộ hệ thống
  // Bạn chỉ cần gắn hàm này vào nút "Tự động điều phối" ở Frontend
  async runAutoPilot(): Promise<OptimizationResponse> {
    try {
      const response = await aiServiceClient.post(
        'ai-batch-optimizer/ai/optimize', // Endpoint chung duy nhất
        { target_id: null }, // Gửi null để kích hoạt chế độ Global Scan
        { timeout: LONG_TIMEOUT }
      );
      return response.data;
    } catch (error) {
      console.error('Error running Auto-Pilot:', error);
      throw error;
    }
  },

  // --- 3. Targeted Action (Dành cho việc Debug hoặc chạy lẻ tẻ nếu cần) ---
  // Vẫn gọi endpoint /ai/optimize nhưng có truyền ID cụ thể
  async runTargetedOptimization(targetId: string): Promise<OptimizationResponse> {
    try {
      const response = await aiServiceClient.post(
        '/ai/optimize',
        { target_id: targetId }, // Gửi ID cụ thể (Hub ID hoặc Area ID)
        { timeout: LONG_TIMEOUT }
      );
      return response.data;
    } catch (error) {
      console.error(`Error optimizing target ${targetId}:`, error);
      throw error;
    }
  }
};