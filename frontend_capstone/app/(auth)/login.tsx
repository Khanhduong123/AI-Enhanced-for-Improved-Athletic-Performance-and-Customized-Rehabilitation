import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, TextInput, useColorScheme, ActivityIndicator, Alert } from 'react-native';
import { Colors } from '../../constants/Colors';
import { useAuthStore } from '../../store/authStore';
import { Link } from 'expo-router';

const LoginScreen = () => {
  const colorScheme = useColorScheme() ?? 'light';
  const { login } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Lỗi', 'Vui lòng nhập email và mật khẩu');
      return;
    }

    setIsLoading(true);

    try {
      await login(email, password);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.';
      Alert.alert('Lỗi đăng nhập', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={styles.headerContainer}>
        <Image
          source={require('../../assets/images/icon.png')}
          style={styles.logo}
          resizeMode="contain"
        />
        <Text style={[styles.title, { color: Colors[colorScheme].text }]}>
          Đăng nhập
        </Text>
        <Text style={[styles.subtitle, { color: Colors.primary }]}>
          Ứng dụng Phục hồi chức năng
        </Text>
      </View>

      <View style={styles.formContainer}>
        <TextInput
          style={[
            styles.input,
            { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5' }
          ]}
          placeholder="Email"
          // placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        
        <TextInput
          style={[
            styles.input,
            { backgroundColor: colorScheme === 'dark' ? '#333' : '#f5f5f5' }
          ]}
          placeholder="Mật khẩu"
          // placeholderTextColor={colorScheme === 'dark' ? '#999' : '#888'}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity
          style={[styles.loginButton, { opacity: isLoading ? 0.7 : 1 }]}
          onPress={handleLogin}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color={Colors.white} />
          ) : (
            <Text style={styles.loginButtonText}>Đăng nhập</Text>
          )}
        </TouchableOpacity>

        <View style={styles.registerContainer}>
          <Text style={{ color: Colors[colorScheme].text }}>
            Chưa có tài khoản?
          </Text>
          <Link href="/(auth)/register" asChild>
            <TouchableOpacity>
              <Text style={{ color: Colors.primary, marginLeft: 5, fontWeight: 'bold' }}>
                Đăng ký
              </Text>
            </TouchableOpacity>
          </Link>
        </View>
      </View>
    </View>
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
    marginBottom: 40,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 20,
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
  loginButton: {
    backgroundColor: Colors.primary,
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  loginButtonText: {
    color: Colors.white,
    fontSize: 16,
    fontWeight: 'bold',
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
  },
});

export default LoginScreen; 