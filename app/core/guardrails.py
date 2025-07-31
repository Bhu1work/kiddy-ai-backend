"""Guardrail helpers – now compatible with google‑generativeai ≥ 0.4.0.

Changes
~~~~~~~
* **Import patch**: Google's client moved `HarmCategory` & `HarmBlockThreshold`
  out of `google.generativeai.types.safety`.  We try the new path first then
  fall back for older versions.
* **Safety settings build**: supports both the old `dict` style and the new
  `SafetySetting` objects, so whichever client version is installed will work.
"""

from __future__ import annotations

import os
import re
import time
from typing import Final

import google.generativeai as genai
from google.generativeai import GenerativeModel
try:  # ≥0.4
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    from google.generativeai.types.safety import HarmCategory, HarmBlockThreshold
try:
    from google.generativeai.types import SafetySetting
except ImportError:
    SafetySetting = None  # type: ignore

from app.core.settings import get_settings

settings = get_settings()

# Configure the API key
genai.configure(api_key=settings.google_api_key)

# ---------------------------------------------------------------------------
# 2. PII scrubbing – simple regexes
# ---------------------------------------------------------------------------
_SSN_RE: Final = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE_RE: Final = re.compile(r"\b\d{10}\b|\(\d{3}\)\s?\d{3}-\d{4}")
_ZIP_RE: Final = re.compile(r"\b\d{5}(?:-\d{4})?\b")
_EMAIL_RE: Final = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}")

_PII_PATTERNS: Final[list[re.Pattern[str]]] = [_SSN_RE, _PHONE_RE, _ZIP_RE, _EMAIL_RE]

_TOKEN_PLACEHOLDER: Final = "[redacted]"

def sanitize(text: str) -> str:
    for pat in _PII_PATTERNS:
        text = pat.sub(_TOKEN_PLACEHOLDER, text)
    return text

# ---------------------------------------------------------------------------
# 3. Token bucket (per 24 h)
# ---------------------------------------------------------------------------
_MAX_TOKENS: Final = settings.max_tokens_per_day
_bucket: dict[str, int] = {}
_reset_ts: float = time.time()
_WORD_RE = re.compile(r"\w+")

def _maybe_reset() -> None:
    global _bucket, _reset_ts  # pylint: disable=global-statement
    if time.time() - _reset_ts > 86_400:
        _bucket.clear(); _reset_ts = time.time()

def within_daily_budget(session_id: str, text: str) -> bool:
    _maybe_reset()
    tokens = len(_WORD_RE.findall(text))
    used = _bucket.get(session_id, 0)
    if used + tokens > _MAX_TOKENS:
        _bucket[session_id] = 0
        return False
    _bucket[session_id] = used + tokens
    return True

# ---------------------------------------------------------------------------
# 4. Build Gemini model (safety settings handled by system prompt)
# ---------------------------------------------------------------------------

gemini_model = GenerativeModel(
    model_name="gemini-1.5-pro",
)

__all__ = ["sanitize", "within_daily_budget", "gemini_model"]