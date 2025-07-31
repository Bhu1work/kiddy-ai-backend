# 🎮 Kiddy AI Backend

A **child-safe AI companion** with voice interaction, emotional intelligence, and local data storage. Built with FastAPI, Google Gemini, and speech recognition.

## ✨ Features

### 🎤 **Voice Interaction**
- **Speech-to-Text**: Real-time voice recognition using Google Cloud Speech API
- **Text-to-Speech**: AI responds with natural voice using Google Cloud TTS
- **Voice-to-Voice**: Complete conversational experience

### 🧠 **Emotional Intelligence**
- **Mood Detection**: Analyzes kid's emotional state from voice/text
- **Responsive AI**: Matches kid's mood (comforts sad kids, matches happy energy)
- **Age-Appropriate**: Tailored responses for different age groups (3-11 years)

### 🎯 **Character System**
- **Custom Names**: Kids can name their AI buddy (e.g., "Sparkle")
- **Name Recognition**: AI responds when called by its custom name
- **Personality Consistency**: Maintains character throughout conversation

### 🔒 **Privacy & Safety**
- **Local Storage**: All data stays on device, no cloud storage
- **COPPA Compliant**: Child-safe content and privacy protection
- **Token Limits**: Daily usage controls to prevent overuse
- **3-Day Logs**: Automatic conversation cleanup

### 🛡️ **Safety Features**
- **Content Filtering**: Blocks inappropriate topics
- **PII Scrubbing**: Removes personal information
- **Emotional Support**: Encourages positive interaction
- **Parent Controls**: Session management and monitoring

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Clone the repository
git clone <your-repo-url>
cd kiddy-ai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure API Keys**
Create a `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
DEV_MODE=true
MAX_TOKENS_PER_DAY=4096
LOG_RETENTION_DAYS=3
```

### 3. **Run the Server**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. **Test the Demo**
Visit: `http://localhost:8000/public/mic-demo.html`

## 📁 Project Structure

```
kiddy-ai-backend/
├── app/
│   ├── api/v1/
│   │   └── chat.py          # API endpoints
│   ├── core/
│   │   ├── constants.py      # System prompts & config
│   │   ├── guardrails.py     # Safety & token management
│   │   └── settings.py       # Environment configuration
│   └── services/
│       ├── emotion_service.py # Mood detection
│       ├── gemini_service.py  # AI responses
│       ├── memory.py         # Local storage
│       ├── stt_service.py    # Speech-to-Text
│       └── tts_service.py    # Text-to-Speech
├── public/
│   └── mic-demo.html        # Demo frontend
├── tests/                   # Test files
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🎯 API Endpoints

### **Setup Session**
```http
POST /v1/setup
{
  "kid_name": "Alex",
  "age": 7,
  "buddy_name": "Sparkle"
}
```

### **Chat (Text or Voice)**
```http
POST /v1/chat
{
  "session_id": "abc123",
  "message": "Hello Sparkle!",     // Text input
  "audio": "base64_audio_data"     // Voice input (optional)
}
```

**Response:**
```json
{
  "text": "Hi Alex! I'm Sparkle, your AI buddy!",
  "emotion": "cheerful",
  "audio": "base64_mp3_data",
  "transcribed": "Hello Sparkle!"  // If voice input
}
```

## 🔧 Configuration

### **Environment Variables**
- `GOOGLE_API_KEY`: Google Generative AI API key
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud credentials
- `DEV_MODE`: Enable development mode (default: false)
- `MAX_TOKENS_PER_DAY`: Daily token limit (default: 4096)
- `LOG_RETENTION_DAYS`: Conversation log retention (default: 3)

### **AI Model**
- **Model**: `gemini-1.5-pro`
- **Features**: Built-in safety, content filtering
- **Optimization**: Child-safe prompts and responses

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Test voice system
python test_voice_system.py

# Test API endpoints
curl -X POST http://localhost:8000/v1/setup \
  -H "Content-Type: application/json" \
  -d '{"kid_name":"Alex","age":7,"buddy_name":"Sparkle"}'
```

## 🛡️ Safety & Compliance

### **COPPA Compliance**
- ✅ No personal data collection
- ✅ Local-only storage
- ✅ Child-safe content filtering
- ✅ Parental controls
- ✅ Age-appropriate responses

### **Content Safety**
- ✅ Violence prevention
- ✅ Inappropriate content blocking
- ✅ Privacy protection
- ✅ Emotional safety

## 🚀 Deployment

### **Local Development**
```bash
python -m uvicorn app.main:app --reload
```

### **Production**
```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t kiddy-ai .
docker run -p 8000:8000 kiddy-ai
```

## 📊 Performance

- **Response Time**: < 2 seconds for voice-to-voice
- **Accuracy**: High-quality speech recognition
- **Scalability**: Stateless API design
- **Reliability**: Error handling and fallbacks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the [PROJECT_STATUS.md](PROJECT_STATUS.md) for current status
- Review [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for setup help
- Open an issue on GitHub

---

**Made with ❤️ for kids' safety and learning** 