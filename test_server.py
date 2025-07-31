#!/usr/bin/env python3
"""Simple test server to verify basic functionality."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Set dev mode
os.environ["DEV_MODE"] = "1"

app = FastAPI(
    title="Kiddy Backend Test",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

# Add CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "Kiddy Backend is running!"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Kiddy Backend Test",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/test-guardrails")
async def test_guardrails():
    """Test guardrails functionality."""
    try:
        from app.core.guardrails import sanitize, within_daily_budget
        return {
            "status": "ok",
            "guardrails": "working",
            "pii_test": sanitize("Call 555-123-4567"),
            "token_test": within_daily_budget("test_session", "Hello world")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 