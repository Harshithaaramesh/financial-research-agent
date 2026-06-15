"""
report_store.py
---------------
SQLite persistence layer for reports and audit logging.

Tables
------
  reports(id, username, ticker, company, created_at, report_md)
  audit_log(id, username, action, ticker, company, timestamp, detail)

Audit actions tracked:
  login              — user authenticated
  report_generated   — pipeline completed successfully
  email_sent         — PDF emailed to an address
  report_deleted     — report removed from history
  comparison_run     — two-ticker comparison executed
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/reports.db")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ── Init ──────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL DEFAULT 'unknown',
                ticker      TEXT    NOT NULL,
                company     TEXT    NOT NULL,
                created_at  TEXT    NOT NULL,
                report_md   TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL,
                action      TEXT    NOT NULL,
                ticker      TEXT    DEFAULT '',
                company     TEXT    DEFAULT '',
                timestamp   TEXT    NOT NULL,
                detail      TEXT    DEFAULT ''
            )
        """)
        # Migrate existing reports table if username column is missing
        try:
            conn.execute("ALTER TABLE reports ADD COLUMN username TEXT NOT NULL DEFAULT 'unknown'")
        except Exception:
            pass   # column already exists
        conn.commit()


# ── Reports ───────────────────────────────────────────────────────────────────

def save_report(ticker: str, company: str, report_md: str, username: str = "unknown") -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with _get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO reports (username, ticker, company, created_at, report_md) VALUES (?,?,?,?,?)",
            (username, ticker.upper(), company, now, report_md),
        )
        conn.commit()
        return cursor.lastrowid


def get_reports_by_user(username: str) -> list[dict]:
    """All reports for one user, newest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE username=? ORDER BY id DESC", (username,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_reports() -> list[dict]:
    """All reports across all users (admin view), newest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_report_by_id(report_id: int) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    return dict(row) if row else None


def delete_report(report_id: int) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM reports WHERE id=?", (report_id,))
        conn.commit()


# ── Audit log ─────────────────────────────────────────────────────────────────

def log_action(
    username: str,
    action: str,
    ticker: str = "",
    company: str = "",
    detail: str = "",
) -> None:
    """
    Write one line to the audit log. Fire-and-forget — never raises.

    Actions: login | report_generated | email_sent | report_deleted | comparison_run
    """
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO audit_log (username, action, ticker, company, timestamp, detail) "
                "VALUES (?,?,?,?,?,?)",
                (username, action, ticker, company, now, detail),
            )
            conn.commit()
    except Exception:
        pass   # audit must never break the main flow


def get_audit_log(limit: int = 200) -> list[dict]:
    """Return the most recent audit entries (admin view)."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Stats (admin dashboard) ───────────────────────────────────────────────────

def get_stats() -> dict:
    """Quick summary numbers for the admin panel."""
    with _get_conn() as conn:
        total_reports  = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        unique_users   = conn.execute("SELECT COUNT(DISTINCT username) FROM reports").fetchone()[0]
        unique_tickers = conn.execute("SELECT COUNT(DISTINCT ticker) FROM reports").fetchone()[0]
        total_logins   = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action='login'"
        ).fetchone()[0]
    return {
        "total_reports":  total_reports,
        "unique_users":   unique_users,
        "unique_tickers": unique_tickers,
        "total_logins":   total_logins,
    }
