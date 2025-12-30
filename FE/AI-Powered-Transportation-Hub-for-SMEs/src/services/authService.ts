// src/services/authService.ts
import apiClient from './api';

// Thêm interface cho login request
export interface LoginRequest {
  username: string;  // Backend expects username, not email
  password: string;
}

// Interface cho login response (từ auth.py endpoint)
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// Interface cho request data (khớp với SmeOwnerRegistration schema)
export interface SmeOwnerRegistrationRequest {
  username: string;           // userName từ form
  password: string;
  business_name: string;      // companyName từ form  
  tax_code: string;          // taxId từ form
  address: string;
  email: string;
  phone: string;
}

// Interface cho response data (khớp với UserOut schema)
export interface UserResponse {
  user_id: string;
  username: string;
  email: string;
  phone: string;
  role: string;
  sme_id: string | null;
  created_at: string;
}

// Interface cho error response
export interface ApiError {
  detail: string;
  status_code?: number;
}

class AuthService {
  /**
   * Login user - kết nối với endpoint /auth/login
   */
    async login(credentials: LoginRequest): Promise<LoginResponse> {
      try {
        console.log('📤 Sending login request:', { username: credentials.username });
        
        // Backend expects form data format (OAuth2PasswordRequestForm)
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        
        const response = await apiClient.post(
        '/auth/login', // Sẽ thành http://localhost:8000/api/v1/auth/login
        formData,
        {
          headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
        );
        
        console.log('✅ Login response:', response.data);
        
        // === PHẦN HOÀN THIỆN (SỬA LỖI) ===
        // Kiểm tra dữ liệu trả về
        if (response.data && response.data.access_token && response.data.user) {
        // 1. Lưu token và user vào localStorage
        localStorage.setItem('access_token', response.data.access_token);
        // User là object, cần stringify trước khi lưu
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // 2. Trả về dữ liệu cho component (để component có thể chuyển trang)
        return response.data;
        } else {
        // Trường hợp API 200 OK nhưng không trả về data (lỗi bất thường)
        console.error('❌ Login response is missing access_token or user data');
        throw new Error('Login response was invalid.');
        }
        // =================================
        
      } catch (error: any) {
        console.error('❌ Login error:', error.response?.data || error.message);
        // Ném lỗi ra để component có thể bắt và hiển thị (ví dụ: "Sai mật khẩu")
        throw error;
      }
      }
  
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    console.log('✅ User logged out');
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser(): UserResponse | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        this.logout(); // Clear invalid data
        return null;
      }
    }
    return null;
  }

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Check if user is logged in
   */
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  /**
   * Đăng ký SME Owner - kết nối với endpoint register-sme-owner
   */
  async registerSmeOwner(data: SmeOwnerRegistrationRequest): Promise<UserResponse> {
    try {
      console.log('📤 Sending SME registration request:', data);
      
      const response = await apiClient.post<UserResponse>(
        '/auth/register-sme-owner',
        data
      );
      
      console.log('✅ SME registration successful:', response.data);
      return response.data;
      
    } catch (error: any) {
      console.error('❌ SME registration failed:', error);
      
      if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || 'Registration failed';
        
        // Handle specific status codes
        switch (status) {
          case 409:  // Conflict - duplicate data
            if (detail.includes('Tax code')) {
              throw new Error('Tax code is already registered. Please use a different tax code.');
            } else if (detail.includes('Email')) {
              throw new Error('Email is already registered. Please use a different email.');
            } else {
              throw new Error('Registration data already exists. Please check your input.');
            }
            
          case 503:  // Service unavailable
            throw new Error('Service is temporarily unavailable. Please try again in a few seconds.');
            
          case 400:  // Bad request
            throw new Error('Invalid registration data. Please check your input.');
            
          default:
            throw new Error(`Registration failed: ${detail}`);
        }
      } else {
        throw new Error('Network error - Unable to connect to server');
      }
    }
  }

  /**
   * Test connection to backend
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await apiClient.get('/health');
      console.log('🔗 Backend connection test successful');
      return true;
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;