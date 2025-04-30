/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

// Define custom colors
const primaryColor = '#4299E1'; // Blue 500
const secondaryColor = '#EDF2F7'; // Gray 100
const accentColor = '#38B2AC'; // Teal 500
const lightBackground = '#FFFFFF'; // White
const darkBackground = '#1A202C'; // Gray 900
const lightText = '#2D3748'; // Gray 800
const darkText = '#E2E8F0'; // Gray 200
const lightIcon = '#718096'; // Gray 500
const darkIcon = '#A0AEC0'; // Gray 400
const errorColor = '#E53E3E'; // Red 500
const successColor = '#48BB78'; // Green 500
const whiteColor = '#FFFFFF';
const blackColor = '#000000';

const tintColorLight = '#0090ff';
const tintColorDark = '#fff';

export const Colors = {
  light: {
    text: '#000000',
    background: '#ffffff',
    tint: tintColorLight,
    tabIconDefault: '#ccc',
    tabIconSelected: tintColorLight,
    cardBackground: '#fff',
    border: '#e0e0e0',
  },
  dark: {
    text: '#fff',
    background: '#121212',
    tint: tintColorDark,
    tabIconDefault: '#ccc',
    tabIconSelected: tintColorDark,
    cardBackground: '#1e1e1e',
    border: '#333333',
  },
  
  // Common Colors
  primary: '#53F0A1',
  primaryDark: '#007acc',
  primaryLight: '#66b3ff',
  
  secondary: '#4CAF50',
  secondaryDark: '#388E3C',
  secondaryLight: '#81C784',
  
  accent: '#FFC107',
  danger: '#F44336',
  warning: '#FF9800',
  success: '#4CAF50',
  info: '#2196F3',
  
  grey: '#9E9E9E',
  greyLight: '#E0E0E0',
  greyDark: '#616161',
  
  white: '#FFFFFF',
  black: '#000000',
};

// Extended colors for additional UI elements
export const ExtendedColors = {
  ...Colors,
  darkGray: '#666666',
  lightGray: '#f0f0f0',
  darkBackground: '#121212',
  secondary: '#4CAF50',
  danger: '#F44336',
  warning: '#FFC107',
  success: '#4CAF50',
  info: '#2196F3',
  failed: '#D32F2F',
}; 
