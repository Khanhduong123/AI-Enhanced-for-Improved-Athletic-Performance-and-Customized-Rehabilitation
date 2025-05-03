import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, TextInput, Modal, Alert, Platform } from 'react-native';
import { Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../../constants/Colors';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useAuthStore } from '../../store/authStore';

// API Configuration
const API_BASE_URL = Platform.select({
  ios: 'http://localhost:7860',
  android: 'http://192.168.68.104:7860', // Special IP for Android emulator to reach host machine
  default: 'http://localhost:7860',
});

interface Patient {
  _id: string;
  full_name: string;
  email: string;
  phone?: string;
  age?: number;
  gender?: string;
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

export default function DoctorDashboard() {
  const { userData } = useAuthStore();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [exerciseName, setExerciseName] = useState('');
  const [exerciseDescription, setExerciseDescription] = useState('');
  const [assignedDate, setAssignedDate] = useState(new Date());
  const [dueDate, setDueDate] = useState(new Date());
  const [showModal, setShowModal] = useState(false);
  const [showAssignedDatePicker, setShowAssignedDatePicker] = useState(false);
  const [showDueDatePicker, setShowDueDatePicker] = useState(false);
  
  // Get doctor ID from authentication store instead of hardcoding
  const getDoctorId = () => {
    if (!userData) return '';
    
    // Try to get MongoDB _id first, then fall back to regular id
    const userDataAny = userData as any;
    return userDataAny._id || userData.id || '';
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/patients`);
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      } else {
        // If the API call fails, use hardcoded data as fallback
        const hardcodedData = [
          {"email":"duongbaokhanh@gmail.com","full_name":"Dương Bảo Khánh","role":"patient","_id":"67fd4e833d275d212bd47e51"},
          {"email":"duongbaokhanh2@example.com","full_name":"Duong Bao Khanh","role":"patient ","_id":"67fd4f383178c792a8ea939b"}
        ];
        setPatients(hardcodedData);
      }
    } catch (error) {
      console.error('Error fetching patients:', error);
      // Fallback to hardcoded data if network error occurs
      const hardcodedData = [
        {"email":"duongbaokhanh@gmail.com","full_name":"Dương Bảo Khánh","role":"patient","_id":"67fd4e833d275d212bd47e51"},
        {"email":"duongbaokhanh2@example.com","full_name":"Duong Bao Khanh","role":"patient ","_id":"67fd4f383178c792a8ea939b"}
      ];
      setPatients(hardcodedData);
    }
  };

  const handleCreateExercise = async () => {
    if (!exerciseName || !exerciseDescription || !selectedPatient) {
      Alert.alert('Lỗi', 'Vui lòng điền đầy đủ thông tin và chọn bệnh nhân');
      return;
    }
    
    // Get the doctor ID dynamically
    const doctorId = getDoctorId();
    if (!doctorId) {
      Alert.alert('Lỗi', 'Không thể xác định thông tin bác sĩ');
      return;
    }

    console.log('Creating exercise with doctor ID:', doctorId);
    console.log('Selected patient ID:', selectedPatient);

    const newExercise: Exercise = {
      name: exerciseName,
      description: exerciseDescription,
      assigned_by: doctorId,
      assigned_to: selectedPatient,
      assigned_date: assignedDate.toISOString(),
      due_date: dueDate.toISOString(),
      status: 'Pending'
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/exercises/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newExercise),
      });

      if (response.ok) {
        Alert.alert('Thành công', 'Đã tạo bài tập mới');
        setShowModal(false);
        resetForm();
      } else {
        // Get detailed error message
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
        
        throw new Error(`${response.status} ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error creating exercise:', error);
      Alert.alert('Lỗi', `Không thể tạo bài tập. ${error instanceof Error ? error.message : 'Vui lòng thử lại sau.'}`);
    }
  };

  const resetForm = () => {
    setExerciseName('');
    setExerciseDescription('');
    setSelectedPatient('');
    setAssignedDate(new Date());
    setDueDate(new Date());
  };

  const renderPatientItem = ({ item }: { item: Patient }) => (
    <TouchableOpacity
      style={[
        styles.patientItem,
        selectedPatient === item._id && styles.selectedPatient,
      ]}
      onPress={() => setSelectedPatient(item._id)}
    >
      <View style={styles.patientInfo}>
        <Text style={styles.patientName}>{item.full_name}</Text>
        {item.phone && <Text style={styles.patientDetails}>SĐT: {item.phone}</Text>}
        {item.age && <Text style={styles.patientDetails}>Tuổi: {item.age}</Text>}
        {item.gender && <Text style={styles.patientDetails}>Giới tính: {item.gender}</Text>}
        {(item as any).diagnosis && <Text style={styles.patientDiagnosis}>Chẩn đoán: {(item as any).diagnosis}</Text>}
      </View>
      <Ionicons
        name={selectedPatient === item._id ? 'checkmark-circle' : 'ellipse-outline'}
        size={24}
        color="#007AFF"
      />
    </TouchableOpacity>
  );

  const onDateChange = (event: any, selectedDate?: Date, dateType: 'assigned' | 'due' = 'assigned') => {
    if (Platform.OS === 'android') {
      if (dateType === 'assigned') {
        setShowAssignedDatePicker(false);
      } else {
        setShowDueDatePicker(false);
      }
    }
    
    if (selectedDate) {
      if (dateType === 'assigned') {
        setAssignedDate(selectedDate);
      } else {
        setDueDate(selectedDate);
      }
    }
  };

  const renderDatePicker = () => {
    if (Platform.OS === 'ios') {
      return (
        <View style={styles.datePickerContainer}>
          <DateTimePicker
            value={showAssignedDatePicker ? assignedDate : dueDate}
            mode="date"
            display="spinner"
            onChange={(event, date) => onDateChange(event, date, showAssignedDatePicker ? 'assigned' : 'due')}
          />
        </View>
      );
    }

    return (showAssignedDatePicker || showDueDatePicker) ? (
      <DateTimePicker
        value={showAssignedDatePicker ? assignedDate : dueDate}
        mode="date"
        display="default"
        onChange={(event, date) => onDateChange(event, date, showAssignedDatePicker ? 'assigned' : 'due')}
      />
    ) : null;
  };

  const HeaderRight = () => (
    <TouchableOpacity
      style={styles.headerButton}
      onPress={() => setShowModal(true)}
    >
      <Ionicons name="add-circle-outline" size={24} color="white" />
      <Text style={styles.headerButtonText}>Tạo bài tập</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Stack.Screen
        options={{
          headerTitle: "Danh sách bệnh nhân",
          headerRight: HeaderRight,
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      />

      <FlatList
        data={patients}
        renderItem={renderPatientItem}
        keyExtractor={item => item._id}
        style={styles.list}
        ListHeaderComponent={() => (
          <Text style={styles.listTitle}>Danh sách bệnh nhân</Text>
        )}
      />

      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Tạo bài tập mới</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Tên bài tập"
              value={exerciseName}
              onChangeText={setExerciseName}
            />

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Mô tả bài tập"
              value={exerciseDescription}
              onChangeText={setExerciseDescription}
              multiline
              numberOfLines={4}
            />

            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowAssignedDatePicker(true)}
            >
              <Text>Ngày giao: {assignedDate.toLocaleDateString()}</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowDueDatePicker(true)}
            >
              <Text>Hạn hoàn thành: {dueDate.toLocaleDateString()}</Text>
            </TouchableOpacity>

            {showAssignedDatePicker && (
              <DateTimePicker
                value={assignedDate}
                mode="date"
                display="default"
                onChange={(event, selectedDate) => {
                  setShowAssignedDatePicker(false);
                  if (selectedDate) {
                    setAssignedDate(selectedDate);
                  }
                }}
              />
            )}

            {showDueDatePicker && (
              <DateTimePicker
                value={dueDate}
                mode="date"
                display="default"
                onChange={(event, selectedDate) => {
                  setShowDueDatePicker(false);
                  if (selectedDate) {
                    setDueDate(selectedDate);
                  }
                }}
              />
            )}

            <Text style={styles.sectionTitle}>Chọn bệnh nhân:</Text>
            <FlatList
              data={patients}
              renderItem={renderPatientItem}
              keyExtractor={item => item._id}
              style={styles.patientList}
              showsVerticalScrollIndicator={true}
              initialNumToRender={20}
              maxToRenderPerBatch={20}
              windowSize={21}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => {
                  setShowModal(false);
                  resetForm();
                }}
              >
                <Text style={styles.buttonText}>Hủy</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.createButton]}
                onPress={handleCreateExercise}
              >
                <Text style={styles.buttonText}>Tạo bài tập</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  headerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 8,
    padding: 8,
  },
  headerButtonText: {
    color: 'white',
    marginLeft: 4,
    fontWeight: '600',
  },
  list: {
    flex: 1,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  patientItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    marginVertical: 4,
    marginHorizontal: 8,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  selectedPatient: {
    backgroundColor: '#E3F2FD',
  },
  patientInfo: {
    flex: 1,
  },
  patientName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  patientDetails: {
    fontSize: 14,
    color: '#666',
  },
  patientDiagnosis: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '90%',
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  dateButton: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  patientList: {
    maxHeight: 200,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 16,
  },
  modalButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    marginLeft: 8,
  },
  cancelButton: {
    backgroundColor: '#e0e0e0',
  },
  createButton: {
    backgroundColor: '#007AFF',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
  datePickerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
  },
}); 