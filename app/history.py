"""
Chat history and long-term memory module.

Provides a SQLite-backed store for:
1. Per-session conversation messages (for short-term context).
2. Permanent "facts" learned about the user (for long-term memory
   that persists across sessions).
"""

import sqlite3
import os
from app.config import SQLITE_DB_PATH


class ChatHistory:
    """Handles persistence of chat messages and user facts using SQLite."""

    def __init__(self):
        self.db_path = SQLITE_DB_PATH
        # Ensure the storage directory exists before SQLite tries to create the DB file.
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create the required tables if they don't already exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Stores every chat message (user + assistant) per session.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Stores permanent facts about the user, deduplicated via UNIQUE constraint.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT NOT NULL UNIQUE
            )
        """)

        conn.commit()
        conn.close()

    def add_message(self, session_id: str, role: str, content: str):
        """
        Save a single chat message to the database.

        Args:
            session_id: Unique identifier for the chat session.
            role: Either "user" or "assistant".
            content: The text content of the message.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()

    def get_history(self, session_id: str, limit: int = 20):
        """
        Retrieve the most recent messages for a given session, in chronological order.

        Args:
            session_id: Unique identifier for the chat session.
            limit: Maximum number of most recent messages to fetch.

        Returns:
            A list of dicts: [{"role": ..., "content": ...}, ...] oldest to newest.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Fetch newest messages first (DESC) so LIMIT correctly caps to the
        # most recent N, then reverse below to restore chronological order.
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        rows.reverse()
        return [{"role": r, "content": c} for r, c in rows]

    def list_sessions(self):
        """Return all distinct session IDs, ordered by most recently active first."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT session_id FROM messages GROUP BY session_id ORDER BY MAX(timestamp) DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def add_fact(self, fact: str):
        """
        Store a permanent fact about the user (persists across all future chats).

        Uses INSERT OR IGNORE so duplicate facts are silently skipped
        thanks to the UNIQUE constraint on the `fact` column.

        Args:
            fact: A short sentence describing something learned about the user.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO memory_facts (fact) VALUES (?)",
            (fact,)
        )
        conn.commit()
        conn.close()

    def get_all_facts(self):
        """Return every permanently stored fact about the user, across all sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT fact FROM memory_facts")
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]


# Singleton instance so all modules share the same DB connection settings.
chat_history = ChatHistory()