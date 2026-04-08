"""
database.py — SQLite connection, table creation, and query helpers
All pages and services use these helpers — no direct DB access elsewhere.
"""

import sqlite3
import json
import os
from datetime import datetime
from config import DATABASE_PATH


def get_db():
    """Return a new SQLite connection with row_factory for dict-like access."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create all tables on first run. Safe to call multiple times."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS analyses (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                slug                 TEXT UNIQUE NOT NULL,
                repo_url             TEXT,
                repo_name            TEXT,
                input_mode           TEXT DEFAULT 'url',
                raw_commits_json     TEXT,
                grouped_commits_json TEXT,
                narrative_release    TEXT,
                narrative_standup    TEXT,
                narrative_onboarding TEXT,
                narrative_portfolio  TEXT,
                commit_count         INTEGER DEFAULT 0,
                status               TEXT DEFAULT 'pending',
                error_message        TEXT,
                created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_analyses_slug ON analyses(slug);
            CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);
        """)


# ─── CRUD Helpers ─────────────────────────────────────────────────────────────

def save_analysis(slug, repo_url, repo_name, input_mode, raw_commits, grouped_commits, commit_count):
    """Insert a new analysis record. Returns the new row id."""
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO analyses
               (slug, repo_url, repo_name, input_mode, raw_commits_json,
                grouped_commits_json, commit_count, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (
                slug,
                repo_url,
                repo_name,
                input_mode,
                json.dumps(raw_commits, default=str),
                json.dumps(grouped_commits, default=str),
                commit_count,
            ),
        )
        return cursor.lastrowid


def update_narratives(analysis_id, narratives: dict):
    """Store generated narratives dict {release, standup, onboarding, portfolio}."""
    with get_db() as conn:
        conn.execute(
            """UPDATE analyses SET
                narrative_release    = ?,
                narrative_standup    = ?,
                narrative_onboarding = ?,
                narrative_portfolio  = ?,
                status               = 'done'
               WHERE id = ?""",
            (
                narratives.get("release", ""),
                narratives.get("standup", ""),
                narratives.get("onboarding", ""),
                narratives.get("portfolio", ""),
                analysis_id,
            ),
        )


def set_error(analysis_id, message):
    """Mark an analysis as errored."""
    with get_db() as conn:
        conn.execute(
            "UPDATE analyses SET status='error', error_message=? WHERE id=?",
            (message, analysis_id),
        )


def get_analysis_by_id(analysis_id):
    """Fetch one analysis by numeric id. Returns dict or None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
        return dict(row) if row else None


def get_analysis_by_slug(slug):
    """Fetch one analysis by shareable slug. Returns dict or None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE slug = ?", (slug,)
        ).fetchone()
        return dict(row) if row else None


def get_all_analyses(search="", page=1, per_page=12):
    """Paginated list of analyses, optional search by repo_name."""
    offset = (page - 1) * per_page
    with get_db() as conn:
        if search:
            pattern = f"%{search}%"
            rows = conn.execute(
                """SELECT * FROM analyses
                   WHERE repo_name LIKE ? OR repo_url LIKE ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (pattern, pattern, per_page, offset),
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM analyses WHERE repo_name LIKE ? OR repo_url LIKE ?",
                (pattern, pattern),
            ).fetchone()[0]
        else:
            rows = conn.execute(
                "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (per_page, offset),
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        return [dict(r) for r in rows], total
