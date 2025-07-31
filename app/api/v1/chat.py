from __future__ import annotations

"""API routes for parent setup and child chat.

* `/v1/setup`  – parent creates a session; nothing persists off‑device.
* `/v1/chat`   – child sends a prompt; backend returns {text, emotion, audio}.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.services.gemini_service import get_reply
from app.services.emotion_service import detect_emotion, detect_kid_emotion, get_emotional_response_style
from app.services.tts_service import synthesize
from app.services.stt_service import transcribe_audio, is_audio_valid
from app.services.memory import insert

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

# ---------------------------------------------------------------------------
# In‑memory session registry – persists only for process lifetime.
# ---------------------------------------------------------------------------
_sessions: dict[str, dict[str, str | int]] = {}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _validate_session(session_id: str) -> dict[str, str | int]:
    try:
        return _sessions[session_id]
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid session") from exc

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


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    ctx = _validate_session(req.session_id)

    try:
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
        else:
            raise HTTPException(status_code=400, detail="Please provide either text or audio input")
        
        # Enhanced emotion detection from kid's input
        kid_emotion = detect_kid_emotion(user_message)
        response_style = get_emotional_response_style(kid_emotion)
        
        # Generate AI response with age and emotion context
        text_reply = await get_reply(
            req.session_id, 
            user_message, 
            ctx["buddy_name"],
            ctx["age"],
            kid_emotion
        )
        
        # Detect emotion for TTS
        emotion_tag = detect_emotion(text_reply)
        audio_b64 = synthesize(text_reply, emotion_tag)
        
        # Store locally for parent review (3‑day ring buffer)
        insert(req.session_id, f"Q: {user_message}\nA: {text_reply}")
        
        return {
            "text": text_reply, 
            "emotion": emotion_tag, 
            "audio": audio_b64,
            "transcribed": user_message if req.audio else ""
        }
    except Exception as exc:  # broad catch to avoid leaking stack traces to child
        raise HTTPException(status_code=500, detail="Oops, something went wrong. Let’s try again!") from exc
