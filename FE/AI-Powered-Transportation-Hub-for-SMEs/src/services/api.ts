// src/services/api.ts

import axios from 'axios';

const IDENTITY_SERVICE_URL = import.meta.env.VITE_IDENTITY_SERVICE_URL || 'http://localhost:8000/api/v1';
const ORDER_SERVICE_URL = import.meta.env.VITE_ORDER_SERVICE_URL || 'http://localhost:8001/api/v1';
const AI_SERVICE_URL = import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8002/api/v1';

// Default client
export const apiClient = axios.create({
  baseURL: IDENTITY_SERVICE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Order service client
export const orderApiClient = axios.create({
  baseURL: ORDER_SERVICE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// AI service client
export const aiServiceClient = axios.create({
  baseURL: AI_SERVICE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// src/services/api.ts

// ... (Phần khai báo biến và axios.create giữ nguyên)

[apiClient, orderApiClient, aiServiceClient].forEach(client => {
  // Request Interceptor (Giữ nguyên)
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response Interceptor (SỬA ĐOẠN NÀY)
  client.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      console.error('❌ API Error Raw:', error); // Log lỗi gốc

      // 1. Xử lý 401 Unauthorized (Giữ nguyên)
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }

      // 2. [QUAN TRỌNG] Lấy thông báo lỗi từ Backend (FastAPI detail)
      if (error.response && error.response.data) {
        const backendDetail = error.response.data.detail;
        const backendMessage = error.response.data.message;
        
        // Ưu tiên lấy 'detail' (FastAPI mặc định) hoặc 'message'
        const customMessage = backendDetail || backendMessage;

        if (customMessage) {
            // Nếu detail là object (validation error), chuyển thành string
            if (typeof customMessage === 'object') {
                error.message = JSON.stringify(customMessage);
            } else {
                // Gán đè vào error.message để UI có thể hiển thị trực tiếp
                error.message = customMessage; 
            }
        }
      }
      
      // Trả về error đã được "độ" lại message
      return Promise.reject(error);
    }
  );
});

export default apiClient;