import { Exercise, ExerciseResponse } from '../types/exercise';
import { Platform } from 'react-native';

// Thay đổi URL API để hỗ trợ cả local và remote environments
// Trong môi trường thực tế, bạn nên sử dụng biến môi trường (environment variables)
const API_BASE_URL = Platform.select({
  ios: 'http://192.168.68.104:7860/api/v1',
  android: 'http://192.168.68.104:7860/api/v1', // Special IP for Android emulator to reach host machine
  default: 'http://192.168.68.104:7860/api/v1',
});

// Alternative API URL if you're testing on a physical device
// Replace with your actual machine's IP address on your network
const ALTERNATIVE_API_URL = 'http://192.168.68.104:7860/api/v1';

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

export const getPatientExercises = async (patientId: string): Promise<Exercise[]> => {
  try {
    console.log(`Fetching exercises from: ${API_BASE_URL}/exercises/patient/${patientId}`);
    
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/exercises/patient/${patientId}`,
      {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      },
      10000 // 10 second timeout
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error response:', errorText);
      throw new Error(`Server responded with status: ${response.status}`);
    }
    
    const data: ExerciseResponse = await response.json();
    console.log('Exercises fetched successfully:', data);
    return data.data || [];
  } catch (error) {
    console.error('Error fetching exercises:', error);
    // Check for specific network errors
    if (error instanceof TypeError && error.message.includes('Network request failed')) {
      console.error('Network error. API server might be down or unreachable.');
    }
    throw error;
  }
};

export const updateExerciseStatus = async (exerciseId: string, status: Exercise['status']): Promise<Exercise> => {
  try {
    console.log(`Updating exercise status: ${exerciseId} to ${status}`);
    
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/exercises/${exerciseId}`,
      {
        method: 'PATCH',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
      },
      10000 // 10 second timeout
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error response:', errorText);
      throw new Error(`Server responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Exercise status updated successfully:', data);
    return data.data;
  } catch (error) {
    console.error('Error updating exercise status:', error);
    // Check for specific network errors
    if (error instanceof TypeError && error.message.includes('Network request failed')) {
      console.error('Network error. API server might be down or unreachable.');
    }
    throw error;
  }
}; 