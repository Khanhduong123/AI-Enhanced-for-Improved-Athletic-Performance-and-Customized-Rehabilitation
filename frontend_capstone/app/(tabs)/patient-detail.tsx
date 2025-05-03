import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, useColorScheme, ScrollView, TouchableOpacity, FlatList, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, Stack, router } from 'expo-router';
import { FontAwesome, MaterialIcons } from '@expo/vector-icons';
import { Colors } from '../../constants/Colors';
import { getPatientExercises } from '../../services/exerciseService';
import { Exercise } from '../../types/exercise';

// Add extended colors 
const ExtendedColors = {
  ...Colors,
  darkGray: '#666666',
  secondary: '#4CAF50',
  warning: '#FFC107',
  danger: '#F44336',
  success: '#4CAF50',
  lightGray: '#f5f5f5',
  darkBackground: '#333',
  failed: '#ff6b6b', // Màu cho failed exercises
};

// Define Patient type
interface Patient {
  id?: string;
  _id?: string;
  name?: string;
  full_name?: string;
  age?: number | string;
  gender?: string;
  phone?: string;
  email?: string;
  address?: string;
  diagnosis?: string;
  notes?: string;
  startDate?: string;
  nextAppointment?: string;
}

export default function PatientDetail() {
  const params = useLocalSearchParams();
  const colorScheme = useColorScheme() ?? 'light';
  
  // Get patient ID from URL params - Sử dụng _id thay vì id
  const patientId = (params.id as string) || '';
  
  // Parse patient data from params if available
  const [patient, setPatient] = useState<Patient>({});
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Thêm state để quản lý tab đang hiển thị
  const [activeExerciseTab, setActiveExerciseTab] = useState<'assigned' | 'retry' | 'history'>('assigned');

  useEffect(() => {
    // Parse patient data from URL params if available
    try {
      if (params.patientData) {
        const patientData = JSON.parse(params.patientData as string);
        console.log('Parsed patient data:', patientData);
        setPatient(patientData);
      }
    } catch (err) {
      console.error('Error parsing patient data:', err);
      setPatient({ 
        full_name: 'Bệnh nhân',
        email: '',
        diagnosis: 'Chưa có chẩn đoán',
      });
    }
    
    // Fetch patient exercises
    fetchPatientExercises();
  }, [patientId]);

  const fetchPatientExercises = async () => {
    if (!patientId) {
      setError('Không tìm thấy thông tin bệnh nhân');
      setLoading(false);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
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

      console.log('Fetching exercises for patient ID:', patientId);
      
      // Use fetchWithTimeout directly to avoid dependency issues
      // Update API URL to work with Android emulator
      const API_BASE_URL = 'http://10.0.2.2:7860/api/v1'; // For Android emulator
      // const API_BASE_URL = 'http://localhost:7860/api/v1'; // For web or iOS simulator
      
      const response = await fetchWithTimeout(
        `${API_BASE_URL}/exercises/patient/${patientId}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        },
        10000 // 10 second timeout
      );
      
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Patient exercises fetched successfully:', result);
      
      // Kiểm tra cấu trúc dữ liệu và set state đúng cách
      // Dựa vào log, dữ liệu trả về có vẻ là array trực tiếp, không có thuộc tính data
      if (Array.isArray(result)) {
        // Nếu result trực tiếp là array
        console.log(`Found ${result.length} exercises`);
        setExercises(result);
      } else if (result.data && Array.isArray(result.data)) {
        // Nếu result có thuộc tính data là array
        console.log(`Found ${result.data.length} exercises in result.data`);
        setExercises(result.data);
      } else {
        // Trường hợp không xác định được cấu trúc dữ liệu
        console.error('Unexpected data structure:', result);
        setExercises([]);
        setError('Dữ liệu bài tập không đúng định dạng');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching exercises:', err);
      setError('Không thể tải danh sách bài tập');
      setLoading(false);
    }
  };

  // Get status color based on exercise status
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'complete':
      case 'completed':
        return ExtendedColors.success;
      case 'in progress':
        return ExtendedColors.warning;
      case 'failed':
        return ExtendedColors.failed;
      case 'pending':
      default:
        return ExtendedColors.darkGray;
    }
  };

  // Get status text in Vietnamese
  const getStatusText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'complete':
      case 'completed':
        return 'Đã hoàn thành';
      case 'in progress':
        return 'Đang thực hiện';
      case 'failed':
        return 'Tập lại';
      case 'pending':
      default:
        return 'Chưa hoàn thành';
    }
  };

  // Format date for display
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Không có';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('vi-VN');
    } catch (error) {
      return dateString;
    }
  };

  // Lọc danh sách bài tập theo tab đang hiển thị
  const getFilteredExercises = () => {
    if (!exercises || exercises.length === 0) return [];
    
    switch (activeExerciseTab) {
      case 'assigned':
        return exercises.filter(exercise => exercise.status.toLowerCase() === 'pending');
      case 'retry':
        return exercises.filter(exercise => exercise.status.toLowerCase() === 'not completed');
      case 'history':
        return exercises.filter(exercise => exercise.status.toLowerCase() === 'complete' || exercise.status.toLowerCase() === 'completed');
      default:
        return exercises;
    }
  };

  // Hiển thị số lượng bài tập cho mỗi danh mục
  const getPendingExercisesCount = () => exercises.filter(e => e.status.toLowerCase() === 'pending').length;
  const getFailedExercisesCount = () => exercises.filter(e => e.status.toLowerCase() === 'not completed').length;
  const getCompletedExercisesCount = () => exercises.filter(e => e.status.toLowerCase() === 'complete' || e.status.toLowerCase() === 'completed').length;

  // Patient name display (handle both name and full_name properties)
  const patientName = patient.full_name || patient.name || 'Không xác định';

  // Render exercise tabs
  const renderExerciseTabs = () => (
    <View style={styles.tabContainer}>
      <TouchableOpacity
        style={[
          styles.tab,
          activeExerciseTab === 'assigned' && styles.activeTab,
        ]}
        onPress={() => setActiveExerciseTab('assigned')}
      >
        <Text style={[
          styles.tabText,
          activeExerciseTab === 'assigned' && styles.activeTabText,
        ]}>
          Bài tập được giao ({getPendingExercisesCount()})
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[
          styles.tab,
          activeExerciseTab === 'retry' && styles.activeTab,
        ]}
        onPress={() => setActiveExerciseTab('retry')}
      >
        <Text style={[
          styles.tabText,
          activeExerciseTab === 'retry' && styles.activeTabText,
        ]}>
          Cần tập lại ({getFailedExercisesCount()})
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[
          styles.tab,
          activeExerciseTab === 'history' && styles.activeTab,
        ]}
        onPress={() => setActiveExerciseTab('history')}
      >
        <Text style={[
          styles.tabText,
          activeExerciseTab === 'history' && styles.activeTabText,
        ]}>
          Lịch sử ({getCompletedExercisesCount()})
        </Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <>
      <Stack.Screen
        options={{
          title: 'Chi tiết bệnh nhân',
          headerStyle: {
            backgroundColor: Colors.primary,
          },
          headerTintColor: Colors.white,
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        
        }}
      />
      
      <View style={[styles.container, { backgroundColor: colorScheme === 'dark' ? ExtendedColors.darkBackground : Colors.white }]}>
        {/* Patient Info Card */}
        <View style={[styles.card, { 
          backgroundColor: colorScheme === 'dark' ? '#444' : Colors.white,
          margin: 16,
          marginBottom: 8,
        }]}>
          <Text style={[styles.cardTitle, { color: Colors[colorScheme].text }]}>Thông tin bệnh nhân</Text>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Họ tên:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patientName}</Text>
          </View>
          
          {patient.age && (
            <View style={styles.infoRow}>
              <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Tuổi:</Text>
              <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.age}</Text>
            </View>
          )}
          
          {patient.diagnosis && (
            <View style={styles.infoRow}>
              <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Chẩn đoán:</Text>
              <Text style={[styles.infoValue, { color: Colors.primary }]}>{patient.diagnosis}</Text>
            </View>
          )}
        </View>
        
        {/* Exercise Section Header */}
        <View style={[styles.exerciseHeaderView, { 
          marginHorizontal: 16,
          marginTop: 8,
          marginBottom: 8,
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'center' 
        }]}>
          <Text style={[styles.cardTitle, { color: Colors[colorScheme].text, marginBottom: 0 }]}>Bài tập</Text>
          <TouchableOpacity
            style={styles.refreshButton}
            onPress={fetchPatientExercises}
          >
            <MaterialIcons name="refresh" size={20} color={Colors.primary} />
          </TouchableOpacity>
        </View>
        
        {/* Exercise Tabs */}
        {renderExerciseTabs()}
        
        {/* Exercise List - Not inside ScrollView */}
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={Colors.primary} />
            <Text style={styles.loadingText}>Đang tải dữ liệu...</Text>
          </View>
        ) : error ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={fetchPatientExercises}
            >
              <Text style={styles.retryButtonText}>Thử lại</Text>
            </TouchableOpacity>
          </View>
        ) : getFilteredExercises().length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={[styles.emptyText, { color: ExtendedColors.darkGray }]}>
              {activeExerciseTab === 'assigned' && 'Chưa có bài tập nào được giao'}
              {activeExerciseTab === 'retry' && 'Không có bài tập nào cần tập lại'}
              {activeExerciseTab === 'history' && 'Chưa có bài tập nào đã hoàn thành'}
            </Text>
          </View>
        ) : (
          <FlatList
            data={getFilteredExercises()}
            keyExtractor={(item) => item._id}
            style={{ flex: 1, marginTop: 0 }}
            contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 16 }}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[styles.exerciseItem, {
                  borderLeftColor: getStatusColor(item.status)
                }]}
                onPress={() => 
                  router.push({
                    pathname: '/(tabs)/exercise-detail',
                    params: { id: item._id, exerciseData:JSON.stringify(item) }
                  })
                }
              >
                <View style={styles.exerciseHeader}>
                  <Text style={styles.exerciseName}>{item.name}</Text>
                  <Text
                    style={[
                      styles.exerciseStatus,
                      { color: getStatusColor(item.status) }
                    ]}
                  >
                    {getStatusText(item.status)}
                  </Text>
                </View>
                
                <View style={styles.exerciseDetails}>
                  <Text style={styles.exerciseDate}>
                    Ngày giao: {formatDate(item.assigned_date)}
                  </Text>
                  <Text style={styles.exerciseDate}>
                    Hạn hoàn thành: {formatDate(item.due_date)}
                  </Text>
                </View>
                
                {item.description && (
                  <Text style={styles.exerciseDescription} numberOfLines={2}>
                    {item.description}
                  </Text>
                )}
              </TouchableOpacity>
            )}
            ListFooterComponent={null}
          />
        )}

        {/* Thêm nút nhỏ quay lại ở góc trái màn hình */}
       
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  card: {
    borderRadius: 10,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8,
    flexWrap: 'wrap',
  },
  infoLabel: {
    width: 140,
    fontWeight: '500',
    fontSize: 14,
  },
  infoValue: {
    flex: 1,
    fontSize: 14,
  },
  exerciseHeaderView: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  errorContainer: {
    padding: 20,
    alignItems: 'center',
  },
  errorText: {
    color: ExtendedColors.danger,
    marginBottom: 10,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: Colors.primary,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  retryButtonText: {
    color: Colors.white,
    fontWeight: 'bold',
  },
  emptyContainer: {
    padding: 20,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontStyle: 'italic',
    textAlign: 'center',
  },
  exerciseItem: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  exerciseStatus: {
    fontSize: 12,
    fontWeight: 'bold',
    padding: 4,
    borderRadius: 4,
    overflow: 'hidden',
  },
  exerciseDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  exerciseDate: {
    fontSize: 12,
    color: '#666',
  },
  exerciseDescription: {
    fontSize: 13,
    color: '#555',
    marginTop: 4,
  },
  refreshButton: {
    padding: 4,
  },
  tabContainer: {
    flexDirection: 'row',
    marginBottom: 8,
    marginHorizontal: 16,
    backgroundColor: ExtendedColors.lightGray,
    borderRadius: 8,
    overflow: 'hidden',
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
  },
  activeTab: {
    backgroundColor: Colors.primary,
  },
  tabText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#555',
    textAlign: 'center',
  },
  activeTabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  backButtonFloat: {
    position: 'absolute',
    top: 16,
    left: 16,
    backgroundColor: Colors.primary,
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    zIndex: 100,
  },
}); 