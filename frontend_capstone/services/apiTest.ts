/**
 * File này chứa các hàm kiểm tra kết nối API
 * Dùng để debug các vấn đề kết nối API trong ứng dụng
 */

// URL cơ sở của API
const API_BASE_URL = 'http://localhost:7860/api/v1';

// Hàm giúp tạo ra một Promise với timeout
const fetchWithTimeout = (url: string, options: RequestInit = {}, timeout = 10000) => {
  return new Promise<Response>((resolve, reject) => {
    // Tạo một controller để cancel fetch request nếu cần
    const controller = new AbortController();
    
    // Set up timeout handler
    const timeoutId = setTimeout(() => {
      controller.abort();
      reject(new Error(`Request timeout after ${timeout}ms`));
    }, timeout);
    
    // Thực hiện fetch với signal từ controller
    fetch(url, {
      ...options,
      signal: controller.signal
    })
    .then(response => {
      clearTimeout(timeoutId);
      resolve(response);
    })
    .catch(error => {
      clearTimeout(timeoutId);
      reject(error);
    });
  });
};

/**
 * Kiểm tra kết nối tới API server
 * @returns Promise<boolean> - true nếu kết nối thành công, false nếu không
 */
export const testApiConnection = async (): Promise<{success: boolean, message: string}> => {
  try {
    console.log(`Testing connection to ${API_BASE_URL}/status...`);
    
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/status`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      },
      5000 // 5 second timeout
    );
    
    if (!response.ok) {
      return {
        success: false,
        message: `Server responded with status: ${response.status}`
      };
    }
    
    return {
      success: true,
      message: 'Connection successful'
    };
  } catch (error: any) {
    console.error('API connection test failed:', error);
    return {
      success: false,
      message: error.message || 'Unknown error'
    };
  }
};

/**
 * Lấy danh sách bài tập của bệnh nhân
 * @param patientId ID của bệnh nhân
 * @returns Promise với dữ liệu bài tập hoặc lỗi
 */
export const testFetchExercises = async (patientId: string): Promise<{success: boolean, data?: any, message: string}> => {
  try {
    console.log(`Testing fetch exercises for patient ${patientId}...`);
    
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/exercises/patient/${patientId}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      },
      10000 // 10 second timeout
    );
    
    if (!response.ok) {
      return {
        success: false,
        message: `Server responded with status: ${response.status}`
      };
    }
    
    const data = await response.json();
    console.log('API response data:', data);
    
    return {
      success: true,
      data,
      message: `Retrieved ${data.data?.length || 0} exercises`
    };
  } catch (error: any) {
    console.error('Exercise fetch test failed:', error);
    return {
      success: false,
      message: error.message || 'Unknown error'
    };
  }
};

/**
 * Kiểm tra tất cả các API endpoints
 * @returns Promise với kết quả kiểm tra
 */
export const runAllTests = async (patientId: string): Promise<{[key: string]: any}> => {
  const results = {
    connection: await testApiConnection(),
    exercises: await testFetchExercises(patientId)
  };
  
  console.log('API Test Results:', results);
  return results;
}; 