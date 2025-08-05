from __future__ import annotations

"""Service wrapper that calls Google Gemini 1.5 Flash for faster responses.

Key changes (2025‑08‑05):
* Updated to use Gemini 1.5 Flash for faster responses
* Added welcome messages for better conversation start
* Optimized for faster input/output
* Improved system prompt for more human-like responses
"""

import re
import random
from typing import Final, List, Dict, Any

from app.core.constants import SYSTEM_PROMPT, WELCOME_MESSAGES
from app.core.guardrails import sanitize, within_daily_budget, gemini_model

# ---------------------------------------------------------------------------
# Helpers -------------------------------------------------------------------
# ---------------------------------------------------------------------------

_LINE_RE: Final = re.compile(r"[\r\n]+")
_MAX_LINES: Final = 2  # Reduced for faster responses
_EMOJI_RE: Final = re.compile(r'[^\w\s\.,!?;:()\-\'\"\n]')  # Remove emojis and special symbols


def _remove_emojis(text: str) -> str:
    """Remove emojis and special symbols from text to prevent TTS issues."""
    return _EMOJI_RE.sub('', text)


def _truncate_to_lines(text: str, max_lines: int = _MAX_LINES) -> str:  # noqa: D401
    """Ensure the assistant reply is ≤ `max_lines` by line‑breaks."""
    lines = _LINE_RE.split(text.strip())
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return "\n".join(lines).strip()


def get_welcome_message(buddy_name: str = "Buddy") -> str:
    """Get a random welcome message."""
    return random.choice(WELCOME_MESSAGES)


async def get_reply(session_id: str, user_text: str, buddy_name: str = "Buddy", kid_age: int = 7, kid_emotion: str = "neutral") -> str:
    """Generate a kid‑safe reply using Gemini 1.5 Pro for faster responses.

    Steps:
    * Sanitize input (PII redaction).
    * Enforce per‑day token bucket.
    * Inject custom buddy name, age, and emotion into system prompt.
    * Truncate output to ≤ 2 lines for faster conversation.
    """

    if not within_daily_budget(session_id, user_text):
        return "We've been chatting a lot! Let's take a break and talk again later!"

    clean_text = sanitize(user_text)
    
    try:
        # Enhanced system prompt with age and emotion context
        sys_prompt = SYSTEM_PROMPT.format(
            custom_name=buddy_name,
            kid_age=kid_age
        )
        
        # Add emotional context based on kid's state
        emotion_context = ""
        if kid_emotion == "sad":
            emotion_context = "\nThe child seems sad. Be extra comforting and warm in your response."
        elif kid_emotion == "happy":
            emotion_context = "\nThe child seems happy! Match their positive energy and be excited!"
        elif kid_emotion == "neutral":
            emotion_context = "\nThe child seems neutral. Be engaging and curious to draw them in."

        # For Gemini, we need to include the system prompt in the user message
        # since system roles are not supported in the same way
        user_message = f"{sys_prompt}{emotion_context}\n\nUser: {clean_text}"
        
        messages: List[Dict[str, Any]] = [
            {"role": "user", "parts": [user_message]},
        ]

        reply = gemini_model.generate_content(messages)
        raw_text: str = getattr(reply, "text", "")
        
        # Remove emojis and clean the text for TTS
        clean_reply = _remove_emojis(raw_text)
        
        return _truncate_to_lines(clean_reply)
    except Exception as e:
        # Fallback responses if model fails
        fallback_responses = [
            f"Hey {buddy_name} here! That's really interesting! Tell me more about that!",
            f"Wow, that's cool! I'm {buddy_name} and I'd love to hear more!",
            f"That's awesome! What else do you want to talk about?",
            f"I'm {buddy_name} and I think that's really neat! Want to tell me more?",
            f"That sounds fun! I'm curious to hear more about it!"
        ]
        return random.choice(fallback_responses)


async def get_welcome_reply(session_id: str, buddy_name: str = "Buddy", kid_age: int = 7) -> str:
    """Generate a natural welcome message."""
    return "Hey whatsup!!"
