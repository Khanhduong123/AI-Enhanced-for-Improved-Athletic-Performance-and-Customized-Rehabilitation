#!/usr/bin/env python
"""
Configuration check script
This script verifies that the application configuration loads correctly
"""
import os
import sys

# Make sure we can import from the current directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_configuration():
    """Check if the application configuration loads correctly"""
    try:
        # Import the settings module
        from src.v1.configs.app_config import settings
        
        # Print all settings (excluding sensitive info)
        print("Configuration loaded successfully.")
        print("-" * 50)
        print(f"APP_NAME: {settings.APP_NAME}")
        print(f"APP_VERSION: {settings.APP_VERSION}")
        print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
        print(f"DEBUG: {settings.DEBUG}")
        print(f"LOG_LEVEL: {settings.LOG_LEVEL}")
        print(f"MONGO_URI: {'*****' if settings.MONGO_URI else 'Not set'}")  # Redacted for security
        print(f"DB_NAME: {settings.DB_NAME}")
        print(f"UPLOAD_DIR: {settings.UPLOAD_DIR}")
        print(f"TEMP_DIR: {settings.TEMP_DIR}")
        print(f"CORS_ORIGINS: {settings.get_cors_origins()}")
        print("-" * 50)
        print("No errors found in configuration.")
        return True
    except Exception as e:
        print(f"Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_configuration()
    sys.exit(0 if success else 1) 