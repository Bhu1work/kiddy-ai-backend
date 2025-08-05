from __future__ import annotations

"""Google Cloud Text‑to‑Speech wrapper.

* Accepts text + emotion tag and returns base‑64 MP3.
* No text or audio is persisted; the binary is streamed back and then GC’d.
* Uses SSML tweaks to add subtle emotional prosody.  Google’s standard voices
  don’t expose an explicit "emotion" feature, so we approximate with emphasis,
  rate, and pitch.
"""

import base64
from typing import Final

from google.cloud import texttospeech_v1 as tts

from app.core.settings import get_settings
from app.core.constants import ALLOWED_EMOTIONS

settings = get_settings()

# ---------------------------------------------------------------------------
# Lazy-load GCP client to avoid import-time credential errors
# ---------------------------------------------------------------------------
_client = None

def _get_client():
    """Get or create the TTS client."""
    global _client
    if _client is None:
        # Explicitly set the credentials path
        import os
        from google.oauth2 import service_account
        
        # Get the credentials path from environment
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/dev-credentials.json")
        
        # Ensure we're using the correct path inside the container
        if not os.path.exists(creds_path):
            # Try alternative paths
            alt_paths = ["/app/dev-credentials.json", "./kiddy-service.json", "kiddy-service.json"]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    creds_path = alt_path
                    break
        
        # Create credentials from the service account file
        credentials = service_account.Credentials.from_service_account_file(creds_path)
        
        # Create client with explicit credentials
        _client = tts.TextToSpeechClient(credentials=credentials)
    return _client

# Precompile SSML templates for speed
_SSML_TEMPLATES: Final[dict[str, str]] = {
    "excited": (
        "<speak><emphasis level='strong'><prosody pitch='+2st' rate='fast'>{text}</prosody></emphasis></speak>"
    ),
    "friendly": (
        "<speak><prosody pitch='+1st' rate='medium'>{text}</prosody></speak>"
    ),
    "caring": (
        "<speak><prosody rate='slow' pitch='-1st'>{text}</prosody></speak>"
    ),
    # Fallback templates for old emotions
    "cheerful": (
        "<speak><emphasis level='moderate'>{text}</emphasis></speak>"
    ),
    "curious": (
        "<speak><prosody pitch='+2st'>{text}</prosody></speak>"
    ),
    "affectionate": (
        "<speak><prosody rate='slow' pitch='-1st'>{text}</prosody></speak>"
    ),
}

def synthesize(text: str, emotion: str) -> str:
    """Return base‑64 MP3 for given text & emotion tag.

    Parameters
    ----------
    text : str
        The assistant reply (≤ ~300 chars recommended).
    emotion : str
        One of `ALLOWED_EMOTIONS`.
    """
    # Map emotion to a valid template
    if emotion not in _SSML_TEMPLATES:
        emotion = "friendly"  # Default to friendly

    try:
        ssml = _SSML_TEMPLATES[emotion].format(text=text)

        synthesis_input = tts.SynthesisInput(ssml=ssml)
        voice_params = tts.VoiceSelectionParams(
            language_code="en-US",
            name=settings.google_tts_voice,
        )
        audio_cfg = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

        client = _get_client()
        response = client.synthesize_speech(
            request={
                "input": synthesis_input,
                "voice": voice_params,
                "audio_config": audio_cfg,
            }
        )
        return base64.b64encode(response.audio_content).decode()
    except Exception as e:
        print(f"TTS Error: {e}")
        # Fallback: return empty audio if TTS fails
        return ""


__all__ = ["synthesize"]