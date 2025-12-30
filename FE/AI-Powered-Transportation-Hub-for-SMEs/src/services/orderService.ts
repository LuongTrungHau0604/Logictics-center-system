// src/services/orderService.ts

import { orderApiClient } from './api';

// Interface cho order response (khớp với schema backend OrderOut)
export interface OrderResponse {
  order_id: string;
  order_code: string;
  sme_id: string;
  barcode_id: string;
  receiver_name: string;
  receiver_phone: string;
  receiver_address: string;
  receiver_latitude: number;
  receiver_longitude: number;
  weight: number;
  dimensions?: string;
  note?: string;
  status: string; // PENDING, IN_TRANSIT, etc.
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

// Interface cho update request (các trường optional)
export interface UpdateOrderRequest {
  receiver_name?: string;
  receiver_phone?: string;
  receiver_address?: string;
  weight?: number;
  note?: string;
  dimensions?: string;
}

// Interface cho create request (bắt buộc các trường quan trọng)
export interface CreateOrderRequest {
  receiver_name: string;
  receiver_phone: string;
  receiver_address: string;
  weight: number;
  dimensions?: string;
  note?: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

class OrderService {
  /**
   * Tạo đơn hàng mới
   */
  async createOrder(orderData: CreateOrderRequest): Promise<OrderResponse> {
    try {
      console.log('📦 Creating order:', orderData);
      
      const response = await orderApiClient.post<OrderResponse>(
        '/orders/create', 
        orderData
      );
      
      console.log('✅ Order created successfully:', response.data);
      return response.data;
      
    } catch (error: any) {
      console.error('❌ Order creation failed:', error);
      this.handleError(error); // Helper xử lý lỗi chung
      throw error; // Để typescript biết hàm throw
    }
  }

  /**
   * Get all orders cho SME hiện tại
   */
  async getOrders(): Promise<OrderResponse[]> {
    try {
      console.log('📤 Fetching orders...');
      const response = await orderApiClient.get<OrderResponse[]>('/orders');
      console.log('✅ Fetched orders:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to fetch orders:', error);
      if (error.response?.status === 404) return [];
      throw new Error('Failed to fetch orders');
    }
  }

  /**
   * Get order by ID
   */
  async getOrderById(orderId: string): Promise<OrderResponse> {
    try {
      const response = await orderApiClient.get<OrderResponse>(`/orders/${orderId}`);
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to fetch order:', error);
      throw new Error('Failed to fetch order details');
    }
  }

  /**
   * Get barcode cho order
   */
  /**
   * Get barcode image cho order (Base64 string)
   */
  // src/services/orderService.ts

async getOrderBarcode(orderId: string): Promise<string> {
    try {
      // 1. Thử gọi endpoint hiện tại (nếu bạn đã fix Backend đúng router)
      // Hoặc nếu endpoint nằm ở router barcode thì đổi '/orders' thành '/barcodes'
      const response = await orderApiClient.get<any>(`/orders/${orderId}/barcode`); 
      
      // LOGIC XỬ LÝ (như cũ)
      if (response.data?.image) return response.data.image;
      
      // --- BỔ SUNG: FALLBACK THÔNG MINH ---
      // Nếu Backend trả về metadata (code_value) nhưng thiếu image (do lỗi Pydantic hoặc DB null)
      // Ta sẽ gọi endpoint tạo ảnh trực tiếp từ code_value
      if (response.data?.code_value) {
          console.warn("⚠️ Missing image, trying to generate from code_value...");
          const codeValue = response.data.code_value;
          // Gọi endpoint: @router.get("/{code_value}/image") trong barcode.py
          // Lưu ý: check prefix router của barcode.py (thường là /barcodes)
          const imgResponse = await orderApiClient.get<any>(`/barcodes/${codeValue}/image`); 
          if (imgResponse.data?.image) {
              return imgResponse.data.image;
          }
      }

      console.warn("⚠️ Backend returned 200 but missing 'image' field:", response.data);
      return ""; 

    } catch (error: any) {
      console.error('❌ Failed to fetch barcode:', error);
      return ""; 
    }
}
  /**
   * Update order by ID (Chỉ khi PENDING)
   */
  async updateOrder(orderId: string, updateData: UpdateOrderRequest): Promise<OrderResponse> {
    try {
      console.log(`✏️ Updating order ${orderId}...`);
      const response = await orderApiClient.put<OrderResponse>(`/orders/${orderId}`, updateData);
      console.log('✅ Order updated:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Failed to update order:', error);
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Cancel order by ID (Chỉ khi PENDING)
   */
  async cancelOrder(orderId: string): Promise<void> {
    try {
      console.log(`❌ Cancelling order ${orderId}...`);
      await orderApiClient.put(`/orders/${orderId}/cancel`);
      console.log('✅ Order cancelled successfully');
    } catch (error: any) {
      console.error('❌ Failed to cancel order:', error);
      this.handleError(error);
    }
  }

  /**
   * Test connection to order service
   */
  async testConnection(): Promise<boolean> {
    try {
      await orderApiClient.get('/health');
      console.log('🔗 Order service connection successful');
      return true;
    } catch (error) {
      console.error('❌ Order service connection failed:', error);
      return false;
    }
  }

  /**
   * Helper xử lý lỗi chung để giảm lặp code
   */
  private handleError(error: any): void {
    if (error.response) {
      const detail = error.response.data?.detail || 'Operation failed';
      const status = error.response.status;

      switch (status) {
        case 400: throw new Error(detail); // Lỗi validation hoặc logic nghiệp vụ (vd: status != PENDING)
        case 401: throw new Error('Please login to continue.');
        case 403: throw new Error('Permission denied.');
        case 404: throw new Error('Order not found.');
        case 500: throw new Error('Server error. Please try again later.');
        default: throw new Error(detail);
      }
    } else if (error.request) {
      throw new Error('Network error - Unable to connect to service');
    } else {
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
}

// Export singleton instance
export const orderService = new OrderService();
export default orderService;