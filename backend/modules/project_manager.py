import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class ProjectManager:
    def __init__(self, db_path: str = "projects.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the SQLite database with projects table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                user_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_id INTEGER,
                message TEXT NOT NULL,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL
            )
        ''')

        conn.commit()
        conn.close()

    def create_project(self, name: str, description: str = "", user_id: int = None, metadata: dict = None) -> Dict:
        """Create a new project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            metadata_json = json.dumps(metadata) if metadata else "{}"

            cursor.execute(
                'INSERT INTO projects (name, description, user_id, metadata) VALUES (?, ?, ?, ?)',
                (name, description, user_id, metadata_json)
            )
            project_id = cursor.lastrowid

            conn.commit()
            conn.close()

            return {
                "success": True,
                "project": {
                    "id": project_id,
                    "name": name,
                    "description": description,
                    "user_id": user_id,
                    "metadata": metadata
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_projects(self, user_id: int = None) -> List[Dict]:
        """Get all projects for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if user_id:
                cursor.execute(
                    'SELECT id, name, description, metadata, created_at, updated_at FROM projects WHERE user_id = ? ORDER BY updated_at DESC',
                    (user_id,)
                )
            else:
                cursor.execute(
                    'SELECT id, name, description, metadata, created_at, updated_at FROM projects ORDER BY updated_at DESC'
                )

            projects = []
            for row in cursor.fetchall():
                projects.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {},
                    "created_at": row[4],
                    "updated_at": row[5]
                })

            conn.close()
            return projects
        except Exception as e:
            return []

    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get a specific project by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT id, name, description, user_id, metadata, created_at, updated_at FROM projects WHERE id = ?',
                (project_id,)
            )

            row = cursor.fetchone()
            if row:
                project = {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "user_id": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {},
                    "created_at": row[5],
                    "updated_at": row[6]
                }
                conn.close()
                return project

            conn.close()
            return None
        except Exception as e:
            return None

    def update_project(self, project_id: int, name: str = None, description: str = None, metadata: dict = None) -> bool:
        """Update a project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))

            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
                params.append(project_id)
                cursor.execute(query, params)
                conn.commit()

            conn.close()
            return True
        except Exception as e:
            return False

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    def add_chat_message(self, message: str, response: str = None, project_id: int = None, user_id: int = None) -> bool:
        """Add a chat message to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO chat_history (project_id, user_id, message, response) VALUES (?, ?, ?, ?)',
                (project_id, user_id, message, response)
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

    def get_chat_history(self, project_id: int = None, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Get chat history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = 'SELECT id, project_id, message, response, timestamp FROM chat_history WHERE 1=1'
            params = []

            if project_id:
                query += ' AND project_id = ?'
                params.append(project_id)
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)

            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)

            cursor.execute(query, params)

            history = []
            for row in cursor.fetchall():
                history.append({
                    "id": row[0],
                    "project_id": row[1],
                    "message": row[2],
                    "response": row[3],
                    "timestamp": row[4]
                })

            conn.close()
            return history
        except Exception as e:
            return []

    def search_chat_history(self, search_term: str, user_id: int = None, limit: int = 50) -> List[Dict]:
        """Search chat history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = '''
                SELECT id, project_id, message, response, timestamp
                FROM chat_history
                WHERE (message LIKE ? OR response LIKE ?)
            '''
            params = [f'%{search_term}%', f'%{search_term}%']

            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)

            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)

            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "project_id": row[1],
                    "message": row[2],
                    "response": row[3],
                    "timestamp": row[4]
                })

            conn.close()
            return results
        except Exception as e:
            return []
