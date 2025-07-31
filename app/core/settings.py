import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Centralised environment configuration.

    Notes
    -----
    * **Stateless** – no sensitive data other than API keys is loaded; nothing else is persisted.
    * Uses `.env` so keys never get committed to VCS.  In production, rely on *real* env vars
      (`export GOOGLE_API_KEY=...`).
    * If the `GOOGLE_APPLICATION_CREDENTIALS` env var is **not** set, we raise instantly instead of
      failing deep in a request‑handler.
    """

    # === Google Generative AI ===
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")

    # === Google Cloud client libraries (Text‑to‑Speech, Natural Language) ===
    gcp_credentials_json: Path = Field(..., env="GOOGLE_APPLICATION_CREDENTIALS")
    google_tts_voice: str = Field("en-US-Standard-F", env="GOOGLE_TTS_VOICE")
    google_tts_project: str | None = Field(None, env="GOOGLE_TTS_PROJECT")

    # === Local‑only memory controls ===
    max_tokens_per_day: int = Field(4096, env="MAX_TOKENS_PER_DAY")
    log_retention_days: int = Field(3, env="LOG_RETENTION_DAYS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file

    # --- custom validators -------------------------------------------------
    @classmethod
    def validate_environment(cls, values):  # pylint: disable=no-self-argument
        cred_path: Path = values.get("gcp_credentials_json")
        if not cred_path.exists():
            raise FileNotFoundError(
                "GOOGLE_APPLICATION_CREDENTIALS does not point to a valid file."
            )
        return values


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton loader so every import shares the same validated settings object."""

    try:
        # Try to create settings with explicit values from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if api_key and creds_path:
            # We have the required environment variables
            return Settings(
                google_api_key=api_key,
                gcp_credentials_json=Path(creds_path),
                google_tts_voice=os.getenv("GOOGLE_TTS_VOICE", "en-US-Standard-F"),
                google_tts_project=os.getenv("GOOGLE_TTS_PROJECT"),
                max_tokens_per_day=int(os.getenv("MAX_TOKENS_PER_DAY", "4096")),
                log_retention_days=int(os.getenv("LOG_RETENTION_DAYS", "3"))
            )
        else:
            raise ValueError("Missing required environment variables")
            
    except Exception as e:
        # In development mode, allow missing env vars
        if os.getenv("DEV_MODE"):
            print(f"⚠️  Warning: Settings validation failed: {e}")
            print("   Set environment variables to enable full functionality.")
            # Return a minimal settings object for development
            return Settings(
                google_api_key=os.getenv("GOOGLE_API_KEY", "dev-key"),
                gcp_credentials_json=Path("dev-credentials.json"),
                google_tts_voice="en-US-Standard-F",
                max_tokens_per_day=4096,
                log_retention_days=3
            )
        else:
            raise
