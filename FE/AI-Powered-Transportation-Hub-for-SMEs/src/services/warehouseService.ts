import { aiServiceClient } from './api'; // Sử dụng chung client với các service khác (đã cấu hình đúng Port/Token)

// ✅ Response types
export interface Warehouse {
  warehouse_id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  capacity_limit: number;
  current_load: number;
  status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE';
  area_id?: string;
  type?: 'HUB' | 'SATELLITE' | 'LOCAL_DEPOT';
  manager?: string;
  contact_phone?: string;
}

export interface CreateWarehouseRequest {
  name: string;
  address: string;
  capacity_limit: number;
  area_id: string;
  type: string;
  manager?: string;
  contact_phone?: string;
}

export interface WarehouseStats {
  warehouse_id: string;
  name: string;
  capacity_limit: number;
  current_load: number;
  utilization_rate: number;
  available_capacity: number;
  status: string;
}

export interface WarehouseUsageSyncResponse {
  total_warehouses_scanned: number;
  warehouses_updated: Array<{
    warehouse_id: string;
    warehouse_name: string;
    old_load: number;
    new_load: number;
    capacity_limit: number;
  }>;
  total_orders_counted: number;
  timestamp: string;
}

export interface WarehouseDetailedStats {
  warehouse_id: string;
  warehouse_name: string;
  capacity_limit: number;
  current_load: number;
  utilization_rate: number;
  orders_breakdown: {
    total: number;
    waiting_for_transfer: number;
    transfer_in_progress: number;
  };
}

export const warehouseService = {
  // Get all warehouses
  async getAllWarehouses(): Promise<Warehouse[]> {
    // apiClient đã có base URL là /api/v1, nên chỉ cần gọi /warehouses
    const response = await aiServiceClient.get<Warehouse[]>('/warehouses/'); 
    return response.data;
  },

  // Get warehouse by ID (Đây là hàm quan trọng đang bị lỗi)
  async getWarehouseById(warehouseId: string): Promise<Warehouse> {
    const response = await aiServiceClient.get<Warehouse>(`/warehouses/${warehouseId}`);
    return response.data;
  },

  // Create new warehouse (Admin only)
  async createWarehouse(data: CreateWarehouseRequest): Promise<Warehouse> {
    const response = await aiServiceClient.post<Warehouse>('/warehouses/', data);
    return response.data;
  },

  // Update warehouse (Admin only)
  async updateWarehouse(
    warehouseId: string,
    data: Partial<CreateWarehouseRequest>
  ): Promise<Warehouse> {
    const response = await aiServiceClient.put<Warehouse>(`/warehouses/${warehouseId}`, data);
    return response.data;
  },

  // Delete warehouse (Admin only)
  async deleteWarehouse(warehouseId: string): Promise<void> {
    await aiServiceClient.delete(`/warehouses/${warehouseId}`);
  },

  // Get warehouse stats
  async getWarehouseStats(warehouseId: string): Promise<WarehouseStats> {
    const response = await aiServiceClient.get<WarehouseStats>(`/warehouses/${warehouseId}/stats`);
    return response.data;
  },

  // Sync warehouse usage từ completed pickup orders
  async syncWarehouseUsage(): Promise<WarehouseUsageSyncResponse> {
    const response = await aiServiceClient.post<WarehouseUsageSyncResponse>('/warehouses/sync-usage');
    return response.data;
  },

  // Get detailed stats cho một warehouse
  async getDetailedStats(warehouseId: string): Promise<WarehouseDetailedStats> {
    const response = await aiServiceClient.get<WarehouseDetailedStats>(`/warehouses/${warehouseId}/stats`);
    return response.data;
  },
};