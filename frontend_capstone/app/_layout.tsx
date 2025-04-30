import React, { useEffect, useState } from 'react';
import { Stack, useRouter, Slot } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { View, Text, ActivityIndicator } from 'react-native';
import { Colors } from '../constants/Colors';

export default function RootLayout() {
  const { isLoggedIn, userRole, checkAuth } = useAuthStore();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateAuth = async () => {
      try {
        setIsLoading(true);
        console.log('[Navigation] Checking authentication state');
        // Verify if token is still valid
        await checkAuth();
        console.log('[Navigation] Auth check complete, authenticated:', isLoggedIn);
      } catch (error) {
        console.error('[Navigation] Auth check error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    validateAuth();
  }, []);

  useEffect(() => {
    if (!isLoading) {
      // Only navigate if not loading
      if (isLoggedIn) {
        console.log('[Navigation] User is authenticated, redirecting to tabs');
        // Use setTimeout to ensure navigation happens after layout is complete
        setTimeout(() => router.replace('/(tabs)'), 0);
      } else {
        console.log('[Navigation] User is not authenticated, redirecting to login');
        try {
          // Add a small delay to ensure state is fully updated before navigation
          setTimeout(() => {
            console.log('[Navigation] Executing redirect to login screen');
            router.replace('/(auth)/login');
          }, 100);
        } catch (error) {
          console.error('[Navigation] Error during navigation:', error);
          // Fallback attempt with different approach
          setTimeout(() => router.push('/(auth)/login'), 300);
        }
      }
    }
  }, [isLoggedIn, isLoading, router]);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={{ marginTop: 10, color: Colors.primary }}>Đang tải...</Text>
      </View>
    );
  }

  // Use Slot instead of Stack to fix navigation issues
  return <Slot />;
}
