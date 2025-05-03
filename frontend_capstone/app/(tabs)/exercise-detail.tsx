import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView, Alert, ActivityIndicator, Button } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { CameraType, CameraView, useCameraPermissions } from 'expo-camera';
import { ResizeMode, Video } from 'expo-av';
import { Colors } from '../../constants/Colors';
import { useColorScheme } from 'react-native';
import { FontAwesome, MaterialIcons } from '@expo/vector-icons';
import { Exercise } from '../../types/exercise';
import { updateExerciseStatus } from '../../services/exerciseService';

// Add warning color if missing in Colors
const ExtendedColors = {
  ...Colors,
  warning: '#FFC107',
  darkGray: '#666666',
  secondary: '#4CAF50'
};

// Giả lập dữ liệu AIResults cho bài tập hoàn thành
const MOCK_AI_RESULTS = {
  score: 92,
  suggestions: [
    'Góc cánh tay nâng lên có thể cao hơn một chút',
    'Giữ tư thế ổn định hơn khi đang giữ',
    'Hoàn thành động tác tốt, tiếp tục luyện tập để cải thiện',
  ],
  overallEvaluation: 'Rất tốt, tiếp tục duy trì',
};

export default function ExerciseDetail() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const colorScheme = useColorScheme() ?? 'light';
  const exerciseId = params.id as string;
  
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Trạng thái camera và video
  const [cameraVisible, setCameraVisible] = useState(false);
  const [video, setVideo] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [aiResults, setAiResults] = useState<any | null>(null);

  const cameraRef = useRef<any>(null);
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  
  const videoRef = useRef(null);
  const [status, setStatus] = useState({});
  // Lấy thông tin bài tập
  useEffect(() => {
    if (!exerciseId) {
      setError('Không tìm thấy thông tin bài tập');
      setLoading(false);
      return;
    }
    
    // Trong thực tế, bạn sẽ gọi API để lấy chi tiết bài tập
    // Ở đây chúng ta giả lập bằng cách trả về dữ liệu từ params
    const fetchExerciseDetail = async () => {
      try {
        // Cố gắng phân tích dữ liệu bài tập từ tham số route nếu có
        if (params.exerciseData) {
          const exerciseData = JSON.parse(params.exerciseData as string);
          setExercise(exerciseData);
        } else {
          // Trong thực tế bạn sẽ gọi API để lấy chi tiết bài tập theo ID
          // Ví dụ: const data = await getExerciseDetail(exerciseId);
          // Ở đây chỉ giả lập với dữ liệu cơ bản
          setExercise({
            _id: exerciseId,
            name: params.name as string || 'Bài tập',
            description: 'Chi tiết bài tập',
            assigned_by: '',
            assigned_to: '',
            assigned_date: new Date().toISOString(),
            due_date: new Date().toISOString(),
            status: (params.status as string || 'Pending') as Exercise['status'],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        }
      } catch (err) {
        console.error('Lỗi khi lấy thông tin bài tập:', err);
        setError('Không thể tải thông tin bài tập');
      } finally {
        setLoading(false);
      }
    };
    
    fetchExerciseDetail();
  }, [exerciseId]);
  
  // Function to start recording
  const startRecording = async () => {
    if (cameraRef.current) {
      try {
        setIsRecording(true);
        console.log("Bắt đầu ghi video");
        const { uri } = await cameraRef.current.recordAsync();
        console.log('URI video:', uri);
        setVideo(uri);
        setCameraVisible(false);
      } catch (error) {
        console.error('Lỗi khi ghi video:', error);
        Alert.alert('Lỗi', 'Không thể quay video. Vui lòng thử lại.');
      } finally {
        setIsRecording(false);
      }
    }
  };

  // Function to stop recording
  const stopRecording = async () => {
    if (cameraRef.current && isRecording) {
      await cameraRef.current.stopRecording();
      setIsRecording(false);
    }
  };

  // Function to upload video and update exercise status
  const uploadVideo = async () => {
    if (!video || !exercise) return;
    
    setUploading(true);
    try {
      // Trong thực tế, bạn sẽ upload video lên server
      // Ở đây chúng ta giả lập quá trình upload và đánh giá AI
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Cập nhật trạng thái bài tập thành "Completed"
      try {
        await updateExerciseStatus(exercise._id, 'Completed');
        console.log('Exercise status updated successfully');
      } catch (error) {
        console.error('Error updating exercise status:', error);
        Alert.alert(
          'Thông báo',
          'Không thể cập nhật trạng thái bài tập do vấn đề kết nối. Vui lòng kiểm tra kết nối của bạn với API server.',
          [{ text: 'OK' }]
        );
      }
      
      // Giả lập kết quả đánh giá AI
      setAiResults(MOCK_AI_RESULTS);
      
      // Thông báo thành công
      Alert.alert(
        'Thành công',
        'Video đã được gửi đi và đánh giá. Bài tập đã được đánh dấu là hoàn thành.',
        [{ text: 'Xem kết quả', onPress: () => {} }]
      );
    } catch (error) {
      Alert.alert('Lỗi', 'Không thể gửi video. Vui lòng thử lại.');
    } finally {
      setUploading(false);
    }
  };

  // Hàm đổi camera
  function toggleCameraFacing() {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  }

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

  // Chuyển về trang trước đó (patient-detail)
  const goBack = () => {
    router.back();
  };
  
  // Chuyển về trang chủ
  const goHome = () => {
    router.replace('/(tabs)');
  };

  if (!permission) {
    // Camera permissions are still loading.
    return <View />;
  }

  if (!permission.granted) {
    // Camera or audio permissions are not granted yet.
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>Chúng tôi cần quyền truy cập camera và ghi âm để tiếp tục</Text>
        <TouchableOpacity 
          style={styles.permissionButton} 
          onPress={async () => {
            await requestPermission();
          }}
        >
          <Text style={styles.permissionButtonText}>Cấp quyền</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Xử lý loading và error states
  if (loading) {
    return (
      <>
        <Stack.Screen
          options={{
            title: 'Chi tiết bài tập',
            headerStyle: {
              backgroundColor: Colors.primary,
            },
            headerTintColor: Colors.white,
            headerTitleStyle: {
              fontWeight: 'bold',
            },
           
          }}
        />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingText}>Đang tải thông tin bài tập...</Text>
        </View>
      </>
    );
  }

  if (error || !exercise) {
    return (
      <>
        <Stack.Screen
          options={{
            title: 'Chi tiết bài tập',
            headerStyle: {
              backgroundColor: Colors.primary,
            },
            headerTintColor: Colors.white,
            headerTitleStyle: {
              fontWeight: 'bold',
            },
           
          }}
        />
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error || 'Không tìm thấy bài tập'}</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={goBack}
          >
            <Text style={styles.backButtonText}>Quay lại</Text>
          </TouchableOpacity>
        </View>
      </>
    );
  }

  const renderContent = () => {
    // Nếu đang hiển thị camera
    if (cameraVisible) {
      return (
        <View style={styles.cameraContainer}>
          <CameraView
            ref={cameraRef}
            style={styles.camera}
            facing={facing}
            enableTorch={false}
          >
            <View style={styles.cameraControls}>
              {isRecording ? (
                <TouchableOpacity 
                  style={[styles.recordButton, styles.recordingButton]} 
                  onPress={stopRecording}
                >
                  <View style={styles.recordingIndicator} />
                </TouchableOpacity>
              ) : (
                <TouchableOpacity 
                  style={styles.recordButton} 
                  onPress={startRecording}
                >
                  <View style={styles.recordButtonInner} />
                </TouchableOpacity>
              )}
              
              <TouchableOpacity 
                style={styles.cameraFlipButton} 
                onPress={toggleCameraFacing}
              >
                <MaterialIcons name="flip-camera-android" size={30} color="white" />
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={styles.closeCameraButton} 
                onPress={() => setCameraVisible(false)}
              >
                <MaterialIcons name="close" size={30} color="white" />
              </TouchableOpacity>
            </View>
          </CameraView>
        </View>
      );
    }

    // Nếu đã ghi video và có kết quả AI
    if (exercise.video || (video && aiResults)) {
      return (
        <>
          <Stack.Screen
            options={{
              title: 'Kết quả bài tập',
              headerStyle: {
                backgroundColor: Colors.primary,
              },
              headerTintColor: Colors.white,
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            
            }}
          />
          <ScrollView style={styles.container}>
            <View style={styles.videoContainer}>
              <Video
                ref={videoRef}
                source={{ uri: `http://192.168.2.11:7860/${exercise.video.file_path}` }}
                style={styles.video}
                useNativeControls
                resizeMode={ResizeMode.CONTAIN}
                onPlaybackStatusUpdate={status => setStatus(() => status)}
              />
            </View>
            <View style={styles.buttonsContainer}>
              {!status.isPlaying ? (
                <TouchableOpacity
                  style={[styles.controlButton, { backgroundColor: Colors.primary }]}
                  onPress={() => videoRef.current.playAsync()}
                >
                  <Text style={styles.controlButtonText}>Play</Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity
                  style={[styles.controlButton, { backgroundColor: '#f44336' }]}
                  onPress={() => videoRef.current.pauseAsync()}
                >
                  <Text style={styles.controlButtonText}>Pause</Text>
                </TouchableOpacity>
              )}
               <TouchableOpacity
           style={[styles.controlButton, { backgroundColor: Colors.primary }]}
                onPress={goBack}
              >
                <Text style={styles.controlButtonText}>Quay lại</Text>
              </TouchableOpacity>
            </View>
            {/* <View style={styles.resultContainer}>
              <Text style={styles.resultTitle}>Kết quả đánh giá</Text>
              
              <View style={styles.scoreContainer}>
                <Text style={styles.scoreLabel}>Điểm số:</Text>
                <Text style={styles.scoreValue}>{aiResults.score}/100</Text>
              </View>
              
              <Text style={styles.suggestionsTitle}>Gợi ý cải thiện:</Text>
              {aiResults.suggestions.map((suggestion: string, index: number) => (
                <View key={index} style={styles.suggestionItem}>
                  <MaterialIcons name="check-circle" size={20} color={Colors.primary} />
                  <Text style={styles.suggestionText}>{suggestion}</Text>
                </View>
              ))}
              
              <View style={styles.evaluationContainer}>
                <Text style={styles.evaluationLabel}>Đánh giá tổng thể:</Text>
                <Text style={styles.evaluationText}>{aiResults.overallEvaluation}</Text>
              </View>
            </View> */}
            
          
          </ScrollView>
        </>
      );
    }

    // Nếu đã ghi video nhưng chưa upload
    if (video) {
      return (
        <View style={styles.container}>
          <View style={styles.videoContainer}>
            <Video
              source={{ uri: video }}
              style={styles.video}
              useNativeControls
              resizeMode={ResizeMode.CONTAIN}
            />
          </View>
          
          <View style={styles.videoControlsContainer}>
            <TouchableOpacity
              style={styles.retakeButton}
              onPress={() => {
                setVideo(null);
                setCameraVisible(true);
              }}
            >
              <Text style={styles.retakeButtonText}>Quay lại</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.uploadButton}
              onPress={uploadVideo}
              disabled={uploading}
            >
              {uploading ? (
                <ActivityIndicator size="small" color="white" />
              ) : (
                <Text style={styles.uploadButtonText}>Gửi video</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      );
    }

    // Mặc định: hiển thị thông tin bài tập
    return (
      <>
        <Stack.Screen
          options={{
            title: 'Chi tiết bài tập',
            headerStyle: {
              backgroundColor: Colors.primary,
            },
            headerTintColor: Colors.white,
            headerTitleStyle: {
              fontWeight: 'bold',
            },
           
          }}
        />
        <ScrollView style={styles.container}>
          <View style={styles.exerciseHeader}>
            <Text style={styles.exerciseName}>{exercise.name}</Text>
            <View 
              style={[
                styles.statusBadge, 
                { 
                  backgroundColor: 
                    exercise.status === 'Completed' ? ExtendedColors.secondary : 
                    exercise.status === 'In Progress' ? ExtendedColors.warning : 
                    Colors.primary 
                }
              ]}
            >
              <Text style={styles.statusText}>
                {exercise.status === 'Completed' ? 'Đã hoàn thành' : 
                 exercise.status === 'In Progress' ? 'Đang thực hiện' : 
                 'Chưa hoàn thành'}
              </Text>
            </View>
          </View>

          <View style={styles.dateInfo}>
            <Text style={styles.dateLabel}>Ngày giao:</Text>
            <Text style={styles.dateValue}>{formatDate(exercise.assigned_date)}</Text>
          </View>

          <View style={styles.dateInfo}>
            <Text style={styles.dateLabel}>Hạn hoàn thành:</Text>
            <Text style={styles.dateValue}>{formatDate(exercise.due_date)}</Text>
          </View>
          
          {exercise.description && (
            <View style={styles.descriptionContainer}>
              <Text style={styles.descriptionTitle}>Mô tả:</Text>
              <Text style={styles.descriptionText}>{exercise.description}</Text>
            </View>
          )}
          
          {/* Hướng dẫn video giả lập */}
          <View style={styles.videoGuideContainer}>
            <Text style={styles.videoGuideTitle}>Video chi tiết của bệnh nhân</Text>
            <Image
              source={{ uri: 'https://via.placeholder.com/350x200?text=Video+Hu%E1%BB%9Bng+D%E1%BA%ABn' }}
              style={styles.videoGuidePlaceholder}
            />
          </View>
          
          {/* Bước thực hiện giả lập */}
          {/* <View style={styles.stepsContainer}>
            <Text style={styles.stepsTitle}>Các bước thực hiện:</Text>
            <View style={styles.stepsList}>
              {['Bước 1: Chuẩn bị tư thế', 
                'Bước 2: Thực hiện động tác', 
                'Bước 3: Giữ tư thế trong 5 giây', 
                'Bước 4: Thả lỏng và lặp lại'].map((step, index) => (
                <View key={index} style={styles.stepItem}>
                  <MaterialIcons name="check-circle" size={20} color={Colors.primary} />
                  <Text style={styles.stepText}>{step}</Text>
                </View>
              ))}
            </View>
          </View> */}
          
          {/* {exercise.status !== 'Completed' && (
            <TouchableOpacity
              style={styles.startExerciseButton}
              onPress={() => setCameraVisible(true)}
            >
              <Text style={styles.startExerciseButtonText}>Bắt đầu tập và ghi lại</Text>
            </TouchableOpacity>
          )} */}
        </ScrollView>

        {/* Thêm nút nhỏ quay lại ở góc trái màn hình */}
      
      </>
    );
  };

  return renderContent();
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: 'red',
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
  },
  backButton: {
    backgroundColor: Colors.primary,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  exerciseName: {
    fontSize: 22,
    fontWeight: 'bold',
    flex: 1,
  },
  statusBadge: {
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 15,
  },
  statusText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  dateInfo: {
    flexDirection: 'row',
    padding: 16,
    paddingVertical: 8,
  },
  dateLabel: {
    width: 120,
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
  },
  dateValue: {
    fontSize: 14,
  },
  descriptionContainer: {
    padding: 16,
  },
  descriptionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  descriptionText: {
    fontSize: 14,
    lineHeight: 22,
  },
  videoGuideContainer: {
    padding: 16,
  },
  videoGuideTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  videoGuidePlaceholder: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginBottom: 8,
  },
  videoGuideInstruction: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
  },
  stepsContainer: {
    padding: 16,
  },
  stepsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  stepsList: {
    marginVertical: 8,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  stepText: {
    marginLeft: 10,
    fontSize: 14,
    flex: 1,
  },
  startExerciseButton: {
    margin: 16,
    backgroundColor: Colors.primary,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  startExerciseButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  permissionButton: {
    backgroundColor: Colors.primary,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  cameraControls: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordButtonInner: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: 'red',
  },
  recordingButton: {
    borderWidth: 3,
    borderColor: '#fff',
  },
  recordingIndicator: {
    width: 24,
    height: 24,
    borderRadius: 4,
    backgroundColor: 'red',
  },
  cameraFlipButton: {
    position: 'absolute',
    right: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeCameraButton: {
    position: 'absolute',
    left: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  videoContainer: {
    aspectRatio: 9/16,
    backgroundColor: '#000',
  },
  video: {
    flex: 1,
  },
  videoControlsContainer: {
    flexDirection: 'row',
    padding: 16,
    justifyContent: 'space-between',
  },
  retakeButton: {
    flex: 1,
    backgroundColor: '#ccc',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginRight: 8,
  },
  retakeButtonText: {
    fontWeight: 'bold',
  },
  uploadButton: {
    flex: 2,
    backgroundColor: Colors.primary,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  uploadButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  resultContainer: {
    padding: 16,
  },
  resultTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  scoreLabel: {
    fontSize: 18,
    marginRight: 8,
  },
  scoreValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  suggestionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  suggestionText: {
    marginLeft: 10,
    fontSize: 14,
    flex: 1,
  },
  evaluationContainer: {
    marginTop: 20,
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  evaluationLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  evaluationText: {
    fontSize: 14,
    lineHeight: 22,
  },
  doneButton: {
    marginTop: 24,
    backgroundColor: Colors.primary,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  doneButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  buttonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
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
  controlButton: {
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 8,
  },
  controlButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
}); 