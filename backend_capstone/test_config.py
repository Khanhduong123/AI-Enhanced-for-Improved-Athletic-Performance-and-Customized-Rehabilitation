#!/usr/bin/env python
"""
Simple configuration test script
This script only tests the app_config module without other dependencies
"""
import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_app_config():
    """Test only the app_config module"""
    try:
        # Import the settings module directly, avoiding other imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'v1', 'configs'))
        import app_config
        settings = app_config.settings
        
        # Print settings
        print("Configuration loaded successfully.")
        print("-" * 50)
        print(f"APP_NAME: {settings.APP_NAME}")
        print(f"APP_VERSION: {settings.APP_VERSION}")
        print(f"PORT: {settings.PORT}")
        print(f"UPLOAD_DIR: {settings.UPLOAD_DIR}")
        print(f"CORS_ORIGINS: {settings.get_cors_origins()}")
        print(f"GRAFANA_USER: {settings.GRAFANA_USER}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_config() 