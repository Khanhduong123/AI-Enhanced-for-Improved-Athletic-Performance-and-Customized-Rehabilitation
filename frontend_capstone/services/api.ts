import axios from 'axios';
import { Platform } from 'react-native';

// Hàm tiện ích để đảm bảo dữ liệu tiếng Việt được xử lý đúng
export const ensureValidUnicode = (text: string): string => {
  if (!text) return '';
  return text.trim();
};

// API configuration based on platform
const API_URL = Platform.select({
  ios: 'http://192.168.2.11:7860/api/v1',
  android: 'http://192.168.2.11:7860/api/v1', // Special IP for Android emulator to reach host machine
  default: 'http://192.168.2.11:7860/api/v1', // Change this to your actual machine's IP
});

// Fallback in case primary API fails
const FALLBACK_API_URL = 'http://192.168.2.11:7860/api/v1'; // Change this to your actual machine's IP

console.log('[API] Platform is:', Platform.OS);
console.log('[API] API URL being used:', API_URL);
console.log('[API] Fallback API URL:', FALLBACK_API_URL);

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json; charset=utf-8',
  },
  timeout: 15000, // 15 seconds timeout (increased from 10 seconds)
});

// Add request/response logging for debugging
apiClient.interceptors.request.use(request => {
  console.log('[API] Request:', request.method, request.url);
  console.log('[API] Request headers:', JSON.stringify(request.headers));
  if (request.params) console.log('[API] Request params:', JSON.stringify(request.params));
  if (request.data) console.log('[API] Request data:', JSON.stringify(request.data));
  
  // Đảm bảo Content-Type header luôn có charset=utf-8
  if (request.headers && request.headers['Content-Type'] === 'application/json') {
    request.headers['Content-Type'] = 'application/json; charset=utf-8';
  }
  
  return request;
});

apiClient.interceptors.response.use(
  response => {
    console.log('[API] Response SUCCESS:', response.status, response.config.url);
    console.log('[API] Response data preview:', JSON.stringify(response.data).substring(0, 200) + '...');
    return response;
  },
  error => {
    if (error.response) {
      // The request was made and the server responded with an error
      console.error('[API] Error Response:', error.response.status, error.response.config.url);
      console.error('[API] Error data:', JSON.stringify(error.response.data));
      console.error('[API] Response headers:', JSON.stringify(error.response.headers));
    } else if (error.request) {
      // The request was made but no response was received
      console.error('[API] No Response Error - Request failed to complete');
      console.error('[API] Request details:', error.request._url || error.request.url);
      
      // Try with fallback URL if the main one failed
      if (error.config && error.config.url && error.config.url.includes(API_URL)) {
        console.log('[API] Attempting fallback URL...');
        
        // Create a new config with the fallback URL
        const fallbackConfig = {...error.config};
        fallbackConfig.url = fallbackConfig.url.replace(API_URL, FALLBACK_API_URL);
        console.log('[API] Retrying with:', fallbackConfig.url);
        
        // Return the new request
        return axios(fallbackConfig);
      }
    } else {
      // Something else happened in setting up the request
      console.error('[API] Setup Error:', error.message);
      if (error.stack) console.error('[API] Error stack:', error.stack);
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  // Đăng ký người dùng (endpoint: /users/)
  register: async (userData: {
    email: string;
    full_name: string;
    role: string;
    password: string;
    specialization?: string;
    diagnosis?: string;
  }) => {
    try {
      console.log('[Auth API] Registering user:', userData.email);
      
      // Chuẩn hóa role
      const normalizedRole = userData.role.toLowerCase() === 'doctor' ? 'Doctor' : 'Patient';
      
      // Đảm bảo dữ liệu Unicode (tiếng Việt) được xử lý đúng
      const sanitizedUserData = {
        ...userData,
        role: normalizedRole,
        full_name: ensureValidUnicode(userData.full_name),
        email: ensureValidUnicode(userData.email),
        specialization: userData.specialization ? ensureValidUnicode(userData.specialization) : undefined,
      };
      
      const response = await apiClient.post('/users/', sanitizedUserData);
      console.log('[Auth API] Registration successful');
      return response.data;
    } catch (error) {
      console.error('[Auth API] Registration failed:', error);
      throw error;
    }
  },

  // Cập nhật hàm login để gửi email và password qua query parameters
  login: async (email: string, password: string) => {
    try {
      console.log('[Auth API] Attempting login with email:', email);
      
      // Send POST request to /users/login
      // Add email and password in `params` for axios to attach to URL
      const response = await apiClient.post('/users/login', null, {
        params: {
          email: email,
          password: password
        }
      });
      
      console.log('[Auth API] Login successful, status:', response.status);
      console.log('[Auth API] User data received:', JSON.stringify(response.data));
      
      // Validate the response
      if (!response.data) {
        console.error('[Auth API] Login response is empty');
        throw new Error('Invalid login response: empty data');
      }
      
      if (!response.data.id && !response.data._id) {
        console.error('[Auth API] Login response missing user ID');
        // Try to extract ID from unexpected response format if possible
        if (response.data.data && (response.data.data.id || response.data.data._id)) {
          console.log('[Auth API] Found user ID in nested data property');
          return response.data.data;
        }
        throw new Error('Invalid login response: missing user ID');
      }
      
      return response.data;
    } catch (error) {
      console.error('[Auth API] Login failed:', error);
      throw error;
    }
  },

  // Lấy thông tin người dùng hiện tại (giả sử endpoint là /users/me)
  getMe: async (token: string) => {
    try {
      console.log('[Auth API] Fetching user profile with token');
      
      // First 6 chars of token for logging (don't log full token)
      const tokenPreview = token.substring(0, 6) + '...';
      console.log('[Auth API] Using token starting with:', tokenPreview);
      
      const response = await apiClient.get('/users/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      console.log('[Auth API] User profile fetch successful');
      console.log('[Auth API] User data:', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('[Auth API] Failed to fetch user profile:', error);
      throw error;
    }
  }
};

// Thiết lập interceptor để gắn token vào header của các request
export const setupInterceptors = (token: string) => {
  if (!token) {
    console.warn('[API] Attempted to setup interceptors with empty token');
    return;
  }
  
  const tokenPreview = token.substring(0, 6) + '...';
  console.log('[API] Setting up auth interceptors with token starting with:', tokenPreview);

  apiClient.interceptors.request.use(
    (config) => {
      config.headers.Authorization = `Bearer ${token}`;
      return config;
    },
    (error) => {
      console.error('[API] Interceptor request error:', error);
      return Promise.reject(error);
    }
  );
};

export default apiClient;
