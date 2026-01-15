import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthManager:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the SQLite database with users table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

    def register_user(self, email: str, password: str, name: str) -> Dict:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Email already registered"}

            # Insert new user
            password_hash = self._hash_password(password)
            cursor.execute(
                'INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)',
                (email, name, password_hash)
            )
            user_id = cursor.lastrowid

            # Create session token
            token = self._generate_token()
            expires_at = datetime.now() + timedelta(days=30)
            cursor.execute(
                'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user_id, token, expires_at)
            )

            conn.commit()
            conn.close()

            return {
                "success": True,
                "user": {"id": user_id, "email": email, "name": name},
                "token": token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def login_user(self, email: str, password: str) -> Dict:
        """Login user and create session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get user
            password_hash = self._hash_password(password)
            cursor.execute(
                'SELECT id, email, name FROM users WHERE email = ? AND password_hash = ?',
                (email, password_hash)
            )
            user = cursor.fetchone()

            if not user:
                conn.close()
                return {"success": False, "error": "Invalid email or password"}

            user_id, user_email, user_name = user

            # Create session token
            token = self._generate_token()
            expires_at = datetime.now() + timedelta(days=30)
            cursor.execute(
                'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user_id, token, expires_at)
            )

            conn.commit()
            conn.close()

            return {
                "success": True,
                "user": {"id": user_id, "email": user_email, "name": user_name},
                "token": token
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify session token and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT u.id, u.email, u.name
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.token = ? AND s.expires_at > ?
            ''', (token, datetime.now()))

            user = cursor.fetchone()
            conn.close()

            if user:
                return {"id": user[0], "email": user[1], "name": user[2]}
            return None
        except Exception as e:
            return None

    def logout_user(self, token: str) -> bool:
        """Logout user by removing session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
