import sqlite3
import os
from app.config import SQLITE_DB_PATH


class ChatHistory:
    def __init__(self):
        self.db_path = SQLITE_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_message(self, session_id: str, role: str, content: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()

    def get_history(self, session_id: str, limit: int = 20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r, "content": c} for r, c in rows]

    def list_sessions(self):
        """Return all distinct session IDs, most recent first."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT session_id FROM messages GROUP BY session_id ORDER BY MAX(timestamp) DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]


# Singleton instance
chat_history = ChatHistory()