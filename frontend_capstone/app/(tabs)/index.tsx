import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, StyleSheet, useColorScheme, Image, TouchableOpacity, ScrollView, FlatList, ActivityIndicator, Alert, Modal, TextInput, Platform, TouchableWithoutFeedback } from 'react-native';
import { Colors } from '../../constants/Colors';
import { useAuthStore } from '../../store/authStore';
import { router, Stack } from 'expo-router';
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import { getPatients } from '../../services/doctor-api';
import { getPatientExercises } from '../../services/exerciseService';
import { Exercise as ExerciseType } from '../../types/exercise';
import { runAllTests } from '../../services/apiTest';
import DateTimePicker from '@react-native-community/datetimepicker';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';

// Add logging to help debug
const DEBUG = true;
const log = (...args: any[]) => {
  if (DEBUG) console.log('[HomeScreen]', ...args);
};

// API Configuration
// Note: In a real development environment, we need to use the actual
// IP address of the machine running the server, not 'localhost'
// For Android emulator, use 10.0.2.2 to access the host machine
// For iOS simulator, use localhost
// For physical devices, use your actual IP address on your network
const API_BASE_URL = Platform.select({
  ios: 'http://localhost:7860',
  android: 'http://10.0.2.2:7860', // Special IP for Android emulator to reach host machine
  default: 'http://localhost:7860',
});

// Alternative API URL if you're testing on a physical device
// Replace with your actual machine's IP address on your network
// Example: const ALTERNATIVE_API_URL = 'http://192.168.1.100:7860';
const ALTERNATIVE_API_URL = 'http://localhost:7860';

// Add a utility function to help with fallback API calls
const fetchWithFallback = async (url: string, options: RequestInit = {}) => {
  try {
    // First try with the platform-specific API URL
    const response = await fetch(url, options);
    return response;
  } catch (err) {
    // If that fails and we were using the primary API URL, try the alternative URL
    if (url.startsWith(API_BASE_URL)) {
      console.log(`[API] Primary URL failed, trying alternative: ${url.replace(API_BASE_URL, ALTERNATIVE_API_URL)}`);
      return fetch(url.replace(API_BASE_URL, ALTERNATIVE_API_URL), options);
    }
    throw err;
  }
};

// Add extended colors for additional styling
const ExtendedColors = {
  ...Colors,
  darkGray: '#666666',
  secondary: '#4CAF50',
  danger: '#F44336',
  warning: '#FFC107',
  success: '#4CAF50',
};

// Giả lập dữ liệu cho giao diện demo
const MOCK_EXERCISES = [
  { id: '1', name: 'Tập vật lý trị liệu vai', status: 'Chưa hoàn thành', time: '10:00 - 10:30', date: '15/04/2023' },
  { id: '2', name: 'Tập phục hồi cơ lưng', status: 'Đã hoàn thành', time: '14:00 - 14:45', date: '14/04/2023' },
  { id: '3', name: 'Bài tập tăng cường cơ chân', status: 'Thực hiện sai', time: '09:00 - 10:00', date: '16/04/2023' },
  { id: '4', name: 'Tập cổ tay', status: 'Đã hoàn thành', time: '15:30 - 16:00', date: '12/04/2023' },
  { id: '5', name: 'Tập phục hồi cổ', status: 'Chưa hoàn thành', time: '08:00 - 08:30', date: '17/04/2023' },
  { id: '6', name: 'Bài tập khớp gối', status: 'Thực hiện sai', time: '11:00 - 11:30', date: '14/04/2023' },
];


type SortOption = 'time-asc' | 'time-desc' | 'name-asc' | 'name-desc';
type FilterStatus = 'all' | 'Chưa hoàn thành' | 'Thực hiện sai';

interface Patient {
  _id: string;
  full_name: string;
  email?: string;
  phone?: string;
  age?: number;
  gender?: string;
  // Add other fields as needed based on your API response
}

interface UserData {
  id: string;
  _id?: string; // Added for MongoDB compatibility
  full_name: string;
  email: string;
  phone: string;
  address: string;
  date_of_birth: string;
  gender: string;
  avatar_url: string;
  patientAge?: number;
}

interface Exercise {
  name: string;
  description: string;
  assigned_by: string;
  assigned_to: string;
  assigned_date: string;
  due_date: string;
  status: string;
}

// Mảng ánh xạ tên bài tập để hiển thị tên tiếng Việt có dấu
const exerciseNameMapping: Record<string, string> = {
  'Xemxaxemgan': 'Xem xa xem gần',
  'Ngoithangbangtrengot': 'Ngồi thăng bằng trên gót',
  'Dangchanraxanghiengminh': 'Dang chân ra xa nghiêng mình',
  'Sodatvuonlen': 'Sờ đất vươn lên',
  // Thêm các bài tập khác ở đây
};

// Hàm để lấy tên hiển thị của bài tập
const getExerciseDisplayName = (exerciseId: string): string => {
  return exerciseNameMapping[exerciseId] || exerciseId;
};

