#!/usr/bin/env python3
"""
Environment Setup Helper Script

This script helps you set up the required environment variables for the Kiddy AI Backend.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with template values."""
    env_content = """# Google API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Google Cloud Credentials
# Download your service account key from Google Cloud Console
# and place the JSON file in your project directory
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# Optional: Google Cloud Text-to-Speech settings
GOOGLE_TTS_VOICE=en-US-Standard-F
GOOGLE_TTS_PROJECT=your-gcp-project-id

# Development settings
MAX_TOKENS_PER_DAY=4096
LOG_RETENTION_DAYS=3

# Development mode (allows missing env vars with warnings)
DEV_MODE=true
"""
    
    env_path = Path(".env")
    if env_path.exists():
        print(".env file already exists. Skipping creation.")
        return
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("Created .env file with template values.")
    print("Please edit the .env file with your actual API keys and credentials.")

def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment variables...")
    
    required_vars = [
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nSee ENVIRONMENT_SETUP.md for setup instructions.")
        return False
    else:
        print("All required environment variables are set!")
        return True

def test_settings():
    """Test if settings can be loaded successfully."""
    print("Testing settings configuration...")
    
    try:
        from app.core.settings import get_settings
        settings = get_settings()
        print("Settings loaded successfully!")
        return True
    except Exception as e:
        print(f"Failed to load settings: {e}")
        return False

def main():
    """Main function."""
    print("Kiddy AI Backend Environment Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Check environment variables
    env_ok = check_environment()
    
    # Test settings
    settings_ok = test_settings()
    
    print("\n" + "=" * 40)
    if env_ok and settings_ok:
        print("Environment setup complete! You can now run your application.")
    else:
        print("Environment setup incomplete. Please follow the instructions above.")
        print("\nQuick fix: Set DEV_MODE=true in your .env file for development.")

if __name__ == "__main__":
    main() 