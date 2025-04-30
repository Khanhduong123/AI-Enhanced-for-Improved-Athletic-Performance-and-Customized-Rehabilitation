import apiClient from './api';

// Mock patient data for development
const MOCK_PATIENTS = [
  { id: '1', full_name: 'Nguyễn Văn A', age: 45, diagnosis: 'Phục hồi sau phẫu thuật gối', email: 'nguyenvana@example.com', exercises_count: 3 },
  { id: '2', full_name: 'Trần Thị B', age: 32, diagnosis: 'Đau lưng mãn tính', email: 'tranthib@example.com', exercises_count: 2 },
  { id: '3', full_name: 'Lê Văn C', age: 50, diagnosis: 'Phục hồi đột quỵ', email: 'levanc@example.com', exercises_count: 2 },
  { id: '4', full_name: 'Phạm Thị D', age: 28, diagnosis: 'Đau vai', email: 'phamthid@example.com', exercises_count: 1 },
];

/**
 * Get patients for a doctor
 * @param doctorId The ID of the doctor
 * @returns A promise that resolves to an array of patients
 */
export const getPatients = async (doctorId: string) => {
  try {
    // Use the real API endpoint
    const response = await apiClient.get(`/exercises/doctor/${doctorId}/patients`);
    console.log('API response for patients:', response.data);
    return response.data;
    
    // Fallback to mock data if needed for development
    // return MOCK_PATIENTS;
  } catch (error) {
    console.error('Error fetching patients:', error);
    throw error;
  }
};

/**
 * Get exercises assigned to a patient
 * @param patientId The ID of the patient
 * @returns A promise that resolves to an array of exercises
 */
export const getPatientExercises = async (patientId: string) => {
  try {
    // Use the real API endpoint to fetch patient exercises
    const response = await apiClient.get(`/exercises/patient/${patientId}`);
    console.log('Patient exercises response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching patient exercises:', error);
    throw error;
  }
};

/**
 * Get patient details
 * @param patientId The ID of the patient
 * @returns A promise that resolves to patient details
 */
export const getPatientDetails = async (patientId: string) => {
  try {
    // For development, return mock data
    // In a real implementation, this would fetch from the API
    const patient = MOCK_PATIENTS.find(p => p.id === patientId);
    if (!patient) {
      throw new Error('Patient not found');
    }
    return patient;
  } catch (error) {
    console.error('Error fetching patient details:', error);
    throw error;
  }
};

/**
 * Assign exercises to a patient
 * @param patientId The ID of the patient
 * @param exerciseIds Array of exercise IDs to assign
 * @returns A promise that resolves when exercises are assigned
 */
export const assignExercisesToPatient = async (patientId: string, exerciseIds: string[]) => {
  try {
    // For development, just log the action
    console.log(`Assigning exercises ${exerciseIds.join(', ')} to patient ${patientId}`);
    
    // When backend is ready, uncomment this code:
    /*
    const response = await apiClient.post(`/patients/${patientId}/exercises`, {
      exercise_ids: exerciseIds
    });
    return response.data;
    */
    
    return { success: true };
  } catch (error) {
    console.error('Error assigning exercises:', error);
    throw error;
  }
};
