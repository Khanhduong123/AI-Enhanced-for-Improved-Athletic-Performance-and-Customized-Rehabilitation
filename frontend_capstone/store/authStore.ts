import { create } from 'zustand';
import { persist, createJSONStorage, StateStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';
import { Colors } from '../constants/Colors';
import { Platform } from 'react-native';

export interface UserData {
  id?: string;
  _id?: string; // MongoDB sometimes returns _id instead of id
  email: string;
  full_name: string;
  role: string;
}

export interface AuthState {
  isLoggedIn: boolean;
  userRole: string | null;
  user: UserData | null;
  accessToken: string | null;
  
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, full_name: string, role: string, password: string, specialization?: string, diagnosis?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
}

const zustandStorage: StateStorage = {
  getItem: async (name: string): Promise<string | null> => {
    try {
      console.log('[AuthStore] Getting persisted state:', name);
      const value = await AsyncStorage.getItem(name);
      if (value) {
        console.log('[AuthStore] Found persisted state, length:', value.length);
      } else {
        console.log('[AuthStore] No persisted state found');
      }
      return value;
    } catch (error) {
      console.error('[AuthStore] Error getting persisted state:', error);
      return null;
    }
  },

  setItem: async (name: string, value: string): Promise<void> => {
    try {
      console.log('[AuthStore] Saving persisted state, length:', value.length);
      await AsyncStorage.setItem(name, value);
      console.log('[AuthStore] State saved successfully');
    } catch (error) {
      console.error('[AuthStore] Error saving persisted state:', error);
    }
  },

  removeItem: async (name: string): Promise<void> => {
    try {
      console.log('[AuthStore] Removing persisted state:', name);
      await AsyncStorage.removeItem(name);
      console.log('[AuthStore] State removed successfully');
    } catch (error) {
      console.error('[AuthStore] Error removing persisted state:', error);
    }
  },
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isLoggedIn: false,
      userRole: null,
      user: null,
      accessToken: null,
      
      login: async (email: string, password: string) => {
        try {
          console.log('[AuthStore] Attempting login with email:', email);
          
          const userData = await authAPI.login(email, password);
          console.log('[AuthStore] Login response received');
          
          const user: UserData = {
            id: userData.id || userData._id,
            _id: userData._id || userData.id,
            email: userData.email,
            full_name: userData.full_name,
            role: userData.role
          };
          
          const token = userData.token || userData.access_token;
          
          console.log('[AuthStore] User role:', user.role);
          console.log('[AuthStore] Token received:', token ? 'Yes (length: ' + token.length + ')' : 'No');
          
          if (!user.id && !user._id) {
            throw new Error('Invalid user data: Missing ID');
          }
          
          set({
            isLoggedIn: true,
            userRole: user.role,
            user: user,
            accessToken: token
          });
          
          console.log('[AuthStore] Login successful and state updated');
          console.log('[AuthStore] UserRole set to:', user.role);
        } catch (error) {
          console.error('[AuthStore] Login error:', error);
          throw error;
        }
      },
      
      register: async (email: string, full_name: string, role: string, password: string, specialization?: string) => {
        try {
          console.log('[AuthStore] Registering new user:', email, 'with role:', role);
          await authAPI.register({ 
            email, 
            full_name, 
            role, 
            password,
            specialization,
            
          });
          console.log('[AuthStore] Registration successful');
        } catch (error) {
          console.error('[AuthStore] Registration error:', error);
          throw error;
        }
      },
      
      logout: () => {
        console.log('[AuthStore] Logging out user');
        try {
          // Mark that we're in the process of logging out
          console.log('[AuthStore] Starting logout process');
          
          // Clear the async storage first using the available API
          // Create a Promise to handle async storage operations
          const clearStorage = async () => {
            try {
              await AsyncStorage.removeItem('auth-storage');
              console.log('[AuthStore] Successfully cleared storage directly');
            } catch (e) {
              console.error('[AuthStore] Error clearing storage directly:', e);
            }
          };
          
          // Start the async operation
          clearStorage();
          
          // Then use the standard method as a backup
          zustandStorage.removeItem('auth-storage');
          
          // Reset the state with a slight delay to ensure storage is cleared
          setTimeout(() => {
            set({
              isLoggedIn: false,
              userRole: null,
              user: null,
              accessToken: null
            });
            console.log('[AuthStore] Logout complete, auth state reset');
          }, 50);
        } catch (error) {
          console.error('[AuthStore] Error during logout:', error);
          // Still attempt to reset the state even if storage clear fails
          set({
            isLoggedIn: false,
            userRole: null,
            user: null,
            accessToken: null
          });
        }
      },
      
      checkAuth: async () => {
        const token = get().accessToken;
        const currentUser = get().user;
        
        console.log('[AuthStore] Checking authentication');
        console.log('[AuthStore] Current user:', currentUser?.email || 'None');
        console.log('[AuthStore] Has token:', token ? 'Yes' : 'No');
        
        if (!token) {
          console.log('[AuthStore] No token found, not authenticated');
          set({ isLoggedIn: false, userRole: null });
          return false;
        }
        
        try {
          const userData = await authAPI.getMe(token);
          console.log('[AuthStore] Auth check successful');
          
          if (userData) {
            const updatedUser: UserData = {
              id: userData.id || userData._id,
              _id: userData._id || userData.id,
              email: userData.email,
              full_name: userData.full_name,
              role: userData.role
            };
            
            console.log('[AuthStore] User role from API:', updatedUser.role);
            
            set({
              isLoggedIn: true,
              userRole: updatedUser.role,
              user: updatedUser
            });
            return true;
          } else {
            console.log('[AuthStore] No user data returned, authentication failed');
            set({ isLoggedIn: false, userRole: null });
            return false;
          }
        } catch (error) {
          console.error('[AuthStore] Authentication check error:', error);
          set({ isLoggedIn: false, userRole: null });
          return false;
        }
      }
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => zustandStorage),
      partialize: (state) => ({
        isLoggedIn: state.isLoggedIn,
        userRole: state.userRole,
        user: state.user,
        accessToken: state.accessToken
      }),
      onRehydrateStorage: () => (state) => {
        console.log('[AuthStore] State rehydrated:', state ? 'success' : 'failed');
        if (state) {
          console.log('[AuthStore] Rehydrated user role:', state.userRole);
          console.log('[AuthStore] Rehydrated login status:', state.isLoggedIn);
        }
      }
    }
  )
); 

