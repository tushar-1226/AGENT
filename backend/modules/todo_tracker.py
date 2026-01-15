"""
TODO/FIXME/NOTE Tracker Module
Scans codebase for TODO, FIXME, HACK, NOTE, XXX comments
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class TODOTracker:
    # Patterns to detect different comment types
    PATTERNS = {
        'TODO': r'(?:\/\/|#|\/\*|\*|<!--)\s*TODO:?\s*(.+?)(?:\*\/|-->|$)',
        'FIXME': r'(?:\/\/|#|\/\*|\*|<!--)\s*FIXME:?\s*(.+?)(?:\*\/|-->|$)',
        'HACK': r'(?:\/\/|#|\/\*|\*|<!--)\s*HACK:?\s*(.+?)(?:\*\/|-->|$)',
        'NOTE': r'(?:\/\/|#|\/\*|\*|<!--)\s*NOTE:?\s*(.+?)(?:\*\/|-->|$)',
        'XXX': r'(?:\/\/|#|\/\*|\*|<!--)\s*XXX:?\s*(.+?)(?:\*\/|-->|$)',
        'BUG': r'(?:\/\/|#|\/\*|\*|<!--)\s*BUG:?\s*(.+?)(?:\*\/|-->|$)',
    }
    
    # File extensions to scan
    SUPPORTED_EXTENSIONS = {
        '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.h',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.vue',
        '.html', '.css', '.scss', '.sass', '.less'
    }
    
    # Directories to ignore
    IGNORE_DIRS = {
        'node_modules', 'venv', '.venv', 'dist', 'build', '.next',
        '__pycache__', '.git', '.idea', '.vscode', 'target', 'bin', 'obj'
    }
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.todos = []
    
    def scan(self) -> List[Dict]:
        """Scan entire project for TODOs"""
        self.todos = []
        self._scan_directory(self.root_path)
        return self.todos
    
    def _scan_directory(self, directory: Path):
        """Recursively scan directory"""
        try:
            for item in directory.iterdir():
                # Skip ignored directories
                if item.is_dir():
                    if item.name in self.IGNORE_DIRS:
                        continue
                    self._scan_directory(item)
                # Scan supported files
                elif item.is_file() and item.suffix in self.SUPPORTED_EXTENSIONS:
                    self._scan_file(item)
        except PermissionError:
            pass
    
    def _scan_file(self, file_path: Path):
        """Scan single file for TODOs"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for todo_type, pattern in self.PATTERNS.items():
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        todo_text = match.group(1).strip()
                        relative_path = str(file_path.relative_to(self.root_path))
                        
                        self.todos.append({
                            'type': todo_type,
                            'text': todo_text,
                            'file': relative_path,
                            'line': line_num,
                            'code_snippet': line.strip(),
                            'priority': self._get_priority(todo_type),
                            'created_at': datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
    
    def _get_priority(self, todo_type: str) -> str:
        """Assign priority based on TODO type"""
        priority_map = {
            'FIXME': 'high',
            'BUG': 'high',
            'HACK': 'high',
            'TODO': 'medium',
            'XXX': 'medium',
            'NOTE': 'low'
        }
        return priority_map.get(todo_type, 'medium')
    
    def get_stats(self) -> Dict:
        """Get statistics about TODOs"""
        stats = {
            'total': len(self.todos),
            'by_type': {},
            'by_priority': {},
            'by_file': {}
        }
        
        for todo in self.todos:
            # Count by type
            todo_type = todo['type']
            stats['by_type'][todo_type] = stats['by_type'].get(todo_type, 0) + 1
            
            # Count by priority
            priority = todo['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Count by file
            file_path = todo['file']
            stats['by_file'][file_path] = stats['by_file'].get(file_path, 0) + 1
        
        return stats
    
    def filter_by_priority(self, priority: str) -> List[Dict]:
        """Filter TODOs by priority"""
        return [todo for todo in self.todos if todo['priority'] == priority]
    
    def filter_by_type(self, todo_type: str) -> List[Dict]:
        """Filter TODOs by type"""
        return [todo for todo in self.todos if todo['type'].upper() == todo_type.upper()]
    
    def search(self, query: str) -> List[Dict]:
        """Search TODOs by text content"""
        query_lower = query.lower()
        return [
            todo for todo in self.todos 
            if query_lower in todo['text'].lower() or query_lower in todo['file'].lower()
        ]


if __name__ == '__main__':
    # Test the tracker
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = '.'
    
    tracker = TODOTracker(project_path)
    todos = tracker.scan()
    stats = tracker.get_stats()
    
    print(f"\n📝 TODO Tracker Results")
    print(f"{'='*50}")
    print(f"Total TODOs found: {stats['total']}")
    print(f"\nBy Type:")
    for todo_type, count in stats['by_type'].items():
        print(f"  {todo_type}: {count}")
    print(f"\nBy Priority:")
    for priority, count in stats['by_priority'].items():
        print(f"  {priority.upper()}: {count}")
    print(f"\nTop 10 Files with Most TODOs:")
    sorted_files = sorted(stats['by_file'].items(), key=lambda x: x[1], reverse=True)[:10]
    for file_path, count in sorted_files:
        print(f"  {file_path}: {count}")
