from __future__ import annotations

"""FastAPI entry‑point for Kiddy backend.

* Adds permissive CORS **only** in development (env var `DEV_MODE=1`).
* Includes /v1 routes plus a simple `/health` GET for liveness checks.
* Reads `Settings` on startup to fail fast if env keys are missing.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import chat  # noqa: F401 – imported for router side‑effects
from app.core.settings import get_settings

settings = get_settings()  # Validate env immediately on import

app = FastAPI(
    title="Kiddy Backend (Stateless, COPPA‑safe)",
    version="0.1.0",
    contact={"name": "Kiddy Dev Team", "url": "https://example.com"},
    docs_url="/docs" if os.getenv("DEV_MODE") else None,
    redoc_url=None,
)

# ---------------------------------------------------------------------------
# CORS – open in dev; tighten / remove in prod.
# ---------------------------------------------------------------------------
if os.getenv("DEV_MODE"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------
app.include_router(chat.router)

# ---------------------------------------------------------------------------
# Static files (for demo)
# ---------------------------------------------------------------------------
if os.getenv("DEV_MODE"):
    try:
        app.mount("/public", StaticFiles(directory="public"), name="public")
    except Exception:
        pass  # Directory might not exist


# ---------------------------------------------------------------------------
# Health & Root endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
async def health():  # noqa: D401
    """Simple liveness probe for container orchestration."""
    return {"status": "ok"}


@app.get("/", tags=["meta"])
async def root():  # noqa: D401
    """Root endpoint returns basic info (no child content)."""
    return {
        "name": app.title,
        "version": app.version,
        "docs": "/docs" if os.getenv("DEV_MODE") else None,
    }
