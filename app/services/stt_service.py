from __future__ import annotations

"""Speech-to-Text service using Google Cloud Speech API.

This service converts audio input (base64 encoded) to text for kid's voice messages.
Optimized for children's speech patterns and common phrases.
"""

import base64
from typing import Optional
from google.cloud import speech_v1 as speech

# Lazy-load the client to avoid import-time credential errors
_stt_client = None

def _get_client():
    """Get or create the speech-to-text client."""
    global _stt_client
    if _stt_client is None:
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
        _stt_client = speech.SpeechClient(credentials=credentials)
    return _stt_client

def transcribe_audio(audio_b64: str, language_code: str = "en-US") -> Optional[str]:
    """Convert base64 audio to text.
    
    Args:
        audio_b64: Base64 encoded audio data
        language_code: Language code (default: en-US for US English)
    
    Returns:
        Transcribed text or None if transcription fails
    """
    
    try:
        print(f"Starting transcription for {len(audio_b64)} base64 chars")
        
        # Decode base64 audio
        audio_data = base64.b64decode(audio_b64)
        print(f"Decoded audio: {len(audio_data)} bytes")
        
        # Configure audio recognition
        audio = speech.RecognitionAudio(content=audio_data)
        
        # Try different encodings for better compatibility
        encodings_to_try = [
            speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            speech.RecognitionConfig.AudioEncoding.LINEAR16,
            speech.RecognitionConfig.AudioEncoding.FLAC,
        ]
        
        for encoding in encodings_to_try:
            try:
                print(f"Trying encoding: {encoding}")
                
                # Configure recognition settings optimized for children
                config = speech.RecognitionConfig(
                    encoding=encoding,
                    sample_rate_hertz=48000,  # Common sample rate for web audio
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                    enable_word_time_offsets=False,
                    enable_word_confidence=True,
                    # Add alternative encodings for better compatibility
                    alternative_language_codes=["en-US"],
                    # Optimize for children's speech patterns
                    speech_contexts=[speech.SpeechContext(
                        phrases=[
                            # Common kid phrases
                            "hello", "hi", "bye", "goodbye", "thank you", "please",
                            "what", "why", "how", "when", "where", "who",
                            "yes", "no", "maybe", "okay", "sure", "cool",
                            "awesome", "amazing", "wow", "fun", "happy", "sad",
                            "tired", "hungry", "thirsty", "scared", "excited",
                            "story", "joke", "game", "play", "sing", "dance",
                            "draw", "color", "paint", "read", "write", "learn",
                            "school", "home", "family", "friend", "mom", "dad",
                            "brother", "sister", "pet", "dog", "cat", "bird",
                            "toy", "ball", "book", "food", "water", "sleep"
                        ],
                        boost=10.0  # Boost these phrases for better recognition
                    )]
                )
        
                print("Calling Google Speech API...")
                # Perform transcription
                client = _get_client()
                response = client.recognize(config=config, audio=audio)
                print(f"API response received: {len(response.results)} results")
                
                # Extract the best transcription
                if response.results:
                    # Get the most confident result
                    best_result = max(response.results, key=lambda r: r.alternatives[0].confidence if r.alternatives else 0)
                    if best_result.alternatives:
                        transcribed_text = best_result.alternatives[0].transcript.strip()
                        confidence = best_result.alternatives[0].confidence
                        print(f"Best transcription: '{transcribed_text}' (confidence: {confidence:.2f})")
                        
                        # Basic validation - ensure we got meaningful text
                        if len(transcribed_text) > 0:
                            return transcribed_text
                        else:
                            print("Transcription is empty")
                    else:
                        print("No alternatives in best result")
                else:
                    print("No results from speech API")
                    
            except Exception as e:
                print(f"Failed with encoding {encoding}: {e}")
                continue
        
        print("All encodings failed")
        return None
        
    except Exception as e:
        print(f"Speech-to-text error: {e}")
        return None


def is_audio_valid(audio_b64: str) -> bool:
    """Validate that the audio data is properly formatted."""
    try:
        # Try to decode base64
        audio_data = base64.b64decode(audio_b64)
        
        print(f"Audio validation: {len(audio_data)} bytes")
        
        # Check if we have some reasonable amount of data
        if len(audio_data) < 100:  # Too small
            print(f"Audio too small: {len(audio_data)} bytes")
            return False
        if len(audio_data) > 10 * 1024 * 1024:  # Too large (>10MB)
            print(f"Audio too large: {len(audio_data)} bytes")
            return False
            
        print(f"Audio validation passed: {len(audio_data)} bytes")
        return True
        
    except Exception as e:
        print(f"Audio validation error: {e}")
        return False


__all__ = ["transcribe_audio", "is_audio_valid"] 