const HomeScreen = () => {
  console.log("Rendering HomeScreen component");
  
  const colorScheme = useColorScheme() ?? 'light';
  const { userRole, user, isLoggedIn, logout } = useAuthStore();
  
 
  
  const [activeTab, setActiveTab] = useState('current');
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all');
  const [sortOption, setSortOption] = useState<SortOption>('time-asc');
  const [showFilterMenu, setShowFilterMenu] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoadingPatients, setIsLoadingPatients] = useState(false);
  const [patientsError, setPatientsError] = useState<string | null>(null);
  const [exercises, setExercises] = useState<ExerciseType[]>([]);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);
  const [exercisesError, setExercisesError] = useState<string | null>(null);

  // --- State for Create Exercise Modal ---
  const [showCreateExerciseModal, setShowCreateExerciseModal] = useState(false);
  const [selectedPatientForExercise, setSelectedPatientForExercise] = useState<string>('');
  const [exerciseName, setExerciseName] = useState('');
  const [exerciseDescription, setExerciseDescription] = useState('');
  const [assignedDate, setAssignedDate] = useState(new Date());
  const [dueDate, setDueDate] = useState(new Date());
  const [showAssignedDatePicker, setShowAssignedDatePicker] = useState(false);
  const [showDueDatePicker, setShowDueDatePicker] = useState(false);
  const [showExerciseDropdown, setShowExerciseDropdown] = useState(false);
  const [showPatientDropdown, setShowPatientDropdown] = useState(false);




  const handleLogout = () => {
    log('Logging out user');
    try {
      // First clear all component state that might cause hooks issues
      setRecordingExercise(null);
      setVideoUri(null);
      setPredictionResult(null);
      setIsPredicting(false);
      setShowCamera(false);
      setExercises([]);
      setPatients([]);
      setShowCreateExerciseModal(false);
      setShowFilterMenu(false);
      
      // Then call logout after our component is in a clean state
      setTimeout(() => {
        logout();
      }, 50); // Increased from 0 to ensure state updates complete
    } catch (error) {
      console.error('[HomeScreen] Error during logout:', error);
    }
  };

  // Render profile section with avatar and name
  const renderProfileSection = () => {
    if (!user) return null;
    
    // Use type assertion to work around TypeScript error
    const avatarUrl = user && (user as any).avatar_url ? (user as any).avatar_url : 'https://via.placeholder.com/150';
    return (
    <View style={styles.profileSection}>
     <View style={styles.patientAvatarContainer}>
                <View style={[styles.patientAvatar, {backgroundColor:"green"}]}>
                  <Text style={styles.patientInitial}>
                    {user.full_name.charAt(0).toUpperCase()}
                  </Text>
                </View>
              </View>
      <View style={styles.profileInfo}>
        <Text style={[styles.userName, { color: Colors[colorScheme].text }]}>
            {user?.full_name || 'Người dùng'}
        </Text>
        {userRole?.toLowerCase() === 'doctor' || userRole?.toLowerCase() === 'docter' ? (
          <>
            <Text style={[styles.userRole, { color: Colors.primary }]}>
              {(user as any).specialization || 'Bác sĩ phục hồi chức năng'}
            </Text>
            {(user as any).diagnosis && (
              <Text style={{ fontSize: 12, marginBottom: 2, color: ExtendedColors.secondary }}>
                Chuyên khoa: {(user as any).diagnosis}
              </Text>
            )}
          </>
        ) : (
          <Text style={[styles.userRole, { color: Colors.primary }]}>
            Bệnh nhân đang điều trị
          </Text>
        )}
      </View>
      <TouchableOpacity 
        style={styles.logoutButton} 
        onPress={handleLogout}
      >
        <Text style={styles.logoutText}>Đăng xuất</Text>
      </TouchableOpacity>
    </View>
  );
  };

  // Hàm sắp xếp ngày tháng từ dạng chuỗi dd/mm/yyyy
  const compareDates = (date1: string, date2: string) => {
    const [day1, month1, year1] = date1.split('/').map(Number);
    const [day2, month2, year2] = date2.split('/').map(Number);

    if (year1 !== year2) return year1 - year2;
    if (month1 !== month2) return month1 - month2;
    return day1 - day2;
  };

  // Hàm sắp xếp thời gian từ dạng chuỗi hh:mm - hh:mm
  const compareTimes = (time1: string, time2: string) => {
    const startTime1 = time1.split(' - ')[0];
    const startTime2 = time2.split(' - ')[0];
    
    const [hour1, minute1] = startTime1.split(':').map(Number);
    const [hour2, minute2] = startTime2.split(':').map(Number);

    if (hour1 !== hour2) return hour1 - hour2;
    return minute1 - minute2;
  };

  // Fetch exercises when component mounts
  useEffect(() => {
    if(user?._id && user?.role.toLocaleLowerCase() === "patient"){
      fetchExercises(user._id);
    }

  }, [user?._id]); // Chỉ chạy một lần khi component mount

  const fetchExercises = async (userId:string) => {

    setIsLoadingExercises(true);
    setExercisesError(null);
    
    try {
      log('Fetching exercises for patient ID:', userId);
      
      // Gọi trực tiếp API để lấy bài tập
      const response = await fetch(`${API_BASE_URL}/api/v1/exercises/patient/${userId}`);
      
      if (!response.ok) {
        throw new Error(`API returned status code ${response.status}`);
      }
      
      const data = await response.json();
      log('Exercises fetched successfully:', data);
      
      if (Array.isArray(data)) {
        setExercises(data);
        log(`Found ${data.length} exercises`);
      } else if (data && Array.isArray(data.data)) {
        setExercises(data.data);
        log(`Found ${data.data.length} exercises in data.data`);
      } else {
        log('No exercises found or unexpected format');
        setExercises([]);
      }
    } catch (error) {
      console.error('Failed to fetch exercises:', error);
      setExercisesError('Không thể tải danh sách bài tập');
      
      Alert.alert(
        'Lỗi',
        'Không thể tải danh sách bài tập. Vui lòng thử lại sau.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoadingExercises(false);
    }
  };

  // Lọc và sắp xếp bài tập dựa vào tab, filter và sort option
  const getFilteredAndSortedExercises = () => {
    console.log(exercises)
    // Bước 1: Lọc theo tab đang chọn
    let filtered = activeTab === 'current'
      ? exercises.filter(ex => ex.status === 'Pending' || ex.status === 'In Progress' || ex.status === 'Not Completed')
      : exercises.filter(ex => ex.status === 'Completed');
    
    // Bước 2: Lọc theo status filter (chỉ áp dụng cho tab bài tập hiện tại)
    if (activeTab === 'current' && statusFilter !== 'all') {
      filtered = filtered.filter(ex => {
        if (statusFilter === 'Chưa hoàn thành') return ex.status === 'Not Completed';
        if (statusFilter === 'Thực hiện sai') return ex.status === 'In Progress';
        return true;
      });
    }

    // Bước 3: Sắp xếp theo sort option
    const sortedExercises = [...filtered];
    
    switch (sortOption) {
      case 'time-asc':
        sortedExercises.sort((a, b) => 
          new Date(a.assigned_date).getTime() - new Date(b.assigned_date).getTime()
        );
        break;
      case 'time-desc':
        sortedExercises.sort((a, b) => 
          new Date(b.assigned_date).getTime() - new Date(a.assigned_date).getTime()
        );
        break;
      case 'name-asc':
        sortedExercises.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name-desc':
        sortedExercises.sort((a, b) => b.name.localeCompare(a.name));
        break;
    }

    return sortedExercises;
  };

  // Hiển thị menu filter và sort
  const renderFilterSortMenu = () => {
    // Chỉ hiển thị menu khi ở tab bài tập hiện tại và showFilterMenu = true
    if (activeTab !== 'current' || !showFilterMenu) return null;

    return (
      <View style={styles.filterSortMenu}>
        <View style={styles.filterSection}>
          <Text style={[styles.filterTitle, { color: Colors[colorScheme].text }]}>Lọc theo trạng thái:</Text>
          <View style={styles.filterOptions}>
            <TouchableOpacity
              style={[
                styles.filterOption,
                statusFilter === 'all' && { backgroundColor: Colors.primary }
              ]}
              onPress={() => setStatusFilter('all')}
            >
              <Text style={[
                styles.filterOptionText,
                statusFilter === 'all' && { color: Colors.white }
              ]}>
                Tất cả
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.filterOption,
                statusFilter === 'Chưa hoàn thành' && { backgroundColor: Colors.primary }
              ]}
              onPress={() => setStatusFilter('Chưa hoàn thành')}
            >
              <Text style={[
                styles.filterOptionText,
                statusFilter === 'Chưa hoàn thành' && { color: Colors.white }
              ]}>
                Chưa hoàn thành
              </Text>
            </TouchableOpacity>
           
          </View>
        </View>

        <View style={styles.sortSection}>
          <Text style={[styles.sortTitle, { color: Colors[colorScheme].text }]}>Sắp xếp theo:</Text>
          <View style={styles.sortOptions}>
            <TouchableOpacity
              style={[
                styles.sortOption,
                sortOption === 'time-asc' && { backgroundColor: Colors.primary }
              ]}
              onPress={() => setSortOption('time-asc')}
            >
              <Text style={[
                styles.sortOptionText,
                sortOption === 'time-asc' && { color: Colors.white }
              ]}>
                Thời gian ↑
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.sortOption,
                sortOption === 'time-desc' && { backgroundColor: Colors.primary }
              ]}
              onPress={() => setSortOption('time-desc')}
            >
              <Text style={[
                styles.sortOptionText,
                sortOption === 'time-desc' && { color: Colors.white }
              ]}>
                Thời gian ↓
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.sortOption,
                sortOption === 'name-asc' && { backgroundColor: Colors.primary }
              ]}
              onPress={() => setSortOption('name-asc')}
            >
              <Text style={[
                styles.sortOptionText,
                sortOption === 'name-asc' && { color: Colors.white }
              ]}>
                Tên A-Z
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.sortOption,
                sortOption === 'name-desc' && { backgroundColor: Colors.primary }
              ]}
              onPress={() => setSortOption('name-desc')}
            >
              <Text style={[
                styles.sortOptionText,
                sortOption === 'name-desc' && { color: Colors.white }
              ]}>
                Tên Z-A
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  };

  // Add utility function to fetch exercises directly
  const fetchAndShowExercises = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/exercises/patient/67f547aa558195f5ff714715`);
      if (!response.ok) {
        throw new Error('Failed to fetch exercises');
      }
      const data = await response.json();
      
      // Show alert with API response
      Alert.alert(
        'Kết quả API',
        `Số bài tập: ${data.data.length}\n\nBài tập đầu tiên: ${data.data[0]?.name || 'Không có'}\n\nTrạng thái: ${data.data[0]?.status || 'N/A'}`,
        [{ text: 'OK' }]
      );
    } catch (error) {
      console.error('Error fetching exercises directly:', error);
      Alert.alert(
        'Lỗi',
        'Không thể kết nối đến API. Vui lòng kiểm tra server hoặc kết nối mạng.',
        [{ text: 'OK' }]
      );
    }
  };

  // Add a new function to check API connection
  const checkApiConnection = async () => {
    try {
      // Attempt to fetch API status
      const response = await fetchWithTimeout(
        `${API_BASE_URL}/api/v1/status`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        },
        5000 // 5 second timeout
      ).catch((error: Error) => {
        throw new Error(`Fetch failed: ${error.message}`);
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      Alert.alert(
        'Kết nối thành công',
        'API server đang hoạt động bình thường.',
        [{ text: 'OK' }]
      );
    } catch (error: any) {
      console.error('API connection check failed:', error);
      
      // Show detailed error message to help with debugging
      Alert.alert(
        'Lỗi kết nối API',
        `Không thể kết nối đến API server. 
        
Chi tiết lỗi: ${error.message || 'Không xác định'}
        
Vui lòng kiểm tra:
1. API server đã được khởi động chưa? (${API_BASE_URL})
2. Đảm bảo API server có thể truy cập từ mạng của thiết bị.
3. Kiểm tra console để biết thêm thông tin lỗi.
        
