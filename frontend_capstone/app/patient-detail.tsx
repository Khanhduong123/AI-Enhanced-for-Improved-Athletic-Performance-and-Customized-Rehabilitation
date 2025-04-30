import React, { useState } from 'react';
import { View, Text, StyleSheet, useColorScheme, ScrollView, TouchableOpacity, FlatList } from 'react-native';
import { useLocalSearchParams, Stack, router } from 'expo-router';
import { FontAwesome, MaterialIcons } from '@expo/vector-icons';
import { Colors } from '../constants/Colors';

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
};

// Mock patient data
const MOCK_PATIENTS = {
  '1': {
    id: '1',
    name: 'Nguyễn Văn A',
    age: 45,
    gender: 'Nam',
    phone: '0901234567',
    email: 'nguyenvana@example.com',
    address: '123 Đường Lê Lợi, Q.1, TP.HCM',
    diagnosis: 'Phục hồi sau phẫu thuật gối',
    notes: 'Bệnh nhân có tiền sử cao huyết áp, cần lưu ý khi tập vận động mạnh.',
    startDate: '10/03/2023',
    nextAppointment: '15/04/2023',
  },
  '2': {
    id: '2',
    name: 'Trần Thị B',
    age: 32,
    gender: 'Nữ',
    phone: '0912345678',
    email: 'tranthib@example.com',
    address: '456 Đường Nguyễn Huệ, Q.1, TP.HCM',
    diagnosis: 'Đau lưng mãn tính',
    notes: 'Cần tập các bài tập nhẹ nhàng, tăng dần cường độ sau 2 tuần đầu.',
    startDate: '05/03/2023',
    nextAppointment: '16/04/2023',
  },
  '3': {
    id: '3',
    name: 'Lê Văn C',
    age: 50,
    gender: 'Nam',
    phone: '0987654321',
    email: 'levanc@example.com',
    address: '789 Đường Võ Văn Tần, Q.3, TP.HCM',
    diagnosis: 'Phục hồi đột quỵ',
    notes: 'Tập trung vào các bài tập phục hồi vận động nửa người bên phải.',
    startDate: '01/02/2023',
    nextAppointment: '18/04/2023',
  },
  '4': {
    id: '4',
    name: 'Phạm Thị D',
    age: 28,
    gender: 'Nữ',
    phone: '0976543210',
    email: 'phamthid@example.com',
    address: '321 Đường Điện Biên Phủ, Q.Bình Thạnh, TP.HCM',
    diagnosis: 'Đau vai',
    notes: 'Bệnh nhân làm việc văn phòng nhiều, cần tư vấn thêm về tư thế làm việc.',
    startDate: '20/03/2023',
    nextAppointment: '20/04/2023',
  },
};

// Mock patient exercise data
const MOCK_PATIENT_EXERCISES = {
  '1': [
    { id: '1', name: 'Tập vật lý trị liệu vai', status: 'completed', completedDate: '10/04/2023', progress: 100 },
    { id: '2', name: 'Tập phục hồi cơ lưng', status: 'in_progress', completedDate: null, progress: 60 },
    { id: '3', name: 'Bài tập tăng cường cơ chân', status: 'not_started', completedDate: null, progress: 0 },
  ],
  '2': [
    { id: '4', name: 'Tập cổ tay', status: 'completed', completedDate: '12/04/2023', progress: 100 },
    { id: '5', name: 'Tập phục hồi cổ', status: 'completed', completedDate: '14/04/2023', progress: 100 },
  ],
  '3': [
    { id: '6', name: 'Bài tập khớp gối', status: 'in_progress', completedDate: null, progress: 40 },
    { id: '2', name: 'Tập phục hồi cơ lưng', status: 'not_started', completedDate: null, progress: 0 },
  ],
  '4': [
    { id: '1', name: 'Tập vật lý trị liệu vai', status: 'in_progress', completedDate: null, progress: 75 },
  ],
};

