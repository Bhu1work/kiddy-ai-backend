from __future__ import annotations

"""Enhanced emotion detection for kid's input and AI responses.

We use Google Cloud Natural Language `analyze_sentiment` to classify both:
1. The kid's input message (to understand their emotional state)
2. The assistant's reply (for TTS emotion mapping)

This helps the AI respond appropriately to the child's emotional state.
"""

from google.cloud import language_v1 as lang
from app.core.constants import SENTIMENT_TO_EMOTION

# Lazy-load the client to avoid import-time credential errors
_nl_client = None

def _get_client():
    """Get or create the language client."""
    global _nl_client
    if _nl_client is None:
        _nl_client = lang.LanguageServiceClient()
    return _nl_client

# Boundaries tuned so that neutral window is ±0.25, matching Google doc advice.
_POS_THRESH = 0.25
_NEG_THRESH = -0.25


def detect_emotion(text: str) -> str:
    """Return one of {cheerful, curious, affectionate} for given assistant text."""

    try:
        # Build document object – plain text
        client = _get_client()
        document = lang.Document(content=text, type_=lang.Document.Type.PLAIN_TEXT)
        response = client.analyze_sentiment(document=document)
        score = response.document_sentiment.score

        if score >= _POS_THRESH:
            return SENTIMENT_TO_EMOTION["positive"]
        if score <= _NEG_THRESH:
            return SENTIMENT_TO_EMOTION["negative"]
        return SENTIMENT_TO_EMOTION["neutral"]
    except Exception:
        # Fallback to neutral if sentiment analysis fails
        return SENTIMENT_TO_EMOTION["neutral"]


def detect_kid_emotion(text: str) -> str:
    """Analyze kid's input to understand their emotional state."""
    
    try:
        client = _get_client()
        document = lang.Document(content=text, type_=lang.Document.Type.PLAIN_TEXT)
        response = client.analyze_sentiment(document=document)
        score = response.document_sentiment.score
        
        # Map kid's emotion to appropriate response style
        if score >= _POS_THRESH:
            return "happy"  # Kid is happy → match their energy
        elif score <= _NEG_THRESH:
            return "sad"    # Kid is sad → be comforting
        else:
            return "neutral"  # Kid is neutral → be curious/engaging
            
    except Exception:
        return "neutral"


def get_emotional_response_style(kid_emotion: str) -> str:
    """Determine how the AI should respond based on kid's emotion."""
    
    emotion_style_map = {
        "happy": "cheerful",      # Match their happiness
        "sad": "affectionate",    # Be comforting and warm
        "neutral": "curious",     # Be engaging and curious
    }
    
    return emotion_style_map.get(kid_emotion, "curious")


__all__ = ["detect_emotion", "detect_kid_emotion", "get_emotional_response_style"]
