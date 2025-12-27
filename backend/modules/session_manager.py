"""
Session Manager Module for Friday Agent
Handles chat session persistence using SQLite
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, db_path: str = "chat_sessions.db"):
        """Initialize session manager with SQLite database"""
        self.db_path = db_path
        self._init_database()
        logger.info(f"Session manager initialized with database: {db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database tables initialized")
    
    def create_session(self, name: Optional[str] = None) -> Dict:
        """Create a new chat session"""
        import uuid
        
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        if not name:
            name = f"Chat {datetime.now().strftime('%b %d, %I:%M %p')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (id, name, created_at, updated_at, message_count)
            VALUES (?, ?, ?, ?, 0)
        """, (session_id, name, now, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created session: {session_id} - {name}")
        
        return {
            "id": session_id,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "message_count": 0
        }
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, created_at, updated_at, message_count
            FROM sessions
            WHERE id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"]
            }
        return None
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions ordered by updated_at"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, created_at, updated_at, message_count
            FROM sessions
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"]
            }
            for row in rows
        ]
    
    def update_session_name(self, session_id: str, name: str) -> bool:
        """Update session name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions
            SET name = ?, updated_at = ?
            WHERE id = ?
        """, (name, datetime.now().isoformat(), session_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Updated session {session_id} name to: {name}")
        
        return success
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        # Delete session
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Deleted session: {session_id}")
        
        return success
    
    def add_message(self, session_id: str, message_type: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Add a message to a session"""
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert message
        cursor.execute("""
            INSERT INTO messages (session_id, type, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, message_type, content, now, json.dumps(metadata) if metadata else None))
        
        message_id = cursor.lastrowid
        
        # Update session
        cursor.execute("""
            UPDATE sessions
            SET updated_at = ?, message_count = message_count + 1
            WHERE id = ?
        """, (now, session_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Added {message_type} message to session {session_id}")
        
        return {
            "id": message_id,
            "session_id": session_id,
            "type": message_type,
            "content": content,
            "timestamp": now,
            "metadata": metadata
        }
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get all messages for a session"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT id, session_id, type, content, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "type": row["type"],
                "content": row["content"],
                "timestamp": row["timestamp"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else None
            }
            for row in rows
        ]
    
    def clear_old_sessions(self, days: int = 30) -> int:
        """Delete sessions older than specified days"""
        from datetime import timedelta
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get sessions to delete
        cursor.execute("""
            SELECT id FROM sessions
            WHERE updated_at < ?
        """, (cutoff_date,))
        
        session_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete messages
        for session_id in session_ids:
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        # Delete sessions
        cursor.execute("DELETE FROM sessions WHERE updated_at < ?", (cutoff_date,))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {count} old sessions (older than {days} days)")
        
        return count
