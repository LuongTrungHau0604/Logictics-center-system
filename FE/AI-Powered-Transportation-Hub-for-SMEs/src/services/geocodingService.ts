import axios from 'axios';

// Lấy URL từ biến môi trường (Giống areaService)
const API_BASE_URL = import.meta.env.VITE_AI_AGENT_SERVICE_URL || 'http://localhost:8002';

// Interface cho Suggestion từ Autocomplete
export interface AddressSuggestion {
  place_id: string;
  description: string; // Hoặc 'structured_formatting.main_text' tùy vào response của Goong/Google
  main_text?: string;
  secondary_text?: string;
}

export interface GeocodingResponse {
  latitude: float;
  longitude: float;
  address?: string;
  is_valid: boolean;
  is_vietnam: boolean;
}

// Axios instance riêng hoặc dùng chung
const geoAPI = axios.create({
  baseURL: `${API_BASE_URL}`, // Lưu ý: Backend router của bạn prefix là gì? (VD: /api/v1). Ở đây tôi để root theo code mẫu.
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token interceptor (Nếu API geocoding cần bảo mật)
geoAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const geocodingService = {
  // 1. Gợi ý địa chỉ (Autocomplete)
  async getSuggestions(query: string): Promise<AddressSuggestion[]> {
    if (!query) return [];
    try {
      // Backend: @router.get("/autocomplete")
      const response = await geoAPI.get('/geocoding/autocomplete', { 
        params: { text: query } 
      });
      // Backend trả về: { suggestions: [...] }
      return response.data.suggestions || [];
    } catch (error) {
      console.error("Error fetching suggestions:", error);
      return [];
    }
  },

  // 2. Lấy tọa độ chi tiết (Place Detail)
  async getPlaceDetail(placeId: string): Promise<GeocodingResponse | null> {
    try {
      // Backend: @router.post("/geocode/place-detail")
      // Body: { place_id: string }
      const response = await geoAPI.post('/geocoding/geocode/place-detail', { 
        place_id: placeId 
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching place detail:", error);
      return null;
    }
  }
};