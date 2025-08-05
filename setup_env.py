#!/usr/bin/env python3
"""
Environment setup script for Kiddy AI Backend.

This script helps set up the required environment variables for the Kiddy AI Backend.
It will create a .env file with the necessary configuration.
"""

import os
import sys
from pathlib import Path

def main():
    """Set up environment variables for Kiddy AI Backend."""
    
    print("🔧 Setting up Kiddy AI Backend environment...")
    print()
    
    # Check if .env file already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print("📝 Please enter your Google API key:")
    print("   Get it from: https://makersuite.google.com/app/apikey")
    api_key = input("Google API Key: ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        return
    
    # Get credentials file path
    print()
    print("📁 Please enter the path to your Google Cloud credentials JSON file:")
    print("   Get it from: https://console.cloud.google.com/apis/credentials")
    creds_path = input("Credentials file path: ").strip()
    
    if not creds_path:
        print("❌ Credentials file path is required!")
        return
    
    # Validate credentials file exists
    if not Path(creds_path).exists():
        print(f"❌ Credentials file not found: {creds_path}")
        return
    
    # Create .env file
    env_content = f"""# Kiddy AI Backend Environment Configuration

# Google API Configuration
GOOGLE_API_KEY={api_key}
GOOGLE_APPLICATION_CREDENTIALS={creds_path}

# Optional Settings
GOOGLE_TTS_VOICE=en-US-Standard-F
GOOGLE_TTS_PROJECT=
MAX_TOKENS_PER_DAY=4096
LOG_RETENTION_DAYS=3
DEV_MODE=true
"""
    
    # Write .env file
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print()
        print("✅ Environment setup complete!")
        print()
        print("📋 Created .env file with the following configuration:")
        print(f"   Google API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"   Credentials File: {creds_path}")
        print()
        print("🚀 You can now start the backend with:")
        print("   docker-compose up kiddy-ai-dev")
        print()
        print("⚠️  IMPORTANT: Never commit your .env file to version control!")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return

if __name__ == "__main__":
    main() 