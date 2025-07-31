# Environment Setup Guide

## Required Environment Variables

Your application requires the following environment variables to be set. Create a `.env` file in the root directory with the following variables:

### 1. Google API Key
```
GOOGLE_API_KEY=your_google_api_key_here
```
**How to get it:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and paste it as the value

### 2. Google Cloud Credentials
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```
**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Cloud Text-to-Speech API
   - Cloud Natural Language API
4. Create a service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and description
   - Grant it the following roles:
     - "Cloud Text-to-Speech Admin"
     - "Cloud Natural Language API Admin"
5. Create a key for the service account:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file
6. Place the JSON file in your project directory
7. Update the path in your `.env` file to point to this JSON file

### 3. Optional Settings
```
GOOGLE_TTS_VOICE=en-US-Standard-F
GOOGLE_TTS_PROJECT=your-gcp-project-id
MAX_TOKENS_PER_DAY=4096
LOG_RETENTION_DAYS=3
DEV_MODE=true
```

## Example .env file
```
GOOGLE_API_KEY=AIzaSyC...
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
GOOGLE_TTS_VOICE=en-US-Standard-F
GOOGLE_TTS_PROJECT=my-kiddy-ai-project
MAX_TOKENS_PER_DAY=4096
LOG_RETENTION_DAYS=3
DEV_MODE=true
```

## Development Mode
If you set `DEV_MODE=true`, the application will run with dummy values and show warnings instead of crashing when environment variables are missing. This is useful for development but should not be used in production.

## Security Notes
- Never commit your `.env` file to version control
- Keep your API keys and service account credentials secure
- In production, use real environment variables instead of `.env` files 