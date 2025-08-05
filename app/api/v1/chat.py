from __future__ import annotations

"""API routes for parent setup and child chat.

* `/v1/setup`  – parent creates a session; nothing persists off‑device.
* `/v1/chat`   – child sends a prompt; backend returns {text, emotion, audio}.
* `/v1/welcome` – get welcome message when starting conversation.
* `/v1/export-logs` – parent exports conversation logs with PIN verification.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.services.gemini_service import get_reply, get_welcome_reply
from app.services.emotion_service import detect_emotion, detect_kid_emotion, get_emotional_response_style
from app.services.tts_service import synthesize
from app.services.stt_service import transcribe_audio, is_audio_valid
from app.services.memory import insert, get_logs

router = APIRouter(prefix="/v1", tags=["kiddy"])

# ---------------------------------------------------------------------------
# Pydantic Schemas -----------------------------------------------------------
# ---------------------------------------------------------------------------

class SetupRequest(BaseModel):
    kid_name: str = Field(..., max_length=40)
    age: int = Field(..., ge=3, le=11)
    buddy_name: str = Field(..., max_length=30)

class SetupResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field("", max_length=300)  # Optional text message
    audio: str = Field("", max_length=5000000)  # Optional base64 audio data

class ChatResponse(BaseModel):
    text: str
    emotion: str
    audio: str  # base64 MP3
    transcribed: str = ""  # Original transcribed text (for debugging)

class WelcomeRequest(BaseModel):
    session_id: str

class WelcomeResponse(BaseModel):
    text: str
    emotion: str
    audio: str  # base64 MP3

class ExportLogsRequest(BaseModel):
    session_id: str
    pin: str = Field(..., min_length=4, max_length=8)

class ExportLogsResponse(BaseModel):
    logs: list[str]
    session_info: dict[str, str | int]
    total_conversations: int

# ---------------------------------------------------------------------------
# In‑memory session registry – persists only for process lifetime.
# ---------------------------------------------------------------------------
_sessions: dict[str, dict[str, str | int]] = {}

# Parent PIN for log export (in production, this should be stored securely)
PARENT_PIN = "1234"  # Simple 4-digit PIN for demo purposes

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _validate_session(session_id: str) -> dict[str, str | int]:
    """Validate session and return session data."""
    try:
        session_data = _sessions[session_id]
        if not session_data:
            raise KeyError("Session data is empty")
        return session_data
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Session not found. Please setup again."
        ) from exc

# ---------------------------------------------------------------------------
# Routes --------------------------------------------------------------------
# ---------------------------------------------------------------------------

@router.post("/setup", response_model=SetupResponse)
async def setup(req: SetupRequest):
    """Parent onboarding – returns opaque session UUID."""
    session_id = uuid.uuid4().hex
    _sessions[session_id] = {
        "kid_name": req.kid_name,
        "age": req.age,
        "buddy_name": req.buddy_name,
    }
    return {"session_id": session_id}


@router.post("/welcome", response_model=WelcomeResponse)
async def welcome(req: WelcomeRequest):
    """Get a welcome message when starting conversation."""
    ctx = _validate_session(req.session_id)
    
    try:
        # Generate welcome message
        welcome_text = await get_welcome_reply(
            ctx["buddy_name"],
            ctx["age"]
        )
        
        # Detect emotion for TTS
        emotion_tag = detect_emotion(welcome_text)
        
        try:
            audio_b64 = synthesize(welcome_text, emotion_tag)
        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            # Return empty audio if TTS fails
            audio_b64 = ""
        
        return {
            "text": welcome_text,
            "emotion": emotion_tag,
            "audio": audio_b64
        }
    except Exception as exc:
        print(f"Welcome endpoint error: {exc}")
        # Return a simple fallback response
        return {
            "text": f"Hey {ctx.get('buddy_name', 'Buddy')}! What's up?",
            "emotion": "friendly",
            "audio": ""
        }


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Handle chat messages with comprehensive error handling."""
    try:
        ctx = _validate_session(req.session_id)
        print(f"Processing chat for session: {req.session_id}, kid: {ctx.get('kid_name')}")
        
        # Process input - prioritize audio over text
        user_message = ""
        
        if req.audio and req.audio.strip():
            print(f"Processing audio input (length: {len(req.audio)})")
            
            # Validate audio data
            if not is_audio_valid(req.audio):
                print("Audio validation failed")
                raise HTTPException(status_code=400, detail="Invalid audio data")
            
            # Transcribe audio to text
            print("Transcribing audio...")
            transcribed_text = transcribe_audio(req.audio)
            print(f"Transcription result: '{transcribed_text}'")
            
            if transcribed_text:
                user_message = transcribed_text
                print(f"Using transcribed text: '{user_message}'")
            else:
                print("Transcription returned None")
                raise HTTPException(status_code=400, detail="Could not understand audio. Please try speaking clearly!")
        
        elif req.message and req.message.strip():
            user_message = req.message
            print(f"Using text message: '{user_message}'")
        else:
            raise HTTPException(status_code=400, detail="Please provide either text or audio input")
        
        # Enhanced emotion detection from kid's input
        kid_emotion = detect_kid_emotion(user_message)
        response_style = get_emotional_response_style(kid_emotion)
        print(f"Detected emotion: {kid_emotion}, response style: {response_style}")
        
        # Generate AI response with age and emotion context
        text_reply = await get_reply(
            req.session_id, 
            user_message, 
            ctx["buddy_name"],
            ctx["age"],
            kid_emotion
        )
        print(f"AI response: '{text_reply}'")
        
        # Detect emotion for TTS
        emotion_tag = detect_emotion(text_reply)
        print(f"TTS emotion: {emotion_tag}")
        
        try:
            audio_b64 = synthesize(text_reply, emotion_tag)
            print(f"TTS successful, audio length: {len(audio_b64)}")
        except Exception as tts_error:
            print(f"TTS Error in chat: {tts_error}")
            audio_b64 = ""
        
        # Store locally for parent review (3‑day ring buffer)
        insert(req.session_id, f"Q: {user_message}\nA: {text_reply}")
        
        return {
            "text": text_reply, 
            "emotion": emotion_tag, 
            "audio": audio_b64,
            "transcribed": user_message if req.audio else ""
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as exc:
        print(f"Unexpected error in chat: {exc}")
        raise HTTPException(status_code=500, detail="Oops, something went wrong. Let's try again!") from exc


@router.post("/export-logs", response_model=ExportLogsResponse)
async def export_logs(req: ExportLogsRequest):
    """Parent-only endpoint to export conversation logs with PIN verification."""
    
    # Validate session exists
    session_info = _validate_session(req.session_id)
    
    # Verify PIN (simple string comparison for demo)
    if req.pin != PARENT_PIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid PIN. Access denied."
        )
    
    try:
        # Retrieve logs for the session
        logs = get_logs(req.session_id)
        
        if not logs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No logs found for this session"
            )
        
        return {
            "logs": logs,
            "session_info": session_info,
            "total_conversations": len(logs)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to export logs") from exc
