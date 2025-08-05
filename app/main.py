from __future__ import annotations

"""FastAPI entry‑point for Kiddy backend.

* Adds permissive CORS **only** in development (env var `DEV_MODE=1`).
* Includes /v1 routes plus a simple `/health` GET for liveness checks.
* Reads `Settings` on startup to fail fast if env keys are missing.
"""

import os
import sys
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import chat  # noqa: F401 – imported for router side‑effects
from app.core.settings import get_settings

settings = get_settings()  # Validate env immediately on import

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------

import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Logging Middleware
# ---------------------------------------------------------------------------

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        logger.info(
            f"HTTP Request: {request.method} {request.url} from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"HTTP Response: {request.method} {request.url} -> {response.status_code}"
        )
        
        return response

app = FastAPI(
    title="Kiddy Backend (Stateless, COPPA‑safe)",
    version="0.1.0",
    contact={"name": "Kiddy Dev Team", "url": "https://example.com"},
    docs_url="/docs" if os.getenv("DEV_MODE") else None,
    redoc_url=None,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------

if os.getenv("DEV_MODE") == "1":
    # CORS – open in dev; tighten / remove in prod.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---------------------------------------------------------------------------
# Static Files
# ---------------------------------------------------------------------------

# Serve static files from public directory
app.mount("/public", StaticFiles(directory="public"), name="public")

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------

app.include_router(chat.router)

# ---------------------------------------------------------------------------
# Startup and Shutdown Events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Log startup and validate configuration."""
    logger.info("Starting Kiddy Backend...")
    logger.info(f"Environment: {'Development' if os.getenv('DEV_MODE') else 'Production'}")
    logger.info(f"API Key configured: {'Yes' if settings.google_api_key else 'No'}")
    logger.info(f"Credentials path: {settings.gcp_credentials_json}")

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown."""
    logger.info("Shutting down Kiddy Backend...")

# ---------------------------------------------------------------------------
# Health Check Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
async def health():  # noqa: D401
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "kiddy-backend"
    }

@app.get("/", tags=["meta"])
async def root():  # noqa: D401
    """Root endpoint with basic service information."""
    return {
        "name": "Kiddy Backend",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs" if os.getenv("DEV_MODE") else None
    }

@app.get("/conversation-demo.html", tags=["demo"])
async def conversation_demo():
    """Serve the conversation demo HTML file."""
    try:
        with open("public/conversation-demo.html", "r", encoding="utf-8") as f:
            content = f.read()
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=content)
    except FileNotFoundError:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Demo file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