// Available exercises to assign to patients
const AVAILABLE_EXERCISES = [
  { id: '1', name: 'Tập vật lý trị liệu vai', duration: '15 phút', intensity: 'Nhẹ' },
  { id: '2', name: 'Tập phục hồi cơ lưng', duration: '10 phút', intensity: 'Trung bình' },
  { id: '3', name: 'Bài tập tăng cường cơ chân', duration: '20 phút', intensity: 'Cao' },
  { id: '4', name: 'Tập cổ tay', duration: '10 phút', intensity: 'Nhẹ' },
  { id: '5', name: 'Tập phục hồi cổ', duration: '8 phút', intensity: 'Nhẹ' },
  { id: '6', name: 'Bài tập khớp gối', duration: '15 phút', intensity: 'Trung bình' },
  { id: '7', name: 'Tập mềm khớp cổ chân', duration: '12 phút', intensity: 'Nhẹ' },
  { id: '8', name: 'Bài tập hồi phục đau khớp', duration: '25 phút', intensity: 'Cao' },
];

export default function PatientDetail() {
  const params = useLocalSearchParams();
  const colorScheme = useColorScheme() ?? 'light';
  const patientId = params.id as string;
  const patient = MOCK_PATIENTS[patientId as keyof typeof MOCK_PATIENTS];
  const exercises = MOCK_PATIENT_EXERCISES[patientId as keyof typeof MOCK_PATIENT_EXERCISES] || [];
  
  const [showAddExercise, setShowAddExercise] = useState(false);
  const [selectedExercises, setSelectedExercises] = useState<string[]>([]);

  // Toggle selection of an exercise to add
  const toggleExerciseSelection = (exerciseId: string) => {
    if (selectedExercises.includes(exerciseId)) {
      setSelectedExercises(selectedExercises.filter(id => id !== exerciseId));
    } else {
      setSelectedExercises([...selectedExercises, exerciseId]);
    }
  };

  // Add selected exercises to patient's program
  const addExercisesToPatient = () => {
    // Here you would typically make an API call to add exercises
    // For demo purposes, just show an alert
    alert(`Đã thêm ${selectedExercises.length} bài tập cho bệnh nhân ${patient.name}`);
    setShowAddExercise(false);
    setSelectedExercises([]);
  };

  // Get status color based on exercise status
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return ExtendedColors.success;
      case 'in_progress':
        return ExtendedColors.warning;
      case 'not_started':
        return ExtendedColors.darkGray;
      default:
        return ExtendedColors.darkGray;
    }
  };

  // Get status text in Vietnamese
  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Đã hoàn thành';
      case 'in_progress':
        return 'Đang thực hiện';
      case 'not_started':
        return 'Chưa bắt đầu';
      default:
        return 'Không xác định';
    }
  };

  // Check if an exercise is already assigned to the patient
  const isExerciseAssigned = (exerciseId: string) => {
    return exercises.some(ex => ex.id === exerciseId);
  };

  return (
    <>
      <Stack.Screen
        options={{
          headerShown: true,
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
      
      <ScrollView 
        style={[styles.container, { backgroundColor: colorScheme === 'dark' ? ExtendedColors.darkBackground : Colors.white }]}
        contentContainerStyle={styles.contentContainer}
      >
        {/* Patient Info Card */}
        <View style={[styles.card, { backgroundColor: colorScheme === 'dark' ? '#444' : Colors.white }]}>
          <Text style={[styles.cardTitle, { color: Colors[colorScheme].text }]}>Thông tin bệnh nhân</Text>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Họ tên:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.name}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Tuổi:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.age}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Giới tính:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.gender}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Số điện thoại:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.phone}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Email:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.email}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Địa chỉ:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.address}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Chẩn đoán:</Text>
            <Text style={[styles.infoValue, { color: Colors.primary }]}>{patient.diagnosis}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Ngày bắt đầu điều trị:</Text>
            <Text style={[styles.infoValue, { color: Colors[colorScheme].text }]}>{patient.startDate}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Lịch hẹn tiếp theo:</Text>
            <Text style={[styles.infoValue, { color: ExtendedColors.secondary }]}>{patient.nextAppointment}</Text>
          </View>
          
          <View style={styles.notesContainer}>
            <Text style={[styles.infoLabel, { color: ExtendedColors.darkGray }]}>Ghi chú:</Text>
            <Text style={[styles.notesText, { color: Colors[colorScheme].text }]}>{patient.notes}</Text>
          </View>
        </View>
        
        {/* Exercise Progress Card */}
        <View style={[styles.card, { backgroundColor: colorScheme === 'dark' ? '#444' : Colors.white }]}>
          <View style={styles.cardHeader}>
            <Text style={[styles.cardTitle, { color: Colors[colorScheme].text }]}>Tiến độ bài tập</Text>
            <TouchableOpacity 
              style={styles.addButton}
              onPress={() => setShowAddExercise(true)}
            >
              <Text style={styles.addButtonText}>+ Thêm bài tập</Text>
            </TouchableOpacity>
          </View>
          
          {exercises.length > 0 ? (
            exercises.map(exercise => (
              <View key={exercise.id} style={styles.exerciseItem}>
                <View style={styles.exerciseHeader}>
                  <Text style={[styles.exerciseName, { color: Colors[colorScheme].text }]}>
                    {exercise.name}
                  </Text>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(exercise.status) }]}>
                    <Text style={styles.statusText}>{getStatusText(exercise.status)}</Text>
                  </View>
                </View>
                
                <View style={styles.progressContainer}>
                  <View style={[styles.progressBar, { backgroundColor: colorScheme === 'dark' ? '#555' : ExtendedColors.lightGray }]}>
                    <View 
                      style={[
                        styles.progressFill, 
                        { 
                          width: `${exercise.progress}%`,
                          backgroundColor: getStatusColor(exercise.status)
                        }
                      ]} 
                    />
                  </View>
                  <Text style={[styles.progressText, { color: ExtendedColors.darkGray }]}>
                    {exercise.progress}%
                  </Text>
                </View>
                
                {exercise.completedDate && (
                  <Text style={[styles.completedDate, { color: ExtendedColors.darkGray }]}>
                    Hoàn thành: {exercise.completedDate}
                  </Text>
                )}

                <TouchableOpacity 
                  style={styles.viewDetailsButton}
                  onPress={() => router.push(`/exercise-detail?id=${exercise.id}`)}
                >
                  <Text style={styles.viewDetailsText}>Xem chi tiết</Text>
                  <MaterialIcons name="chevron-right" size={16} color={Colors.primary} />
                </TouchableOpacity>
              </View>
            ))
          ) : (
            <Text style={[styles.emptyText, { color: ExtendedColors.darkGray }]}>
              Chưa có bài tập được gán cho bệnh nhân này
            </Text>
          )}
        </View>
      </ScrollView>
      
      {/* Add Exercise Modal */}
      {showAddExercise && (
        <View style={styles.modalOverlay}>
          <View style={[styles.modal, { backgroundColor: colorScheme === 'dark' ? '#333' : Colors.white }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: Colors[colorScheme].text }]}>
                Thêm bài tập cho bệnh nhân
              </Text>
              <TouchableOpacity onPress={() => {
                setShowAddExercise(false);
                setSelectedExercises([]);
              }}>
                <FontAwesome name="close" size={24} color={ExtendedColors.darkGray} />
              </TouchableOpacity>
            </View>
            
            <FlatList
              data={AVAILABLE_EXERCISES}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => {
                const isAssigned = isExerciseAssigned(item.id);
                const isSelected = selectedExercises.includes(item.id);
                
                return (
                  <TouchableOpacity 
                    style={[
                      styles.exerciseOption,
                      isSelected && styles.exerciseOptionSelected,
                      isAssigned && styles.exerciseOptionDisabled
                    ]}
                    onPress={() => !isAssigned && toggleExerciseSelection(item.id)}
                    disabled={isAssigned}
                  >
                    <View style={styles.exerciseOptionContent}>
                      <Text style={[
                        styles.exerciseOptionName, 
                        { color: isAssigned ? ExtendedColors.darkGray : Colors[colorScheme].text }
                      ]}>
                        {item.name}
                      </Text>
                      <View style={styles.exerciseOptionDetails}>
                        <Text style={[styles.exerciseOptionDuration, { color: ExtendedColors.darkGray }]}>
                          {item.duration}
                        </Text>
                        <Text style={[styles.exerciseOptionIntensity, { color: ExtendedColors.darkGray }]}>
                          • Cường độ: {item.intensity}
                        </Text>
                      </View>
                    </View>
                    
                    {isAssigned ? (
                      <Text style={styles.assignedBadge}>Đã gán</Text>
                    ) : (
                      <View style={[
                        styles.checkBox,
                        isSelected && { backgroundColor: Colors.primary, borderColor: Colors.primary }
                      ]}>
                        {isSelected && <FontAwesome name="check" size={14} color={Colors.white} />}
                      </View>
                    )}
                  </TouchableOpacity>
                );
              }}
              style={styles.exerciseList}
            />
            
            <View style={styles.modalFooter}>
              <TouchableOpacity 
                style={[
                  styles.addExercisesButton,
                  selectedExercises.length === 0 && styles.addExercisesButtonDisabled
                ]}
                onPress={addExercisesToPatient}
                disabled={selectedExercises.length === 0}
              >
                <Text style={styles.addExercisesButtonText}>
                  Thêm {selectedExercises.length} bài tập
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  card: {
    borderRadius: 10,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  addButton: {
    backgroundColor: Colors.primary,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  addButtonText: {
    color: Colors.white,
    fontWeight: 'bold',
    fontSize: 14,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  infoLabel: {
    width: 150,
    fontSize: 14,
    fontWeight: '500',
  },
  infoValue: {
    flex: 1,
    fontSize: 14,
  },
  notesContainer: {
    marginTop: 8,
  },
  notesText: {
    fontSize: 14,
    marginTop: 4,
    lineHeight: 20,
  },
  exerciseItem: {
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.1)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: '500',
    flex: 1,
  },
  statusBadge: {
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 12,
  },
  statusText: {
    color: Colors.white,
    fontSize: 12,
    fontWeight: '500',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 8,
  },
  progressBar: {
    flex: 1,
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: 8,
  },
  progressFill: {
    height: '100%',
  },
  progressText: {
    fontSize: 12,
    width: 35,
    textAlign: 'right',
  },
  completedDate: {
    fontSize: 12,
    marginBottom: 8,
  },
  viewDetailsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
  },
  viewDetailsText: {
    color: Colors.primary,
    fontSize: 14,
    marginRight: 4,
  },
  emptyText: {
    textAlign: 'center',
    fontSize: 14,
    fontStyle: 'italic',
    padding: 20,
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modal: {
    width: '90%',
    maxHeight: '80%',
    borderRadius: 10,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  exerciseList: {
    maxHeight: 400,
  },
  exerciseOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.05)',
  },
  exerciseOptionSelected: {
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
  },
  exerciseOptionDisabled: {
    opacity: 0.6,
  },
  exerciseOptionContent: {
    flex: 1,
  },
  exerciseOptionName: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  exerciseOptionDetails: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  exerciseOptionDuration: {
    fontSize: 14,
    marginRight: 8,
  },
  exerciseOptionIntensity: {
    fontSize: 14,
  },
  assignedBadge: {
    fontSize: 12,
    color: ExtendedColors.darkGray,
    fontStyle: 'italic',
  },
  checkBox: {
    width: 22,
    height: 22,
    borderRadius: 22,
    borderWidth: 2,
    borderColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalFooter: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
  },
  addExercisesButton: {
    backgroundColor: Colors.primary,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  addExercisesButtonDisabled: {
    backgroundColor: 'rgba(0,0,0,0.2)',
  },
  addExercisesButtonText: {
    color: Colors.white,
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 