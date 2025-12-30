import axios from 'axios';

// Lấy URL từ biến môi trường
const API_BASE_URL = import.meta.env.VITE_AI_AGENT_SERVICE_URL || 'http://localhost:8002';

// Interface cho Area
export interface Area {
  area_id: string;
  name: string;
  type: 'CITY' | 'DISTRICT' | 'REGION' | 'CUSTOM';
  status: 'ACTIVE' | 'INACTIVE';
  description?: string;
  radius_km: number;
  center_latitude: number;
  center_longitude: number;
  created_at?: string;
}

// Interface cho Create/Update
export interface CreateAreaRequest {
  name: string;
  type: string;
  status: string;
  description?: string;
  radius_km: number;
  center_latitude: number;
  center_longitude: number;
}

export interface UpdateAreaRequest extends Partial<CreateAreaRequest> {}

// Axios instance
const areaAPI = axios.create({
  baseURL: `${API_BASE_URL}/areas`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token interceptor
areaAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const areaService = {
  // GET ALL
  async getAllAreas(areaType?: string): Promise<Area[]> {
    const params: any = {};
    if (areaType) params.area_type = areaType;
    
    try {
      const response = await areaAPI.get('/', { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching areas:", error);
      return [];
    }
  },

  // GET BY ID
  async getAreaById(areaId: string): Promise<Area | null> {
    try {
      const response = await areaAPI.get(`/${areaId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching area ${areaId}:`, error);
      return null;
    }
  },

  // CREATE
  async createArea(data: CreateAreaRequest): Promise<Area> {
    const response = await areaAPI.post('/', data);
    return response.data;
  },

  // UPDATE
  async updateArea(areaId: string, data: UpdateAreaRequest): Promise<Area> {
    const response = await areaAPI.put(`/${areaId}`, data);
    return response.data;
  },

  // DELETE
  async deleteArea(areaId: string): Promise<void> {
    await areaAPI.delete(`/${areaId}`);
  }
};