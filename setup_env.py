#!/usr/bin/env python3
"""Environment setup script for Kiddy AI Backend."""

import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file with user's credentials."""
    
    # Copy credentials file to local directory if it doesn't exist
    local_creds_path = Path("./kiddy-service.json")
    if not local_creds_path.exists():
        source_creds_path = Path(r"C:\Users\bhuva\.gcp\kiddy-service.json")
        if source_creds_path.exists():
            import shutil
            shutil.copy2(source_creds_path, local_creds_path)
            print("Copied credentials file to local directory!")
        else:
            print("Warning: Could not find source credentials file!")
    
    env_content = f"""# Google API Configuration
GOOGLE_API_KEY=AIzaSyCAqJ5ig6_irxVziwHFvxXknLxoPYwYDug

# Google Cloud Service Account (for TTS, Speech, Language APIs)
GOOGLE_APPLICATION_CREDENTIALS=/app/dev-credentials.json

# Google Cloud Text-to-Speech Configuration
GOOGLE_TTS_VOICE=en-US-Standard-F
GOOGLE_TTS_PROJECT=

# Application Settings
MAX_TOKENS_PER_DAY=4096
LOG_RETENTION_DAYS=3

# Development Mode (set to 1 for development, 0 for production)
DEV_MODE=1
"""
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Created .env file with your credentials!")
    print("Location: .env")
    print("API Key: AIzaSyCAqJ5ig6_irxVziwHFvxXknLxoPYwYDug")
    print("Credentials: ./kiddy-service.json")

def verify_credentials():
    """Verify that the credentials file exists and is valid JSON."""
    
    # First check if local file exists
    local_creds_path = Path("./kiddy-service.json")
    if local_creds_path.exists():
        try:
            with open(local_creds_path, 'r') as f:
                json.load(f)
            print("Local credentials file is valid JSON!")
            return True
        except json.JSONDecodeError:
            print("Error: Local credentials file is not valid JSON!")
            print(f"   Please check: {local_creds_path}")
            return False
    
    # Fallback to original location
    creds_path = Path(r"C:\Users\bhuva\.gcp\kiddy-service.json")
    
    if not creds_path.exists():
        print("Error: Credentials file not found!")
        print(f"   Expected location: {creds_path}")
        print("   Please ensure the file exists and try again.")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            json.load(f)
        print("Credentials file is valid JSON!")
        return True
    except json.JSONDecodeError:
        print("Error: Credentials file is not valid JSON!")
        print(f"   Please check: {creds_path}")
        return False

def main():
    """Main setup function."""
    print("Setting up Kiddy AI Backend Environment...")
    print()
    
    # Verify credentials
    if not verify_credentials():
        return
    
    # Create .env file
    create_env_file()
    
    print()
    print("Environment setup complete!")
    print()
    print("Next steps:")
    print("   1. Run: docker-compose up kiddy-ai-dev")
    print("   2. Open: http://localhost:8000")
    print("   3. Check health: http://localhost:8000/health")
    print()
    print("For production:")
    print("   docker-compose --profile prod up kiddy-ai-prod")

if __name__ == "__main__":
    main() 