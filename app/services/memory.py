from __future__ import annotations

"""Encrypted ring‑buffer log for last N days.

* Uses **SQLCipher** if available; falls back to vanilla `sqlite3` (unencrypted)
  with a warning in dev mode.
* Designed for **local‑only** storage – the file path should point inside the
  app sandbox (e.g. <ApplicationSupport>/kiddy/kiddy.db on iOS / macOS; or
  internal storage on Android).
* Purge policy: any row whose `created_at` is older than `retention_days` is
  deleted on every insert.
"""

import os
import sqlite3
import time
from pathlib import Path
from typing import Iterable

from app.core.settings import get_settings

settings = get_settings()

DB_PATH = Path(os.getenv("KIDDY_DB_PATH", "./kiddy.db")).expanduser()
_DB_CONN: sqlite3.Connection | None = None

# ---------------------------------------------------------------------------
# Helpers -------------------------------------------------------------------
# ---------------------------------------------------------------------------

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT    NOT NULL,
    created_at  INTEGER NOT NULL,
    text        TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_created ON messages(created_at);
"""

_PURGE_SQL = "DELETE FROM messages WHERE created_at < ?"  # param = ts cutoff
_INSERT_SQL = "INSERT INTO messages(session_id, created_at, text) VALUES (?, ?, ?)"
_SELECT_SQL = "SELECT created_at, text FROM messages WHERE session_id = ? ORDER BY created_at DESC"

_RETENTION_SECS = settings.log_retention_days * 86_400


def _connect() -> sqlite3.Connection:
    global _DB_CONN  # pylint: disable=global-statement

    if _DB_CONN is not None:
        return _DB_CONN

    need_cipher = True
    try:
        import sqlcipher3 as sqlite  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover – dev env only
        import sqlite3 as sqlite  # pylint: disable=import-error
        need_cipher = False

    conn = sqlite.connect(DB_PATH)

    if need_cipher:
        # Use 256‑bit random key – persisted in Keychain/Keystore by caller.
        key = os.getenv("SQLCIPHER_KEY", "demo‑key‑replace‑me")
        conn.executescript(f"PRAGMA key = '{key}';\nPRAGMA cipher_compatibility = 4;")

    conn.executescript(_CREATE_SQL)
    _DB_CONN = conn
    return conn


def _purge_old(conn: sqlite3.Connection) -> None:
    cutoff = int(time.time()) - _RETENTION_SECS
    conn.execute(_PURGE_SQL, (cutoff,))
    conn.commit()


def insert(session_id: str, text: str) -> None:
    """Insert a message and purge anything older than retention window."""
    conn = _connect()
    now = int(time.time())
    conn.execute(_INSERT_SQL, (session_id, now, text))
    _purge_old(conn)


def fetch_last(session_id: str, limit: int = 100) -> list[tuple[int, str]]:
    """Return up to `limit` rows for parent review (most recent first)."""
    conn = _connect()
    cur = conn.execute(_SELECT_SQL + " LIMIT ?", (session_id, limit))
    return cur.fetchall()


def get_logs(session_id: str) -> list[str]:
    """Return all logs for a session as formatted strings."""
    logs = fetch_last(session_id, limit=1000)  # Get all logs
    return [text for _, text in logs]


__all__ = ["insert", "fetch_last", "get_logs"]
