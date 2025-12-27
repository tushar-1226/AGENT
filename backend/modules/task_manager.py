"""
AI-powered task management with natural language parsing
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid
import re

class TaskManager:
    def __init__(self, db_path: str = 'tasks.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize tasks database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                category TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def parse_natural_language(self, text: str, gemini_processor=None) -> Dict[str, Any]:
        """Parse natural language task input"""
        task_data = {
            'title': text,
            'description': '',
            'priority': 'medium',
            'due_date': None,
            'category': 'general'
        }
        
        # Extract priority
        if any(word in text.lower() for word in ['urgent', 'asap', 'critical', 'important']):
            task_data['priority'] = 'high'
        elif any(word in text.lower() for word in ['low priority', 'whenever', 'someday']):
            task_data['priority'] = 'low'
        
        # Extract due date keywords
        today = datetime.now()
        if 'today' in text.lower():
            task_data['due_date'] = today.isoformat()
        elif 'tomorrow' in text.lower():
            task_data['due_date'] = (today + timedelta(days=1)).isoformat()
        elif 'next week' in text.lower():
            task_data['due_date'] = (today + timedelta(days=7)).isoformat()
        elif 'next month' in text.lower():
            task_data['due_date'] = (today + timedelta(days=30)).isoformat()
        
        # Extract date patterns (e.g., "on Friday", "by Monday", "Dec 25")
        # Simple regex for dates
        date_pattern = r'(on|by|before)\s+(\w+\s+\d{1,2}|\w+)'
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        if date_match and not task_data['due_date']:
            # For now, default to 7 days from now if we can't parse precisely
            task_data['due_date'] = (today + timedelta(days=7)).isoformat()
        
        # Extract category
        categories = {
            'work': ['work', 'meeting', 'project', 'deadline'],
            'personal': ['personal', 'buy', 'call', 'email'],
            'coding': ['code', 'bug', 'feature', 'deploy', 'fix'],
            'learning': ['learn', 'study', 'read', 'course']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text.lower() for keyword in keywords):
                task_data['category'] = category
                break
        
        # Clean up title (remove date/priority keywords)
        title = text
        for word in ['urgent', 'asap', 'today', 'tomorrow', 'next week', 'next month']:
            title = re.sub(rf'\b{word}\b', '', title, flags=re.IGNORECASE)
        task_data['title'] = ' '.join(title.split()).strip()
        
        return task_data
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO tasks (id, title, description, priority, status, due_date, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            task_data.get('title', ''),
            task_data.get('description', ''),
            task_data.get('priority', 'medium'),
            'pending',
            task_data.get('due_date'),
            task_data.get('category', 'general'),
            now,
            now
        ))
        conn.commit()
        conn.close()
        
        return self.get_task(task_id)
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a single task by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_tasks(self, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        cursor = conn.execute(query, params)
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task"""
        conn = sqlite3.connect(self.db_path)
        
        # Build update query
        allowed_fields = ['title', 'description', 'priority', 'status', 'due_date', 'category']
        update_fields = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = ?")
                values.append(updates[field])
        
        if not update_fields:
            conn.close()
            return self.get_task(task_id)
        
        # Add updated_at
        update_fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        
        # Add completed_at if status changed to done
        if updates.get('status') == 'done':
            update_fields.append("completed_at = ?")
            values.append(datetime.now().isoformat())
        
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()
        
        return self.get_task(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        stats = {
            'total': 0,
            'pending': 0,
            'in_progress': 0,
            'done': 0,
            'overdue': 0,
            'by_category': {},
            'by_priority': {}
        }
        
        # Get all tasks
        cursor = conn.execute("SELECT * FROM tasks")
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        stats['total'] = len(tasks)
        now = datetime.now()
        
        for task in tasks:
            # Count by status
            status = task['status']
            if status in stats:
                stats[status] += 1
            
            # Count overdue
            if task['due_date'] and task['status'] != 'done':
                due_date = datetime.fromisoformat(task['due_date'])
                if due_date < now:
                    stats['overdue'] += 1
            
            # Count by category
            category = task['category'] or 'general'
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # Count by priority
            priority = task['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return stats