URL API hiện tại: ${API_BASE_URL}/api/v1/exercises/patient/[ID]`,
        [{ text: 'OK' }]
      );
    }
  };

  // Add comprehensive API test function
  const testAllApiEndpoints = async () => {
    try {
      // Hiển thị thông báo đang kiểm tra
      Alert.alert('Đang kiểm tra API', 'Vui lòng đợi...');
      
      // Chạy tất cả các kiểm tra
      const results = await runAllTests('67f547aa558195f5ff714715');
      
      // Hiển thị kết quả
      let resultMessage = '';
      
      // Kết quả kiểm tra kết nối
      resultMessage += `1. Kết nối API: ${results.connection.success ? '✅ OK' : '❌ Lỗi'}\n`;
      resultMessage += `   ${results.connection.message}\n\n`;
      
      // Kết quả kiểm tra lấy bài tập
      resultMessage += `2. Lấy bài tập: ${results.exercises.success ? '✅ OK' : '❌ Lỗi'}\n`;
      resultMessage += `   ${results.exercises.message}\n`;
      
      if (results.exercises.success && results.exercises.data?.data) {
        resultMessage += `\nSố bài tập: ${results.exercises.data.data.length}\n`;
        if (results.exercises.data.data.length > 0) {
          const firstExercise = results.exercises.data.data[0];
          resultMessage += `\nBài tập đầu tiên:\n`;
          resultMessage += `- Tên: ${firstExercise.name}\n`;
          resultMessage += `- Trạng thái: ${firstExercise.status}\n`;
          resultMessage += `- ID: ${firstExercise._id}`;
        }
      }
      
      Alert.alert(
        'Kết quả kiểm tra API',
        resultMessage,
        [{ text: 'OK' }]
      );
      
    } catch (error: any) {
      console.error('API test failed:', error);
      Alert.alert(
        'Kiểm tra thất bại',
        `Lỗi: ${error.message || 'Không xác định'}`,
        [{ text: 'OK' }]
      );
    }
  };

  // State for patient content - Moved from renderPatientContent to component root level
  const [cameraPermission, setCameraPermission] = useState<boolean | null>(null);
  const [recordingExercise, setRecordingExercise] = useState<ExerciseType | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [videoUri, setVideoUri] = useState<string | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState<string | null>(null);
  const [pickVideoModalVisible, setPickVideoModalVisible] = useState(false);
  // Fix the camera ref type - Moved from renderPatientContent to component root level
  const cameraRef = useRef<any>(null);

  // Request permissions for camera and media library
  useEffect(() => {
    if (userRole === 'patient') {
      (async () => {
        // Request media library permission instead of camera
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        setCameraPermission(status === 'granted');
        if (status !== 'granted') {
          console.log('Media library permission denied');
          Alert.alert(
            'Cần quyền truy cập', 
            'Ứng dụng cần quyền truy cập thư viện ảnh và video để thực hiện chức năng này.'
          );
        }
      })();
    }
  }, [userRole]);

  // Render patient-specific content
  const renderPatientContent = () => {
    const displayedExercises = getFilteredAndSortedExercises();
    
    // Handle starting a new video recording
    const startRecording = async () => {
      if (cameraRef.current) {
        setIsRecording(true);
        try {
          console.log("Starting recording...");
          // Simplify the recording options
          const video = await cameraRef.current.recordAsync({
            maxDuration: 10,
            mimeType: 'video/mp4'
          });
          console.log("Recording completed:", video.uri);
          setVideoUri(video.uri);
          setIsRecording(false);
          setShowCamera(false);
        } catch (error) {
          console.error('Error recording video:', error);
          setIsRecording(false);
          Alert.alert('Lỗi', 'Không thể quay video. Vui lòng thử lại.');
        }
      } else {
        console.error('Camera ref is null');
        Alert.alert('Lỗi', 'Không thể kết nối với camera. Vui lòng thử lại sau.');
      }
    };

    // Handle stopping a video recording
    const stopRecording = async () => {
      try {
        if (cameraRef.current && isRecording) {
          console.log("Stopping recording...");
          cameraRef.current.stopRecording();
          setIsRecording(false);
        }
      } catch (error) {
        console.error('Error stopping recording:', error);
        setIsRecording(false);
      }
    };

    // Handle picking a video from the device library
    const pickVideo = async () => {
      try {
        // Show message to user that we're starting the video selection process
        console.log('Opening video picker...');
        
        const result = await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Videos,
          allowsEditing: true,
          aspect: [4, 3],
          quality: 1,
          // Limit video duration to 30 seconds to avoid large file uploads
          videoMaxDuration: 30,
        });

        if (!result.canceled && result.assets && result.assets.length > 0) {
          const selectedVideo = result.assets[0];
          console.log('Selected video:', selectedVideo.uri);
          console.log('Video size:', selectedVideo.fileSize, 'bytes');
          console.log('Video duration:', selectedVideo.duration, 'seconds');
          
          // Display information about the selected video
          Alert.alert(
            'Đã chọn video',
            `Video đã được chọn và sẵn sàng để xử lý.\n\nKích thước: ${formatFileSize(selectedVideo.fileSize || 0)}\n${selectedVideo.duration ? `Thời lượng: ${Math.round(selectedVideo.duration)}s` : ''}`,
            [
              {
                text: 'Hủy',
                style: 'cancel',
              },
              {
                text: 'Xác nhận',
                onPress: () => {
                  setVideoUri(selectedVideo.uri);
                  setRecordingExercise(recordingExercise); // Maintain the current exercise context
                  setShowCamera(false);
                  setPickVideoModalVisible(false);
                }
              }
            ]
          );
        } else {
          console.log('Video selection cancelled');
        }
      } catch (error) {
        console.error('Error picking video:', error);
        Alert.alert('Lỗi', 'Không thể chọn video. Vui lòng thử lại.');
      }
    };
    
    // Format file size for display (convert bytes to KB/MB)
    const formatFileSize = (bytes: number) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Send the video to the AI prediction API
    const predictExercise = async () => {
      if (!videoUri || !recordingExercise) {
        Alert.alert('Lỗi', 'Vui lòng chọn video trước khi dự đoán.');
        return;
      }

      setIsPredicting(true);
      setPredictionResult(null);

      try {
        // Show a loading message
        console.log('Bắt đầu tải video lên...');
        
        // Create form data for the API request
        const formData = new FormData();
        
        // Get file info to include size in logs
        const videoInfo = await FileSystem.getInfoAsync(videoUri);
        console.log('Video info:', videoInfo);
        
        // Adding file to FormData with appropriate content type
        const fileType = videoUri.endsWith('.mp4') ? 'video/mp4' : 'video/quicktime';
        const fileName = videoUri.split('/').pop() || 'video.mp4';
        
        console.log('Preparing form data with filename:', fileName);
        
        // @ts-ignore - FormData type doesn't match React Native's implementation
        formData.append('video_file', {
          uri: videoUri,
          name: fileName,
          type: fileType,
        });
        
        // Add patient_id to form data
        // Use the actual user ID from auth store if available
        const patientId = user?.id || user?._id || '67fd4e833d275d212bd47e51';
        formData.append('patient_id', patientId);
        
        // Add exercise_id to form data
        formData.append('exercise_id', recordingExercise._id);
        
        console.log('Sending video for prediction. Patient ID:', patientId, 'Exercise ID:', recordingExercise._id);
        
        // Update UI with upload progress message
        setPredictionResult('⏳ Đang tải video lên máy chủ...');
        
        // Post to the prediction API
        const apiUrl = `${API_BASE_URL}/api/v1/predict/`;
        console.log('Uploading to:', apiUrl);
        
        const response = await fetch(apiUrl, {
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        console.log('Upload response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error(`API returned status code ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Prediction result:', result);
        
        // Set the prediction result
        if (result) {
          const isCorrect = result.prediction.is_match
          setPredictionResult(
            isCorrect 
              ? `✅ Đúng bài tập! (${result.prediction.predicted_motion})`
              : `❌ Sai bài tập! Hệ thống phát hiện bạn đang thực hiện: ${result.prediction.predicted_motion}`
          );
          
          // Show alert with result
          Alert.alert(
            isCorrect ? 'Thực hiện đúng' : 'Thực hiện sai',
            isCorrect 
              ? `Bạn đã thực hiện đúng bài tập ${recordingExercise.name}!` 
              : `Bài tập này yêu cầu ${recordingExercise.name}, nhưng bạn đang thực hiện ${result.prediction.predicted_motion}. Vui lòng xem hướng dẫn và thử lại.`,
            [{ text: 'OK' }]
          );
        } else {
          setPredictionResult('Không thể nhận dạng bài tập. Vui lòng thử lại.');
        }
      } catch (error) {
        console.error('Error predicting exercise:', error);
        setPredictionResult('❌ Lỗi khi dự đoán bài tập. Vui lòng thử lại.');
        Alert.alert(
          'Lỗi Upload', 
          `Không thể tải lên hoặc dự đoán bài tập. Lỗi: ${error instanceof Error ? error.message : 'Không xác định'}`
        );
      } finally {
        setIsPredicting(false);
      }
    };

    // Reset all recording/prediction state
    const resetRecording = () => {
      setVideoUri(null);
      setRecordingExercise(null);
      setPredictionResult(null);
    };

    // Render the camera view for recording
    const renderCameraView = () => {
      // Create a simple placeholder UI instead of using the Camera component
      return (
        <View style={{ 
          flex: 1, 
          backgroundColor: '#000', 
          justifyContent: 'center', 
          alignItems: 'center',
          padding: 20 
        }}>
          <Text style={{ 
            color: 'white', 
            fontSize: 18, 
            fontWeight: 'bold', 
            marginBottom: 20,
            textAlign: 'center' 
          }}>
            Camera Preview Placeholder
          </Text>
          
          <View style={{
            width: '100%',
            height: 300,
            backgroundColor: '#333',
            borderRadius: 12,
            justifyContent: 'center',
            alignItems: 'center',
            marginBottom: 30
          }}>
            <Ionicons name="camera" size={80} color="#666" />
          </View>

          <Text style={{ 
            color: 'white', 
            fontSize: 14, 
            marginBottom: 30,
            textAlign: 'center' 
          }}>
            Do bị lỗi với thư viện expo-camera, chúng tôi đã tạm thời thay thế bằng chức năng chọn video từ thư viện.
          </Text>
          
          <View style={{
            flexDirection: 'row',
            width: '100%',
            justifyContent: 'space-around'
          }}>
            <TouchableOpacity
              style={{
                backgroundColor: '#f44336',
                paddingVertical: 15,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
              onPress={() => setShowCamera(false)}
            >
              <Text style={{ color: 'white', fontWeight: 'bold' }}>Hủy</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={{
                backgroundColor: Colors.primary,
                paddingVertical: 15,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
              onPress={async () => {
                // Use ImagePicker to get a video directly instead of using Camera
                try {
                  const result = await ImagePicker.launchImageLibraryAsync({
                    mediaTypes: ImagePicker.MediaTypeOptions.Videos,
                    allowsEditing: true,
                    aspect: [4, 3],
                    quality: 1,
                  });

                  if (!result.canceled && result.assets && result.assets.length > 0) {
                    console.log("Selected video:", result.assets[0].uri);
                    setVideoUri(result.assets[0].uri);
                    setShowCamera(false);
                  } else {
                    console.log("Video selection canceled");
                  }
                } catch (error) {
                }
              }}
            >
              <Text style={{ color: 'white', fontWeight: 'bold' }}>Chọn Video</Text>
            </TouchableOpacity>
          </View>
        </View>
      );
    };

    // Render video preview and prediction controls
    const renderVideoPreview = () => {
      if (!videoUri) return null;

      // Get filename from URI for display
      const fileName = videoUri.split('/').pop() || 'video.mp4';

      return (
        <View style={{ 
          backgroundColor: 'rgba(0,0,0,0.9)', 
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <View style={{
            width: '90%',
            backgroundColor: 'white',
            borderRadius: 12,
            padding: 20,
            alignItems: 'center'
          }}>
            <Text style={{ 
              fontSize: 18, 
              fontWeight: 'bold', 
              marginBottom: 20,
              textAlign: 'center'
            }}>
              Video đã sẵn sàng cho bài tập: {recordingExercise ? getExerciseDisplayName(recordingExercise.name) : ''}
            </Text>
            
            {/* Video thumbnail */}
            <View 
              style={{ 
                width: 200, 
                height: 150, 
                marginBottom: 20,
                borderRadius: 8,
                backgroundColor: '#e0e0e0',
                justifyContent: 'center',
                alignItems: 'center',
                borderWidth: 1,
                borderColor: '#cccccc'
              }}
            >
              <Ionicons name="videocam" size={40} color="#666666" />
              <Text style={{ marginTop: 8, fontSize: 14, color: '#666666' }}>
                {fileName}
              </Text>
            </View>
            
            {/* Display additional video information */}
            <View style={{
              backgroundColor: '#f5f5f5',
              padding: 10,
              borderRadius: 8,
              marginBottom: 20,
              width: '100%',
              alignItems: 'center'
            }}>
              <Text style={{ fontSize: 14, color: '#666', marginBottom: 5 }}>
                Video đã chọn sẵn sàng để tải lên
              </Text>
              <Text style={{ fontSize: 12, color: '#999' }}>
                Nhấn "Tải lên & Phân tích" để bắt đầu
              </Text>
            </View>
            
            {predictionResult && (
              <View style={{ 
                padding: 10, 
                backgroundColor: predictionResult.includes('✅') ? '#e6f7e6' : 
                               predictionResult.includes('❌') ? '#ffebee' : 
                               predictionResult.includes('⏳') ? '#e3f2fd' : '#f5f5f5',
                borderRadius: 8,
                marginBottom: 20,
                width: '100%'
              }}>
                <Text style={{ 
                  fontSize: 16, 
                  textAlign: 'center',
                  color: predictionResult.includes('✅') ? '#2e7d32' : 
                         predictionResult.includes('❌') ? '#c62828' : 
                         predictionResult.includes('⏳') ? '#1565c0' : '#666666'
                }}>
                  {predictionResult.replace(recordingExercise?.name || '', getExerciseDisplayName(recordingExercise?.name || ''))}
                </Text>
              </View>
            )}
            
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', width: '100%' }}>
              <TouchableOpacity
                style={{
                  backgroundColor: '#f44336',
                  paddingVertical: 10,
                  paddingHorizontal: 20,
                  borderRadius: 8,
                  marginRight: 10,
                  flex: 1,
                  alignItems: 'center'
                }}
                onPress={resetRecording}
              >
                <Text style={{ color: 'white', fontWeight: 'bold' }}>Hủy</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={{
                  backgroundColor: isPredicting ? '#bdbdbd' : Colors.primary,
                  paddingVertical: 10,
                  paddingHorizontal: 20,
                  borderRadius: 8,
                  flex: 1,
                  alignItems: 'center'
                }}
                onPress={predictExercise}
                disabled={isPredicting}
              >
                {isPredicting ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <Text style={{ color: 'white', fontWeight: 'bold' }}>
                    {predictionResult ? 'Tải lên lại' : 'Tải lên & Phân tích'}
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      );
    };

    // Render the action sheet for an exercise
    const renderExerciseActions = (exercise: ExerciseType) => {
      if (recordingExercise?._id !== exercise._id) return null;
      
      // Kiểm tra xem ứng dụng đang chạy trên web hay không
      const isWeb = Platform.OS === 'web';
      
      // Hàm xử lý khi file được chọn trên web
      const handleWebFileChange = (event: any) => {
        if (!event.target.files || event.target.files.length === 0) return;
        
        const file = event.target.files[0];
        console.log('File selected from computer:', file.name, file.type, file.size);
        
        // Kiểm tra nếu file không phải là video
        if (!file.type.startsWith('video/')) {
          Alert.alert('Lỗi', 'Vui lòng chọn file video hợp lệ');
          return;
        }
        
        // Tạo URI từ file đã chọn
        const fileUri = URL.createObjectURL(file);
        
        // Hiển thị thông tin file đã chọn
        Alert.alert(
          'Đã chọn video từ máy tính',
          `Tên file: ${file.name}\nKích thước: ${formatFileSize(file.size)}`,
          [
            {
              text: 'Hủy',
              style: 'cancel',
            },
            {
              text: 'Xác nhận',
              onPress: () => {
                setVideoUri(fileUri);
                setRecordingExercise(exercise);
                // Đóng modal sau khi chọn xong
                setRecordingExercise(null);
              }
            }
          ]
        );
      };
      
      return (
        <Modal
          visible={pickVideoModalVisible}
          transparent={true}
          animationType="slide"
        >
          <View style={{
            flex: 1,
            justifyContent: 'flex-end',
            backgroundColor: 'rgba(0,0,0,0.5)'
          }}>
            <View style={{
              backgroundColor: 'white',
              borderTopLeftRadius: 20,
              borderTopRightRadius: 20,
              padding: 20
            }}>
              <Text style={{
                fontSize: 18,
                fontWeight: 'bold',
                marginBottom: 20,
                textAlign: 'center'
              }}>
                Ghi lại bài tập: {getExerciseDisplayName(exercise.name)}
              </Text>
              
              <Text style={{
                fontSize: 14,
                marginBottom: 20,
                textAlign: 'center',
                color: '#666'
              }}>
                Chọn cách bạn muốn ghi lại bài tập này
              </Text>
              
              {/* Remove or hide camera option since it's not working */}
              {false && (
                <TouchableOpacity
                  style={{
                    backgroundColor: '#f5f5f5',
                    padding: 15,
                    borderRadius: 10,
                    flexDirection: 'row',
                    alignItems: 'center',
                    marginBottom: 10
                  }}
                  onPress={() => {
                    setShowCamera(true);
                  }}
                >
                  <Ionicons name="camera" size={24} color={Colors.primary} style={{marginRight: 10}} />
                  <Text style={{fontSize: 16}}>Quay video mới</Text>
                </TouchableOpacity>
              )}
              
              <TouchableOpacity
                style={{
                  backgroundColor: '#f5f5f5',
                  padding: 15,
                  borderRadius: 10,
                  flexDirection: 'row',
                  alignItems: 'center',
                  marginBottom: 10
                }}
                onPress={pickVideo}
              >
                <Ionicons name="phone-portrait" size={24} color={Colors.primary} style={{marginRight: 10}} />
                <Text style={{fontSize: 16}}>Chọn video từ thiết bị di động</Text>
              </TouchableOpacity>
              
              {/* Thêm tùy chọn upload từ máy tính khi chạy trên web */}
              {isWeb && (
                <View>
                  <TouchableOpacity
                    style={{
                      backgroundColor: '#f5f5f5',
                      padding: 15,
                      borderRadius: 10,
                      flexDirection: 'row',
                      alignItems: 'center',
                      marginBottom: 20
                    }}
                    onPress={() => {
                      // Tạo một input file tạm thời và kích hoạt nó
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.accept = 'video/*';
                      input.onchange = handleWebFileChange;
                      input.click();
                    }}
                  >
                    <Ionicons name="desktop-outline" size={24} color={Colors.primary} style={{marginRight: 10}} />
                    <Text style={{fontSize: 16}}>Chọn video từ máy tính này</Text>
                  </TouchableOpacity>
                </View>
              )}
              
              <TouchableOpacity
                style={{
                  padding: 15,
                  borderRadius: 10,
                  flexDirection: 'row',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderTopWidth: 1,
                  borderTopColor: '#eee'
                }}
                onPress={() => setPickVideoModalVisible(false)}
              >
                <Text style={{fontSize: 16, color: '#666'}}>Hủy</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      );
    };

    const renderExerciseItem = ({ item }: { item: ExerciseType }) => (
      <TouchableOpacity
        style={styles.exerciseItem}
        onPress={() => { 
          // Hiển thị chi tiết bài tập khi click vào
          Alert.alert(
            getExerciseDisplayName(item.name),
            `Mô tả: ${item.description}\n\nNgày giao: ${new Date(item.assigned_date).toLocaleDateString('vi-VN')}\n\nHạn hoàn thành: ${new Date(item.due_date).toLocaleDateString('vi-VN')}\n\nTrạng thái: ${item.status === 'Pending' ? 'Chưa hoàn thành' : item.status === 'Completed' ? 'Đã hoàn thành' : 'Đang thực hiện'}`,
            [
              { text: 'Đóng', style: 'cancel' },
              { text: 'Thực hiện bài tập', onPress: () => {
                setRecordingExercise(item);
                setPickVideoModalVisible(true);
              } }
            ]
          );
        }}
        // onPress={() => 
        //   router.push({
        //     pathname: '/(tabs)/exercise-detail',
        //     params: { id: item._id, exerciseData:JSON.stringify(item) }
        //   })
        // }
      >
        <View style={styles.exerciseInfo}>
          <Text style={styles.exerciseName}>{getExerciseDisplayName(item.name)}</Text>
          <Text style={styles.exerciseDetailText}>Mô tả: {item.description}</Text>
          {item.assigned_date && (
            <Text style={styles.exerciseDetailText}>
              Ngày giao: {new Date(item.assigned_date).toLocaleDateString('vi-VN')}
            </Text>
          )}
          {item.due_date && (
            <Text style={styles.exerciseDetailText}>
              Hạn hoàn thành: {new Date(item.due_date).toLocaleDateString('vi-VN')}
            </Text>
          )}
          <View style={{
            flexDirection: 'row', 
            alignItems: 'center', 
            marginTop: 5,
            backgroundColor: item.status === 'Pending' ? '#FFC107' : '#4CAF50',
            paddingVertical: 3,
            paddingHorizontal: 8,
            borderRadius: 4,
            alignSelf: 'flex-start'
          }}>
            <Text style={{ 
              fontSize: 12, 
              color: 'white', 
              fontWeight: 'bold'
            }}>
              {item.status === 'Pending' ? 'Chưa hoàn thành' : 
              item.status === 'Completed' ? 'Đã hoàn thành' : 'Đang thực hiện'}
            </Text>
          </View>
        </View>
        <View style={{ flexDirection: 'column', alignItems: 'center' }}>
          <TouchableOpacity 
            style={{
              backgroundColor: Colors.primary,
              borderRadius: 20,
              width: 40,
              height: 40,
              justifyContent: 'center',
              alignItems: 'center',
              marginBottom: 8
            }}
            // onPress={() => setRecordingExercise(item)}
          >
            <Ionicons name="camera" size={22} color="#fff" />
          </TouchableOpacity>
          <Ionicons name="chevron-forward" size={20} color={ExtendedColors.darkGray} />
        </View>
      </TouchableOpacity>
    );

    return (
      <View style={styles.contentSection}>
        {showCamera && renderCameraView()}
        {videoUri && renderVideoPreview()}
        {recordingExercise && renderExerciseActions(recordingExercise)}
        
        <View style={{padding: 16, marginBottom: 0}}>
          <Text style={{fontSize: 18, fontWeight: 'bold', marginBottom: 8}}>
            Danh sách bài tập của bạn
          </Text>
          <Text style={{fontSize: 14, color: '#666'}}>
            Bạn có {exercises.length} bài tập
          </Text>
        </View>
        
        {/* Tabs for Current and History */}
        <View style={styles.tabContainer}>
          <TouchableOpacity 
            style={[
              styles.tab, 
              activeTab === 'current' && styles.activeTab,
              activeTab === 'current' && { backgroundColor: Colors.primary }
            ]} 
            onPress={() => setActiveTab('current')}
          >
            <Text style={[
              styles.tabText, 
              activeTab === 'current' && styles.activeTabText,
              activeTab === 'current' && { color: Colors.white }
            ]}>
              Bài tập hiện tại
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[
              styles.tab, 
              activeTab === 'history' && styles.activeTab,
              activeTab === 'history' && { backgroundColor: Colors.primary }
            ]} 
            onPress={() => setActiveTab('history')}
          >
            <Text style={[
              styles.tabText, 
              activeTab === 'history' && styles.activeTabText,
              activeTab === 'history' && { color: Colors.white }
            ]}>
              Lịch sử bài tập
            </Text>
          </TouchableOpacity>
        </View>

        {/* Filter and Sort button (Chỉ hiển thị cho tab bài tập hiện tại) */}
        {activeTab === 'current' && exercises.length > 0 && (
          <TouchableOpacity 
            style={styles.filterSortButton}
            onPress={() => setShowFilterMenu(!showFilterMenu)}
          >
            <Text style={styles.filterSortButtonText}>
              {showFilterMenu ? 'Ẩn bộ lọc' : 'Lọc & Sắp xếp'}
            </Text>
          </TouchableOpacity>
        )}

        {/* Filter and Sort Menu */}
        {renderFilterSortMenu()}


        {isLoadingExercises ? (
          <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
            <ActivityIndicator size="large" color={Colors.primary} />
            <Text style={{ marginTop: 12, fontSize: 16, color: '#666' }}>Đang tải danh sách bài tập...</Text>
          </View>
        ) : exercisesError ? (
          <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
            <Text style={{ fontSize: 16, color: ExtendedColors.danger, textAlign: 'center', marginBottom: 16 }}>{exercisesError}</Text>
            <TouchableOpacity 
              style={{ backgroundColor: Colors.primary, paddingVertical: 8, paddingHorizontal: 16, borderRadius: 8 }}
              onPress={()=>fetchExercises(user!._id!)}
            >
              <Text style={{ color: 'white', fontWeight: 'bold' }}>Thử lại</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <>
            {displayedExercises.length === 0 ? (
              <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
                <Ionicons name="fitness-outline" size={60} color="#ccc" />
                <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 16, marginBottom: 8, color: '#333' }}>
                  Chưa có bài tập nào
                </Text>
                <Text style={{ fontSize: 14, color: '#666', textAlign: 'center' }}>
                  {activeTab === 'current' 
                    ? 'Bạn chưa được giao bài tập nào.'
                    : 'Bạn chưa có lịch sử bài tập nào.'}
                </Text>
                <TouchableOpacity 
                  style={{ 
                    backgroundColor: Colors.primary, 
                    paddingVertical: 8, 
                    paddingHorizontal: 16, 
                    borderRadius: 8,
                    marginTop: 16
                  }}
                  onPress={()=>fetchExercises(user!._id!)}
                >
                  <Text style={{ color: 'white', fontWeight: 'bold' }}>Làm mới</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <FlatList
                data={displayedExercises}
                renderItem={renderExerciseItem}
                keyExtractor={item => item._id || `${item.name}-${item.assigned_date}`}
                contentContainerStyle={{
                  padding: 16,
                  paddingBottom: 80
                }}
              />
            )}
          </>
        )}
      </View>
    );
  };

  // Fetch danh sách bệnh nhân khi component mount
  useEffect(() => {
    // Update this check to be case-insensitive 
    if ((userRole?.toLowerCase() === 'doctor' || userRole?.toLowerCase() === 'docter') && user?.id) {
      log('Fetching patient list for doctor:', user.id);
      fetchPatientList();
    }
  }, [userRole, user]);

  // Hàm fetch danh sách bệnh nhân
  const fetchPatientList = async () => {
    if (!user?.id) {
      log('Not fetching patients - no user ID available');
      return;
    }
    
    setIsLoadingPatients(true);
    setPatientsError(null);
    
    try {
      log('Fetching patients list');
      
      // Sử dụng API endpoint cho danh sách bệnh nhân
      const url = `${API_BASE_URL}/api/v1/users/patients`;
      log('Requesting API:', url);
      
      const response = await fetchWithFallback(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`API returned status code ${response.status}`);
      }
      
      const data = await response.json();
      log('Received API response for patients:', data);
      
      // Kiểm tra dữ liệu trả về có đúng định dạng không
      if (Array.isArray(data)) {
        // Dữ liệu là một mảng như mong đợi
        log('Found', data.length, 'patients in response');
        setPatients(data);
      } else if (data && Array.isArray(data.data)) {
        // Dữ liệu có thể được đóng gói trong một trường 'data'
        log('Found', data.data.length, 'patients in response.data');
        setPatients(data.data);
      } else {
        // Không có dữ liệu hoặc định dạng không như mong đợi, dùng dữ liệu mẫu
        log('Response format unexpected, using mock data:', data);
        setPatients([]);
      }
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      
      // Try using the sample data you provided
      try {
        const hardcodedData = [
          {"email":"duongbaokhanh@gmail.com","full_name":"Dương Bảo Khánh","role":"patient","_id":"67fd4e833d275d212bd47e51","created_at":"2025-04-14T18:05:55.903000","updated_at":"2025-04-14T18:05:55.903000"},
          {"email":"duongbaokhanh2@example.com","full_name":"Duong Bao Khanh","role":"patient ","_id":"67fd4f383178c792a8ea939b","created_at":"2025-04-14T18:08:56.337000","updated_at":"2025-04-14T18:08:56.337000"}
        ];
        
        log('Using hardcoded patient data as fallback');
        setPatients(hardcodedData);
        setPatientsError(null);
      } catch (fallbackError) {
        setPatientsError('Không thể tải danh sách bệnh nhân: ' + (error instanceof Error ? error.message : String(error)));
        
        // Nếu API lỗi, sử dụng dữ liệu mẫu để hiển thị UI
        log('API error occurred, using mock data for UI display');
        setPatients([]);
      }
    } finally {
      setIsLoadingPatients(false);
    }
  };

  // --- Create Exercise Modal Logic ---
  const handleCreateExerciseSubmit = (formData: ExerciseFormData) => {
    // Kiểm tra nếu thiếu dữ liệu
    if (!formData.exerciseName || !formData.exerciseDescription || !formData.selectedPatientId) {
      Alert.alert('Thiếu thông tin', 'Vui lòng điền đầy đủ thông tin bài tập và chọn bệnh nhân.');
      return;
    }
    
    // Tạo object bài tập để gửi lên server
    const exerciseData: Exercise = {
      name: formData.exerciseName,
      description: formData.exerciseDescription,
      assigned_by: user?.id || 'unknown', // Sử dụng doctor ID
      assigned_to: formData.selectedPatientId,
      assigned_date: formData.assignedDate.toISOString(),
      due_date: formData.dueDate.toISOString(),
      status: 'Pending'
    };
    
    // Gọi hàm để tạo bài tập
    createExercise(exerciseData);
  };

  const createExercise = async (exerciseData: Exercise) => {
    try {
      // Format the payload exactly as the backend expects
      const formattedPayload = {
        name: exerciseData.name,
        description: exerciseData.description,
        assigned_by: exerciseData.assigned_by,
        assigned_to: exerciseData.assigned_to,
        assigned_date: exerciseData.assigned_date,
        due_date: exerciseData.due_date
      };

      console.log('Sending payload to API:', formattedPayload);
      
      const response = await fetchWithFallback(`${API_BASE_URL}/api/v1/exercises/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formattedPayload),
      });

      if (response.ok) {
        Alert.alert('Thành công', 'Đã tạo bài tập mới');
        setShowCreateExerciseModal(false);
        resetCreateExerciseForm();
        // Optionally: Refresh patient list or exercise list if needed
      } else {
        const errorText = await response.text();
        let errorMessage = 'Failed to create exercise';
        
        try {
          // Try to parse the error response as JSON
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.error || errorData.message || errorMessage;
          console.error('Error response:', errorData);
        } catch (e) {
          // If not JSON, use the raw text
          console.error('Error response (text):', errorText);
        }
        
        console.error(`API Error ${response.status}: ${errorMessage}`);
        throw new Error(`${response.status} ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error creating exercise:', error);
      const errorMessage = error instanceof Error ? error.message : 'Vui lòng thử lại sau.';
      Alert.alert('Lỗi', `Không thể tạo bài tập: ${errorMessage}`);
    }
  };

  const resetCreateExerciseForm = () => {
    setExerciseName('');
    setExerciseDescription('');
    setSelectedPatientForExercise('');
    setAssignedDate(new Date());
    setDueDate(new Date());
  };

  const handlePatientSelect = useCallback((id: string) => {
    // Toggle selection - if already selected, unselect it
    if (selectedPatientForExercise === id) {
      setSelectedPatientForExercise('');
    } else {
      setSelectedPatientForExercise(id);
    }
  }, [selectedPatientForExercise]);

  const keyExtractor = useCallback((item: Patient) => item._id, []);

  // Interface for form data
  interface ExerciseFormData {
    exerciseName: string;
    exerciseDescription: string;
    assignedDate: Date;
    dueDate: Date;
    selectedPatientId: string;
  }

  // CreateExerciseModalComponent props interface
  interface CreateExerciseModalProps {
    visible: boolean;
    onClose: () => void;
    onSubmit: (data: ExerciseFormData) => void;
    initialData: ExerciseFormData;
    patients: Patient[];
    isLoadingPatients: boolean;
    patientsError: string | null;
  }

  // Define the CreateExerciseModal component outside the main component
  const CreateExerciseModalComponent: React.FC<CreateExerciseModalProps> = ({ 
    visible, 
    onClose, 
    onSubmit,
    initialData,
    patients,
    isLoadingPatients,
    patientsError
  }) => {
    // Local state for the form
    const [exerciseName, setExerciseName] = useState(initialData?.exerciseName || '');
    const [exerciseDescription, setExerciseDescription] = useState(initialData?.exerciseDescription || '');
    const [assignedDate, setAssignedDate] = useState(initialData?.assignedDate || new Date());
    const [dueDate, setDueDate] = useState(initialData?.dueDate || new Date());
    const [selectedPatientId, setSelectedPatientId] = useState(initialData?.selectedPatientId || '');
    const [showAssignedDatePicker, setShowAssignedDatePicker] = useState(false);
    const [showDueDatePicker, setShowDueDatePicker] = useState(false);
    const [showExerciseDropdown, setShowExerciseDropdown] = useState(false);
    const [showPatientDropdown, setShowPatientDropdown] = useState(false);
    
    // Bệnh nhân mẫu để hiển thị trong modal
    const displayPatients = patients.length > 0 ? patients : [];

    // Ref for the patient dropdown container
    const patientDropdownRef = useRef<View | null>(null);
    
    // Close dropdowns when clicking outside
    useEffect(() => {
      const handleOutsideClick = (event: any) => {
        // Note: This will only work in web environments, not in native
        if (Platform.OS === 'web' && patientDropdownRef.current && event.target) {
          // Handle web environment click outside
          const ref = patientDropdownRef.current as any;
        }
      };
      
      if (showPatientDropdown && Platform.OS === 'web') {
        document.addEventListener('mousedown', handleOutsideClick);
      }
      
      return () => {
        if (Platform.OS === 'web') {
          document.removeEventListener('mousedown', handleOutsideClick);
        }
      };
    }, [showPatientDropdown]);

    // Cập nhật phần hiển thị và xử lý cho danh sách bệnh nhân
    const handleModalPatientSelect = useCallback((id: string) => {
      if (selectedPatientId === id) {
        setSelectedPatientId('');
      } else {
        setSelectedPatientId(id);
      }
    }, [selectedPatientId]);

    // Cập nhật renderPatientItem để sử dụng displayPatients
    const modalRenderPatientItem = useCallback(({ item }: { item: Patient }) => (
          <TouchableOpacity 
        style={{
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: 12,
          borderBottomWidth: 1,
          borderBottomColor: '#f0f0f0',
          backgroundColor: selectedPatientId === item._id ? 'rgba(33, 150, 243, 0.1)' : 'white',
        }}
        onPress={() => handleModalPatientSelect(item._id)}
      >
        <Text style={{ fontSize: 16, color: '#333' }}>{item.full_name}</Text>
        <Ionicons
          name={selectedPatientId === item._id ? "checkmark-circle" : "ellipse-outline"}
          size={22}
          color={selectedPatientId === item._id ? Colors.primary : "#aaa"}
        />
      </TouchableOpacity>
    ), [selectedPatientId, handleModalPatientSelect]);

    const memoizedHandleAssignedDateChange = useCallback((event: any, selectedDate?: Date) => {
      setShowAssignedDatePicker(Platform.OS === 'ios');
      if (selectedDate) {
        setAssignedDate(selectedDate);
      }
    }, []);

    const memoizedHandleDueDateChange = useCallback((event: any, selectedDate?: Date) => {
      setShowDueDatePicker(Platform.OS === 'ios');
      if (selectedDate) {
        setDueDate(selectedDate);
      }
    }, []);

    const memoizedHandleSubmit = useCallback(() => {
      // Đóng modal trước khi gọi onSubmit để tránh các vấn đề với re-render
      onClose();
      
      // Gọi hàm onSubmit với form data sau khi đã đóng modal
      setTimeout(() => {
        onSubmit({
          exerciseName,
          exerciseDescription,
          assignedDate,
          dueDate,
          selectedPatientId
        });
      }, 100);
    }, [exerciseName, exerciseDescription, assignedDate, dueDate, selectedPatientId, onClose, onSubmit]);

    // Tạo một useEffect để cập nhật memoizedHandleSubmit khi exerciseName thay đổi
    useEffect(() => {
      // Để memoizedHandleSubmit được cập nhật khi exerciseName thay đổi
    }, [exerciseName]);

    const isSubmitDisabled = !exerciseName || !exerciseDescription || !selectedPatientId || isLoadingPatients;

    // Thêm danh sách các bài tập mẫu
    const predefinedExercises = [
      { id: "Xemxaxemgan", name: "Xem xa xem gần" },
      { id: "Ngoithangbangtrengot", name: "Ngồi thăng bằng trên gót" },
      { id: "Dangchanraxanghiengminh", name: "Dang chân ra xa nghiêng mình" },
      { id: "Sodatvuonlen", name: "Sờ đất vươn lên" }
    ];

    // Thêm hàm xử lý khi chọn bài tập từ dropdown
    const handleSelectExercise = useCallback((exercise: {id: string, name: string}) => {
      setExerciseName(exercise.id);
      setShowExerciseDropdown(false);
    }, []);

    return (
      <Modal
        visible={visible}
        animationType="slide"
        transparent={true}
        onRequestClose={onClose}
      >
        <View style={{
          flex: 1,
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'rgba(0,0,0,0.5)',
        }}>
          <View style={{
            width: '90%',
            height: '80%',
            backgroundColor: 'white',
            borderRadius: 12,
            padding: 0,
            overflow: 'hidden',
          }}>
            {/* Header */}
            <View style={{
              flexDirection: 'row',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 16,
              borderBottomWidth: 1,
              borderBottomColor: '#eee',
              backgroundColor: 'white',
            }}>
              <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Tạo bài tập mới</Text>
              <TouchableOpacity onPress={onClose}>
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            {/* Content */}
            <View style={{ flex: 1 }}>
              {/* <ScrollView> */}
                <View style={{ padding: 16 }}>
                  {/* Exercise Name */}
                  <View style={{ marginBottom: 16 }}>
                    <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Tên bài tập</Text>
                    <View>
                      <TouchableOpacity
                        style={{
                          borderWidth: 1,
                          borderColor: '#ddd',
                          borderRadius: 8,
                          padding: 12,
                          backgroundColor: 'white',
                          flexDirection: 'row',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                        onPress={() => setShowExerciseDropdown(!showExerciseDropdown)}
                      >
                        <Text style={{ fontSize: 16, color: exerciseName ? '#333' : '#999' }}>
                          {exerciseName 
                            ? predefinedExercises.find(ex => ex.id === exerciseName)?.name || exerciseName
                            : "Chọn tên bài tập..."}
            </Text>
                        <Ionicons 
                          name={showExerciseDropdown ? "chevron-up" : "chevron-down"} 
                          size={20} 
                          color={Colors.primary} 
                        />
          </TouchableOpacity>
                      
                      {showExerciseDropdown && (
                        <View style={{
                          position: 'absolute',
                          top: 45,
                          left: 0,
                          right: 0,
                          backgroundColor: 'white',
                          borderWidth: 1,
                          borderColor: '#ddd',
                          borderRadius: 8,
                          zIndex: 1000,
                          elevation: 5,
                          shadowColor: '#000',
                          shadowOffset: { width: 0, height: 2 },
                          shadowOpacity: 0.1,
                          shadowRadius: 4,
                          maxHeight: 200
                        }}>
                          {/* <ScrollView nestedScrollEnabled={true}> */}
                            {predefinedExercises.map((exercise) => (
                              <TouchableOpacity
                                key={exercise.id}
                                style={{
                                  padding: 12,
                                  borderBottomWidth: 1,
                                  borderBottomColor: '#f0f0f0',
                                  backgroundColor: exerciseName === exercise.id ? 'rgba(33, 150, 243, 0.1)' : 'white',
                                }}
                                onPress={() => handleSelectExercise(exercise)}
                              >
                                <Text style={{ fontSize: 16, color: '#333' }}>{exercise.name}</Text>
                              </TouchableOpacity>
                            ))}
                          {/* </ScrollView> */}
                        </View>
                      )}
                      
                      {exerciseName && predefinedExercises.find(ex => ex.id === exerciseName) && (
                        <View style={{ marginTop: 8, paddingHorizontal: 4 }}>
                          <Text style={{ fontSize: 14, color: Colors.primary, fontStyle: 'italic' }}>
                            Bài tập đã chọn: <Text style={{ fontWeight: 'bold' }}>{predefinedExercises.find(ex => ex.id === exerciseName)?.name}</Text>
            </Text>
          </View>
                      )}
                    </View>
                  </View>

                  {/* Exercise Description */}
                  <View style={{ marginBottom: 16 }}>
                    <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Mô tả bài tập</Text>
                    <TextInput
                      style={{
                        borderWidth: 1,
                        borderColor: '#ddd',
                        borderRadius: 8,
                        padding: 12,
                        fontSize: 16,
                        backgroundColor: 'white',
                      }}
                      placeholder="Nhập mô tả chi tiết về bài tập..."
                      value={exerciseDescription}
                      onChangeText={setExerciseDescription}
                      multiline
                      numberOfLines={4}
      />
    </View>

                  {/* Assigned Date */}
                  <View style={{ marginBottom: 16 }}>
                    <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Ngày giao</Text>
                    <TouchableOpacity
                      style={{
                        flexDirection: 'row',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        borderWidth: 1,
                        borderColor: '#ddd',
                        borderRadius: 8,
                        padding: 12,
                        backgroundColor: 'white',
                      }}
                      onPress={() => setShowAssignedDatePicker(true)}
                    >
                      <Text style={{ fontSize: 16 }}>{assignedDate.toLocaleDateString('vi-VN')}</Text>
                      <Ionicons name="calendar-outline" size={20} color={Colors.primary} />
                    </TouchableOpacity>
                    
                    {showAssignedDatePicker && (
                      <View style={{ marginTop: 8 }}>
                        <DateTimePicker
                          value={assignedDate}
                          mode="date"
                          display="default"
                          onChange={memoizedHandleAssignedDateChange}
                        />
                        {Platform.OS === 'ios' && (
                          <TouchableOpacity
                            style={{
                              alignSelf: 'flex-end',
                              backgroundColor: Colors.primary,
                              paddingVertical: 6,
                              paddingHorizontal: 12,
                              borderRadius: 6,
                              marginTop: 8,
                            }}
                            onPress={() => setShowAssignedDatePicker(false)}
                          >
                            <Text style={{ color: 'white', fontWeight: 'bold' }}>Xong</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    )}
                  </View>

                  {/* Due Date */}
                  <View style={{ marginBottom: 16 }}>
                    <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Hạn hoàn thành</Text>
                    <TouchableOpacity
                      style={{
                        flexDirection: 'row',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        borderWidth: 1,
                        borderColor: '#ddd',
                        borderRadius: 8,
                        padding: 12,
                        backgroundColor: 'white',
                      }}
                      onPress={() => setShowDueDatePicker(true)}
                    >
                      <Text style={{ fontSize: 16 }}>{dueDate.toLocaleDateString('vi-VN')}</Text>
                      <Ionicons name="calendar-outline" size={20} color={Colors.primary} />
                    </TouchableOpacity>
                    
                    {showDueDatePicker && (
                      <View style={{ marginTop: 8 }}>
                        <DateTimePicker
                          value={dueDate}
                          mode="date"
                          display="default"
                          onChange={memoizedHandleDueDateChange}
                        />
                        {Platform.OS === 'ios' && (
                          <TouchableOpacity
                            style={{
                              alignSelf: 'flex-end',
                              backgroundColor: Colors.primary,
                              paddingVertical: 6,
                              paddingHorizontal: 12,
                              borderRadius: 6,
                              marginTop: 8,
                            }}
                            onPress={() => setShowDueDatePicker(false)}
                          >
                            <Text style={{ color: 'white', fontWeight: 'bold' }}>Xong</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    )}
                  </View>

                  {/* Patient Selection */}
                  <View style={{ marginBottom: 16 }}>
                    <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Chọn bệnh nhân</Text>
                    <View ref={patientDropdownRef}>
                      <TouchableOpacity
                        style={{
                          borderWidth: 1,
                          borderColor: '#ddd',
                          borderRadius: 8,
                          padding: 12,
                          backgroundColor: 'white',
                          flexDirection: 'row',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                        onPress={() => {
                          // Close all other dropdowns first
                          if (showExerciseDropdown) setShowExerciseDropdown(false);
                          setShowPatientDropdown(!showPatientDropdown);
                        }}
                      >
                        <Text style={{ fontSize: 16, color: selectedPatientId ? '#333' : '#999' }}>
                          {selectedPatientId 
                            ? displayPatients.find(patient => patient._id === selectedPatientId)?.full_name || "Bệnh nhân đã chọn"
                            : "Chọn bệnh nhân..."}
                        </Text>
                        <Ionicons 
                          name={showPatientDropdown ? "chevron-up" : "chevron-down"} 
                          size={20} 
                          color={Colors.primary} 
                        />
                      </TouchableOpacity>
                      
                      {showPatientDropdown && (
                        <TouchableWithoutFeedback
                          onPress={(e) => {
                            // This prevents dropdown from closing when clicking inside it
                            e.stopPropagation();
                          }}
                        >
                          <View style={{
                            position: 'absolute',
                            top: 45,
                            left: 0,
                            right: 0,
                            backgroundColor: 'white',
                            borderWidth: 1,
                            borderColor: '#ddd',
                            borderRadius: 8,
                            zIndex: 9999,
                            elevation: 10,
                            shadowColor: '#000',
                            shadowOffset: { width: 0, height: 4 },
                            shadowOpacity: 0.2,
                            shadowRadius: 6,
                            maxHeight: 250,
                            overflow: 'hidden'
                          }}>
                            {isLoadingPatients ? (
                              <View style={{
                                padding: 12,
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexDirection: 'row'
                              }}>
                                <ActivityIndicator size="small" color={Colors.primary} />
                                <Text style={{ marginLeft: 8, color: '#666' }}>Đang tải...</Text>
                              </View>
                            ) : patientsError ? (
                              <View style={{
                                padding: 12,
                                alignItems: 'center',
                                justifyContent: 'center'
                              }}>
                                <Text style={{ color: '#d32f2f' }}>Lỗi: {patientsError}</Text>
                              </View>
                            ) : displayPatients.length === 0 ? (
                              <View style={{
                                padding: 12,
                                alignItems: 'center',
                                justifyContent: 'center'
                              }}>
                                <Text style={{ color: '#666' }}>Không có bệnh nhân nào</Text>
                              </View>
                            ) : (
                              <FlatList
                                data={displayPatients}
                                keyExtractor={(item) => item._id}
                                renderItem={({ item }) => (
                                  <TouchableOpacity
                                    activeOpacity={0.7}
                                    style={{
                                      padding: 16,
                                      borderBottomWidth: 1,
                                      borderBottomColor: '#f0f0f0',
                                      backgroundColor: selectedPatientId === item._id ? 'rgba(33, 150, 243, 0.1)' : 'white',
                                      flexDirection: 'row',
                                      justifyContent: 'space-between',
                                      alignItems: 'center'
                                    }}
                                    onPress={() => {
                                      handleModalPatientSelect(item._id);
                                      setShowPatientDropdown(false);
                                    }}
                                  >
                                    <View style={{ flex: 1 }}>
                                      <Text style={{ fontSize: 16, color: '#333', fontWeight: '500' }}>{item.full_name}</Text>
                                      {item.email && (
                                        <Text style={{ fontSize: 12, color: '#666' }}>{item.email}</Text>
                                      )}
                                    </View>
                                    {selectedPatientId === item._id && (
                                      <Ionicons
                                        name="checkmark-circle"
                                        size={22}
                                        color={Colors.primary}
                                      />
                                    )}
                                  </TouchableOpacity>
                                )}
                                
                                // initialNumToRender={10}
                                // maxToRenderPerBatch={10}
                                // windowSize={15}
                                // showsVerticalScrollIndicator={true}
                                // contentContainerStyle={{ flexGrow: 0 }}
                                // nestedScrollEnabled={true}
                                // bounces={false}
                                // onScrollBeginDrag={() => {}}
                                // ListFooterComponent={<View style={{ height: 10 }} />}
                              />
                            )}
                          </View>
                        </TouchableWithoutFeedback>
                      )}
                      
                      {selectedPatientId && displayPatients.find(patient => patient._id === selectedPatientId) && (
                        <View style={{ marginTop: 8, paddingHorizontal: 4 }}>
                          <Text style={{ fontSize: 14, color: Colors.primary, fontStyle: 'italic' }}>
                            Bệnh nhân đã chọn: <Text style={{ fontWeight: 'bold' }}>{displayPatients.find(patient => patient._id === selectedPatientId)?.full_name}</Text>
                          </Text>
                        </View>
                      )}
                    </View>
                  </View>
                </View>
              {/* </ScrollView> */}
            </View>

            {/* Footer */}
            <View style={{
              flexDirection: 'row',
              justifyContent: 'flex-end',
              padding: 16,
              borderTopWidth: 1,
              borderTopColor: '#eee',
              backgroundColor: 'white',
            }}>
              <TouchableOpacity
                style={{
                  paddingVertical: 10,
                  paddingHorizontal: 20,
                  backgroundColor: '#f5f5f5',
                  borderRadius: 8,
                  marginRight: 12,
                }}
                onPress={onClose}
              >
                <Text style={{ color: '#666', fontWeight: 'bold' }}>Hủy</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={{
                  paddingVertical: 10,
                  paddingHorizontal: 20,
                  backgroundColor: isSubmitDisabled ? 'rgba(33, 150, 243, 0.5)' : Colors.primary,
                  borderRadius: 8,
                }}
                onPress={memoizedHandleSubmit}
                disabled={isSubmitDisabled}
              >
                <Text style={{ color: 'white', fontWeight: 'bold' }}>Tạo bài tập</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    );
  };

  // Separate stylesheet just for the modal to keep things clean
  const modal = StyleSheet.create({
    overlay: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(0,0,0,0.5)',
    },
    container: {
      width: '90%',
      maxHeight: '90%',
      backgroundColor: 'white',
      borderRadius: 16,
      overflow: 'hidden',
      elevation: 5,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 3.84,
      display: 'flex',
      flexDirection: 'column',
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: '#f0f0f0',
    },
    title: {
      fontSize: 18,
      fontWeight: 'bold',
      color: '#333',
    },
    closeButton: {
      padding: 4,
    },
    scrollContent: {
      flex: 1,
    },
    scrollContentContainer: {
      padding: 16,
      paddingBottom: 24,
    },
    formGroup: {
      marginBottom: 20,
    },
    label: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 8,
      color: '#333',
    },
    input: {
      borderWidth: 1,
      borderColor: '#ddd',
      borderRadius: 8,
      padding: 12,
      fontSize: 16,
      backgroundColor: '#fafafa',
    },
    textArea: {
      minHeight: 100,
      textAlignVertical: 'top',
    },
    dateButton: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderWidth: 1,
      borderColor: '#ddd',
      borderRadius: 8,
      padding: 12,
      backgroundColor: '#fafafa',
    },
    dateText: {
      fontSize: 16,
      color: '#333',
    },
    datePickerWrapper: {
      marginTop: 8,
      backgroundColor: 'white',
      borderRadius: 8,
      borderWidth: 1,
      borderColor: '#f0f0f0',
      overflow: 'hidden',
    },
    doneDateButton: {
      alignSelf: 'flex-end',
      padding: 8,
      marginTop: 8,
      marginRight: 8,
      marginBottom: 8,
      backgroundColor: Colors.primary,
      borderRadius: 6,
    },
    doneDateText: {
      color: 'white',
      fontWeight: 'bold',
    },
    patientList: {
      maxHeight: 200,
      borderWidth: 1,
      borderColor: '#ddd',
      borderRadius: 8,
      backgroundColor: '#fafafa',
    },
    patientItem: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 12,
      borderBottomWidth: 1,
      borderBottomColor: '#f0f0f0',
    },
    patientItemSelected: {
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
    },
    patientItemText: {
      fontSize: 16,
      color: '#333',
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    loadingText: {
      marginTop: 12,
      fontSize: 16,
      color: '#666',
    },
    errorContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    errorText: {
      fontSize: 16,
      color: ExtendedColors.danger,
      textAlign: 'center',
      marginBottom: 16,
    },
    retryButton: {
      backgroundColor: Colors.primary,
      paddingVertical: 8,
      paddingHorizontal: 16,
      borderRadius: 8,
    },
    retryButtonText: {
      color: 'white',
      fontWeight: 'bold',
    },
    emptyListText: {
      textAlign: 'center',
      padding: 20,
      color: '#666',
      fontSize: 16,
    },
    patientSelectItem: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 12,
      borderBottomWidth: 1,
      borderBottomColor: '#f0f0f0',
    },
    selectedPatientItem: {
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
    },
    patientSelectItemText: {
      fontSize: 16,
      color: '#333',
    },
  });

  // --- Header Right Button for Doctor ---
  const HeaderRightDoctor = () => (
    <TouchableOpacity
      style={styles.headerButton}
      onPress={() => setShowCreateExerciseModal(true)}
    >
      <Ionicons name="add-circle-outline" size={24} color={Colors.white} />
      <Text style={styles.headerButtonText}>Tạo BT</Text>
    </TouchableOpacity>
  );
  // --- End Header Right Button ---

  // Render doctor-specific content
  const renderDoctorContent = () => (
    <View style={styles.contentSection}>
  
      {/* Premium-looking Create Exercise Button */}
      <TouchableOpacity 
        style={styles.premiumButton}
        onPress={() => setShowCreateExerciseModal(true)}
      >
        <View style={styles.premiumButtonContent}>
          <View style={styles.premiumButtonIconContainer}>
            <Ionicons name="add-circle" size={22} color="white" />
          </View>
          <Text style={styles.premiumButtonText}>Tạo bài tập mới</Text>
        </View>
        <Ionicons name="chevron-forward" size={22} color="rgba(255,255,255,0.8)" />
      </TouchableOpacity>

      {/* Patient List Section */}
      <View style={[styles.sectionHeader, {marginTop: 16}]}>
        <Text style={styles.sectionHeading}>Danh sách bệnh nhân</Text>
        <TouchableOpacity 
          style={styles.iconButton}
          onPress={fetchPatientList}
        >
          <MaterialIcons name="refresh" size={22} color={Colors.primary} />
        </TouchableOpacity>
      </View>

      {isLoadingPatients ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.statusText}>Đang tải danh sách bệnh nhân...</Text>
        </View>
      ) : patientsError ? (
        <View style={styles.centerContainer}>
          <Text style={styles.errorMessage}>{patientsError}</Text>
          <TouchableOpacity style={styles.actionButton} onPress={fetchPatientList}>
            <Text style={styles.actionButtonText}>Thử lại</Text>
          </TouchableOpacity>
        </View>
      ) : (
      <FlatList
          data={patients}
        renderItem={({ item }) => (
          <TouchableOpacity 
              style={styles.patientCard}
              onPress={() => router.push({
                pathname: "/(tabs)/patient-detail",
                params: { 
                  id: item._id,
                  patientData: JSON.stringify({
                    full_name: item.full_name,
                    email: item.email || "",
                    phone: item.phone || "",
                    age: item.age || "",
                    gender: item.gender || ""
                  })
                }
              })}
            >
              <View style={styles.patientAvatarContainer}>
                <View style={styles.patientAvatar}>
                  <Text style={styles.patientInitial}>
                    {item.full_name.charAt(0).toUpperCase()}
                  </Text>
                </View>
              </View>
              <View style={styles.patientDetails}>
                <Text style={styles.patientFullName}>{item.full_name}</Text>
                <View style={styles.patientMetaInfo}>
                  {item.email && (
                    <View style={styles.patientMetaItem}>
                      <Ionicons name="mail-outline" size={14} color={ExtendedColors.darkGray} style={styles.metaIcon} />
                      <Text style={styles.patientMetaText}>{item.email}</Text>
                    </View>
                  )}
                  {item.phone && (
                    <View style={styles.patientMetaItem}>
                      <Ionicons name="call-outline" size={14} color={ExtendedColors.darkGray} style={styles.metaIcon} />
                      <Text style={styles.patientMetaText}>{item.phone}</Text>
                    </View>
                  )}
                  {item.age && (
                    <View style={styles.patientMetaItem}>
                      <Ionicons name="calendar-outline" size={14} color={ExtendedColors.darkGray} style={styles.metaIcon} />
                      <Text style={styles.patientMetaText}>{item.age} tuổi</Text>
                    </View>
                  )}
                </View>
              </View>
              <View style={styles.patientCardAction}>
                <Ionicons name="chevron-forward" size={20} color={ExtendedColors.darkGray} />
            </View>
          </TouchableOpacity>
        )}
          keyExtractor={item => item._id}
          contentContainerStyle={styles.patientListContent}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyStateContainer}>
              <Ionicons name="people-outline" size={60} color="#ccc" />
              <Text style={styles.emptyStateTitle}>Chưa có bệnh nhân</Text>
              <Text style={styles.emptyStateMessage}>Bạn chưa có bệnh nhân nào trong hệ thống</Text>
            </View>
          }
        />
      )}

      {/* Floating Action Button for quick create */}
      <TouchableOpacity 
        style={styles.floatingButton}
        onPress={() => setShowCreateExerciseModal(true)}
      >
        <Ionicons name="add" size={30} color="white" />
      </TouchableOpacity>
    </View>
  );

  // Define the fetchWithTimeout function inside the component
  // This avoids importing it from apiTest.ts where it's not exported
  const fetchWithTimeout = (url: string, options: RequestInit = {}, timeout = 10000) => {
    return new Promise<Response>((resolve, reject) => {
      // Create a controller to cancel fetch request if needed
      const controller = new AbortController();
      
      // Set up timeout handler
      const timeoutId = setTimeout(() => {
        controller.abort();
        reject(new Error(`Request timeout after ${timeout}ms`));
      }, timeout);
      
      // Perform fetch with signal from controller
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

  const RenderContent = ({role}: {role: string}) => {

    if (role.toLowerCase() === 'doctor') {
      return renderDoctorContent();
    } else if (role.toLowerCase() === 'patient') {
      return renderPatientContent();
    } else {
      return (
        <View style={styles.container}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10 }}>Vai trò người dùng không hợp lệ</Text>
          <Text>Vai trò hiện tại 1: {role || 'không xác định'}</Text>
          <Text>Trạng thái đăng nhập: {isLoggedIn ? 'Đã đăng nhập' : 'Chưa đăng nhập'}</Text>
          <TouchableOpacity 
            style={[styles.logoutButton, { marginTop: 20 }]} 
            onPress={handleLogout}
          >
            <Text style={styles.logoutText}>Đăng xuất</Text>
          </TouchableOpacity>
        </View>
      );
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <Stack.Screen
        options={{
          headerTitle: "Trang chủ", 
          headerStyle: { backgroundColor: Colors.primary },
          headerTintColor: Colors.white,
          headerTitleStyle: { fontWeight: 'bold' },
          headerRight: undefined, // Xóa nút tạo bài tập
        }}
      />

      {isLoggedIn ? (
        <>
          {renderProfileSection()}
          {!userRole ? (
            <View style={styles.container}>
              <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10 }}>Đang tải thông tin người dùng...</Text>
            </View>
          ) : (
            <RenderContent role={userRole}/>
          )}

          {(userRole === 'doctor') && (
            <CreateExerciseModalComponent
              visible={showCreateExerciseModal}
              onClose={() => {
                setShowCreateExerciseModal(false);
                resetCreateExerciseForm();
              }}
              onSubmit={handleCreateExerciseSubmit}
              initialData={{
                exerciseName,
                exerciseDescription,
                assignedDate,
                dueDate,
                selectedPatientId: selectedPatientForExercise
              }}
              patients={patients}
              isLoadingPatients={isLoadingPatients}
              patientsError={patientsError}
            />
          )}
        </>
      ) : (
        <View style={{flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20}}>
          <Text style={{fontSize: 18, marginBottom: 20, textAlign: 'center'}}>
            Vui lòng đăng nhập để tiếp tục
          </Text>
          <TouchableOpacity
            style={{
              backgroundColor: Colors.primary,
              paddingHorizontal: 20,
              paddingVertical: 10,
              borderRadius: 8
            }}
            onPress={() => router.replace('/(auth)/login')}
          >
            <Text style={{color: 'white', fontWeight: 'bold'}}>Đăng nhập</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  profileSection: {
    flexDirection: 'row',
    padding: 16,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 12,
  },
  profileInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  userRole: {
    fontSize: 14,
    marginBottom: 2,
  },
  userEmail: {
    fontSize: 12,
    fontStyle: 'italic',
  },
  logoutButton: {
    backgroundColor: ExtendedColors.danger,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 5,
  },
  logoutText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  contentContainer: {
    flex: 1,
    padding: 16,
  },
  tabContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  tab: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 6,
    marginHorizontal: 4,
    backgroundColor: 'rgba(0,0,0,0.05)',
  },
  activeTab: {
    backgroundColor: Colors.primary,
  },
  tabText: {
    fontWeight: '500',
  },
  activeTabText: {
    color: Colors.white,
  },
  filterSortButton: {
    backgroundColor: Colors.accent,
    padding: 10,
    borderRadius: 6,
    alignItems: 'center',
    marginBottom: 10,
    marginLeft:50,
    marginRight:50
  },
  filterSortButtonText: {
    color: Colors.white,
    fontWeight: 'bold',
  },
  filterSortMenu: {
    backgroundColor: 'rgba(0,0,0,0.05)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  filterSection: {
    marginBottom: 12,
  },
  filterTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  filterOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  filterOption: {
    backgroundColor: 'rgba(0,0,0,0.05)',
    padding: 8,
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  filterOptionText: {
    fontSize: 14,
  },
  sortSection: {
    marginTop: 8,
  },
  sortTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  sortOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  sortOption: {
    backgroundColor: 'rgba(0,0,0,0.05)',
    padding: 8,
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  sortOptionText: {
    fontSize: 14,
  },
  sectionHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    paddingHorizontal: 16, 
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.05)',
  },
  sectionHeading: { 
    fontSize: 20, 
    fontWeight: 'bold',
    color: '#333',
  },
  iconButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.03)',
  },
  contentSection: { 
    flex: 1,
    paddingBottom: 16 
  },
  premiumButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.primary,
    padding: 16,
    borderRadius: 12,
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 8,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  premiumButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  premiumButtonIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  premiumButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  floatingButton: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  patientCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  patientAvatarContainer: {
    marginRight: 14,
  },
  patientAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: Colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
  },
  patientInitial: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  patientDetails: {
    flex: 1,
  },
  patientFullName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    color: '#333',
  },
  patientMetaInfo: {
    flexDirection: 'column',
  },
  patientMetaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  metaIcon: {
    marginRight: 4,
  },
  patientMetaText: {
    fontSize: 13,
    color: ExtendedColors.darkGray,
  },
  patientCardAction: {
    padding: 4,
  },
  patientListContent: {
    padding: 16,
    paddingBottom: 80, // Space for FAB
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  statusText: {
    marginTop: 16,
    color: Colors.primary,
    fontSize: 16,
  },
  errorMessage: {
    color: ExtendedColors.danger,
    fontSize: 16,
    marginBottom: 16,
    textAlign: 'center',
  },
  actionButton: {
    backgroundColor: Colors.primary,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  actionButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  emptyStateContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 8,
    color: '#333',
  },
  emptyStateMessage: {
    fontSize: 14,
    color: ExtendedColors.darkGray,
    textAlign: 'center',
  },
  headerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 15,
    paddingVertical: 5,
    paddingHorizontal: 8,
  },
  headerButtonText: {
    color: Colors.white,
    marginLeft: 5,
    fontWeight: '600',
    fontSize: 14,
  },
  exerciseItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  exerciseInfo: {
    flex: 1,
    marginRight: 10,
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
    color: '#333',
  },
  exerciseDetailText: {
    fontSize: 13,
    color: ExtendedColors.darkGray,
    marginTop: 3,
  },
  apiTestContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
    padding: 16,
  },
  testApiButton: {
    backgroundColor: Colors.primary,
    padding: 8,
    borderRadius: 8,
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 4,
    marginBottom: 8,
  },
  testApiButtonText: {
    color: Colors.white,
    fontWeight: 'bold',
    fontSize: 11,
  },
  patientSelectItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  selectedPatientItem: {
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
  },
  patientSelectItemText: {
    fontSize: 16,
    color: '#333',
  },
  userTitle: {
    fontSize: 12,
    marginBottom: 2,
  },
  specialization: {
    fontSize: 12,
    marginBottom: 2,
    color: ExtendedColors.secondary,
  },
});

export default HomeScreen;

