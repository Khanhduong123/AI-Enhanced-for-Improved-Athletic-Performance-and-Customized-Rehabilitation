import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, useColorScheme, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { Colors } from '../../constants/Colors';
import { useAuthStore } from '../../store/authStore';
import { Link, router } from 'expo-router';

const RegisterScreen = () => {
  const colorScheme = useColorScheme() ?? 'light';
  const { register } = useAuthStore();
  
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<'doctor' | 'patient'>('patient');

  const handleRegister = async () => {
    // Kiểm tra form
    if (!fullName || !email || !password || !confirmPassword) {
      Alert.alert('Lỗi', 'Vui lòng điền đầy đủ thông tin');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Lỗi', 'Mật khẩu không khớp');
      return;
    }

    setIsLoading(true);

    try {
      // Chuẩn bị dữ liệu gửi đi khớp với API backend
      const userData = {
        email: email.trim(),
        full_name: fullName.trim(),
        // Chuẩn hóa role để phù hợp với backend
        role: selectedRole === 'doctor' ? 'Doctor' : 'Patient',
        ...(specialization && {specialization: specialization.trim()}),
        password: password
      };

      // Gọi hàm register từ store (đã kết nối API)
      await register(
        userData.email,
        userData.full_name,
        userData.role,
        userData.password,
        specialization && userData.specialization
      );

      // Thông báo thành công và chuyển hướng
      Alert.alert(
        'Đăng ký thành công',
        'Tài khoản của bạn đã được tạo. Vui lòng đăng nhập.',
        [{ text: 'OK', onPress: () => router.replace('/(auth)/login') }]
      );

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
      Alert.alert('Lỗi đăng ký', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: Colors[colorScheme].background }}>
      <View style={styles.container}>
        <View style={styles.headerContainer}>
          <Text style={[styles.title, { color: Colors[colorScheme].text }]}>
            Đăng ký tài khoản
          </Text>
          <Text style={[styles.subtitle, { color: Colors.primary }]}>
            Ứng dụng Phục hồi chức năng
          </Text>
        </View>

        <View style={styles.formContainer}>
          <TextInput
            style={[
              styles.input,
              { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5', color: Colors[colorScheme].text }
            ]}
            placeholder="Họ và tên"
            placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
            value={fullName}
            onChangeText={setFullName}
            autoCapitalize="words"
            textContentType="name"
          />
          
          <TextInput
            style={[
              styles.input,
              { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5', color: Colors[colorScheme].text }
            ]}
            placeholder="Email"
            placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
          
          <TextInput
            style={[
              styles.input,
              { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5', color: Colors[colorScheme].text }
            ]}
            placeholder="Mật khẩu"
            placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
          
          <TextInput
            style={[
              styles.input,
              { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5', color: Colors[colorScheme].text }
            ]}
            placeholder="Xác nhận mật khẩu"
            placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            secureTextEntry
          />

          {/* Role selection */}
          <View style={styles.roleContainer}>
            <Text style={[styles.roleLabel, { color: Colors[colorScheme].text }]}>Đăng ký với vai trò:</Text>
            
            <View style={styles.roleOptions}>
              <TouchableOpacity
                style={[
                  styles.roleOption,
                  selectedRole === 'patient' && { backgroundColor: Colors.primary }
                ]}
                onPress={() => setSelectedRole('patient')}
              >
                <Text style={[
                  styles.roleText,
                  selectedRole === 'patient' && { color: Colors.white }
                ]}>
                  Bệnh nhân
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.roleOption,
                  selectedRole === 'doctor' && { backgroundColor: Colors.primary }
                ]}
                onPress={() => setSelectedRole('doctor')}
              >
                <Text style={[
                  styles.roleText,
                  selectedRole === 'doctor' && { color: Colors.white }
                ]}>
                  Bác sĩ
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Chuyên môn */}
          {selectedRole == "doctor" && (
              <TextInput
              style={[
                styles.input,
                { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5', color: Colors[colorScheme].text }
              ]}
              placeholder="Chuyên môn (VD: Bác sĩ điều trị vật lý trị liệu)"
              placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
              value={specialization}
              onChangeText={setSpecialization}
            />
          )}
     

       

          <TouchableOpacity
            style={[styles.registerButton, { opacity: isLoading ? 0.7 : 1 }]}
            onPress={handleRegister}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color={Colors.white} />
            ) : (
              <Text style={styles.registerButtonText}>Đăng ký</Text>
            )}
          </TouchableOpacity>

          <View style={styles.loginContainer}>
            <Text style={{ color: Colors[colorScheme].text }}>
              Đã có tài khoản?
            </Text>
            <Link href="/(auth)/login" asChild>
              <TouchableOpacity>
                <Text style={{ color: Colors.primary, marginLeft: 5, fontWeight: 'bold' }}>
                  Đăng nhập
                </Text>
              </TouchableOpacity>
            </Link>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  headerContainer: {
    alignItems: 'center',
    marginTop: 40,
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
  },
  formContainer: {
    width: '100%',
  },
  input: {
    height: 50,
    borderRadius: 8,
    marginBottom: 16,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  roleContainer: {
    marginBottom: 20,
  },
  roleLabel: {
    fontSize: 16,
    marginBottom: 8,
  },
  roleOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  roleOption: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.05)',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  roleText: {
    fontWeight: '500',
  },
  registerButton: {
    backgroundColor: Colors.primary,
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  registerButtonText: {
    color: Colors.white,
    fontSize: 16,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
    marginBottom: 30,
  },
});

export default RegisterScreen; 