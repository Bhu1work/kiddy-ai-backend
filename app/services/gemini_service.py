from __future__ import annotations

"""Service wrapper that calls Google Gemini 1.5 Pro.

Key changes (2025‑07‑30):
* Removed the import of `Content` from `google.generativeai.types` – that
  symbol was renamed in the 0.4.x client release and causes
  `ModuleNotFoundError` on Windows.  Instead we simply type the messages list
  as `list[dict]` which is perfectly fine for runtime and static checkers.
"""

import re
from typing import Final, List, Dict, Any

from app.core.constants import SYSTEM_PROMPT
from app.core.guardrails import sanitize, within_daily_budget, gemini_model

# ---------------------------------------------------------------------------
# Helpers -------------------------------------------------------------------
# ---------------------------------------------------------------------------

_LINE_RE: Final = re.compile(r"[\r\n]+")
_MAX_LINES: Final = 3


def _truncate_to_lines(text: str, max_lines: int = _MAX_LINES) -> str:  # noqa: D401
    """Ensure the assistant reply is ≤ `max_lines` by line‑breaks."""
    lines = _LINE_RE.split(text.strip())
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return "\n".join(lines).strip()


async def get_reply(session_id: str, user_text: str, buddy_name: str = "Buddy", kid_age: int = 7, kid_emotion: str = "neutral") -> str:
    """Generate a kid‑safe reply using Gemini.

    Steps:
    * Sanitize input (PII redaction).
    * Enforce per‑day token bucket.
    * Inject custom buddy name, age, and emotion into system prompt.
    * Truncate output to ≤ 3 lines.
    """

    if not within_daily_budget(session_id, user_text):
        return "We have chatted a lot today! Let's take a play break and talk again tomorrow."

    clean_text = sanitize(user_text)
    
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
        emotion_context = "\nThe child seems happy! Match their positive energy."
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

    return _truncate_to_lines(raw_text)
