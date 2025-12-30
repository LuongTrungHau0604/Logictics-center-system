import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native'; // [QUAN TRỌNG] Để check Web hay App

// ============================================================================
// CẤU HÌNH IP
// ============================================================================
// Nếu chạy trên Web cùng máy tính server: Có thể dùng 'localhost' hoặc IP LAN
// Nếu chạy trên Điện thoại: BẮT BUỘC dùng IP LAN (Vd: 192.168.50.144)
const HOST = '192.168.50.144'; // <-- Đảm bảo IP này đúng với máy tính của bạn
const PORT_IDENTITY = '8000';
const PORT_ORDER = '8001';
const PORT_AI = '8002';

const IDENTITY_URL = `http://${HOST}:${PORT_IDENTITY}/api/v1`;
const ORDER_URL = `http://${HOST}:${PORT_ORDER}/api/v1`;
const AI_URL = `http://${HOST}:${PORT_AI}/api/v1`;

// ============================================================================
// HÀM HỖ TRỢ LƯU TRỮ ĐA NỀN TẢNG (WEB & APP)
// ============================================================================

const setToken = async (key: string, value: string) => {
  if (Platform.OS === 'web') {
    localStorage.setItem(key, value);
  } else {
    await SecureStore.setItemAsync(key, value);
  }
};

const getToken = async (key: string) => {
  if (Platform.OS === 'web') {
    return localStorage.getItem(key);
  } else {
    return await SecureStore.getItemAsync(key);
  }
};

const removeToken = async (key: string) => {
  if (Platform.OS === 'web') {
    localStorage.removeItem(key);
  } else {
    await SecureStore.deleteItemAsync(key);
  }
};

// ============================================================================
// AXIOS CLIENTS
// ============================================================================

export const identityClient = axios.create({
  baseURL: IDENTITY_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const orderClient = axios.create({
  baseURL: ORDER_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const aiClient = axios.create({
  baseURL: AI_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// ============================================================================
// INTERCEPTORS
// ============================================================================

[identityClient, orderClient, aiClient].forEach((client) => {
  client.interceptors.request.use(
    async (config) => {
      try {
        // Sử dụng hàm getToken đã viết ở trên
        const token = await getToken('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        console.log(`🚀 [API] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
      } catch (error) {
        console.error('Error loading token:', error);
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        // Sử dụng hàm removeToken đã viết ở trên
        await removeToken('access_token');
        await removeToken('user_info');
      }
      return Promise.reject(error);
    }
  );
});

// ============================================================================
// API FUNCTIONS
// ============================================================================

export const loginAPI = async (username: string, password: string) => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await identityClient.post('/auth/login', formData.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const data = response.data;

    if (data.access_token) {
      await setToken('access_token', data.access_token);
    }
    if (data.user) {
      await setToken('user_info', JSON.stringify(data.user));
    }

    return data;
  } catch (error: any) {
    // Log chi tiết lỗi để debug
    console.error('Full error:', error);
    throw new Error(error.response?.data?.detail || error.message || 'Đăng nhập thất bại');
  }
};


export const getShipperProfile = async () => {
  try {
    // Calling the endpoint we created above: /shippers/me
    // Note: Adjust '/shippers/me' if your prefix is different (e.g., '/api/v1/shippers/me')
    const response = await identityClient.get('/shippers/me'); 
    return response.data;
  } catch (error: any) {
    console.error('Error fetching profile:', error);
    throw error;
  }
};

export const logout = async () => {
  await removeToken('access_token');
  await removeToken('user_info');
};


// api.ts - Thêm vào phần API FUNCTIONS

export const completeDeliveryOrder = async (orderId: string) => {
  try {
    // Gọi endpoint PUT vừa tạo ở backend
    const response = await orderClient.put(`/orders/shipper/complete-delivery/${orderId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error completing delivery:', error);
    throw new Error(error.response?.data?.detail || 'Không thể cập nhật trạng thái đơn hàng');
  }
};


// 1. Hàm gửi FCM Token lên Server (Gọi khi App vừa mở)
export const registerDeviceToken = async (token: string) => {
  try {
    // Backend cần endpoint này để lưu token vào bảng shippers
    await identityClient.put('/shippers/me/device-token', { fcm_token: token });
    console.log('✅ Đã gửi FCM Token lên server');
  } catch (error) {
    console.error('Lỗi gửi token:', error);
  }
};

export const updateShipperLocation = async (lat: number, lon: number) => {
  try {
    // Backend cần endpoint này để cập nhật current_lat/lon
    await identityClient.post('/shippers/me/location', { 
      current_lat: lat, 
      current_lon: lon 
    });
    // Không log quá nhiều để tránh spam console
  } catch (error) {
    console.error('Lỗi cập nhật vị trí:', error);
  }
};

// ============================================================================
// AI AGENT FUNCTIONS
// ============================================================================

export const reportIncidentAPI = async (shipperId: string, message: string, lat: number, lon: number) => {
  try {
    // Gọi tới AI Service (Port 8002)
    // Lưu ý: Endpoint này phải khớp với backend (/api/v1/report-incident hoặc /report-incident tùy cấu hình prefix)
    const response = await aiClient.post('ai-batch-optimizer/ai/report-incident', {
      shipper_id: shipperId,
      message: message,
      latitude: lat,
      longitude: lon
    });
    
    return response.data;
  } catch (error: any) {
    console.error('Error reporting incident:', error);
    
    // Xử lý lỗi chi tiết để hiển thị cho user
    let errorMessage = 'Không thể kết nối tới AI Agent';
    if (error.response) {
      errorMessage = error.response.data?.detail || `Lỗi Server (${error.response.status})`;
    } else if (error.request) {
      errorMessage = 'Không có phản hồi từ Server. Kiểm tra kết nối mạng.';
    }
    
    throw new Error(errorMessage);
  }
};