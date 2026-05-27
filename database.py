"""SQLite persistence for users and summaries."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from config import DATABASE_PATH, DATA_DIR


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                original_text TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                style TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_user(username: str, password_hash: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, datetime.utcnow().isoformat()),
        )
        return int(cursor.lastrowid)


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def save_summary(
    *,
    user_id: Optional[int],
    original_text: str,
    summary_text: str,
    style: str,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO summaries (user_id, original_text, summary_text, style, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                original_text,
                summary_text,
                style,
                datetime.utcnow().isoformat(),
            ),
        )
        return int(cursor.lastrowid)


def get_summaries_for_user(user_id: int, limit: int = 50) -> List[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, original_text, summary_text, style, timestamp
            FROM summaries
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()


def get_summary_by_id(summary_id: int, user_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, original_text, summary_text, style, timestamp
            FROM summaries
            WHERE id = ? AND user_id = ?
            """,
            (summary_id, user_id),
        ).fetchone()
