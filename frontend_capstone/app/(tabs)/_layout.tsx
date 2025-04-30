import React, { useEffect } from 'react';
import { Stack, useRouter } from 'expo-router';
import { Colors } from '../../constants/Colors';
import { useAuthStore } from '../../store/authStore';

export default function TabLayout() {
  const { isLoggedIn, userRole } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    console.log('[Tabs] TabLayout mounted with role:', userRole);
    
    // Only redirect if not authenticated and this component is mounted
    // This avoids navigation attempts during initialization
    if (!isLoggedIn) {
      // We can't use router.replace here as it causes issues during initialization
      // Instead, we'll just log the state and let the root layout handle redirects
      console.log('[Tabs] User not authenticated in tabs');
    } else {
      console.log('[Tabs] User authenticated in tabs with role:', userRole);
    }
  }, [isLoggedIn, userRole]);

  console.log('[Tabs] Rendering TabLayout with role:', userRole);

  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerStyle: {
          backgroundColor: Colors.primary,
        },
        headerTintColor: Colors.white,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: 'Trang chủ',
        }}
      />
      <Stack.Screen
        name="doctor-dashboard"
        options={{
          title: 'Quản lý bệnh nhân',
        }}
      />
      <Stack.Screen
        name="patient-detail"
        options={{
          title: 'Chi tiết bệnh nhân',
        }}
      />
      <Stack.Screen
        name="exercise-detail"
        options={{
          title: 'Chi tiết bài tập',
        }}
      />
    </Stack>
  );
}
