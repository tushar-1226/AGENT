"""
Shortcuts Manager - Keyboard Shortcuts Management
Manage and customize keyboard shortcuts for power users
"""

import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ShortcutsManager:
    """Manage keyboard shortcuts"""
    
    # Default shortcuts
    DEFAULT_SHORTCUTS = {
        # Navigation
        "goto_file": {"key": "Ctrl+P", "description": "Go to file"},
        "goto_line": {"key": "Ctrl+G", "description": "Go to line"},
        "goto_symbol": {"key": "Ctrl+Shift+O", "description": "Go to symbol"},
        "goto_definition": {"key": "F12", "description": "Go to definition"},
        "find_references": {"key": "Shift+F12", "description": "Find references"},
        
        # Editing
        "save": {"key": "Ctrl+S", "description": "Save file"},
        "save_all": {"key": "Ctrl+Shift+S", "description": "Save all files"},
        "undo": {"key": "Ctrl+Z", "description": "Undo"},
        "redo": {"key": "Ctrl+Y", "description": "Redo"},
        "cut": {"key": "Ctrl+X", "description": "Cut"},
        "copy": {"key": "Ctrl+C", "description": "Copy"},
        "paste": {"key": "Ctrl+V", "description": "Paste"},
        "select_all": {"key": "Ctrl+A", "description": "Select all"},
        "duplicate_line": {"key": "Ctrl+D", "description": "Duplicate line"},
        "delete_line": {"key": "Ctrl+Shift+K", "description": "Delete line"},
        "move_line_up": {"key": "Alt+Up", "description": "Move line up"},
        "move_line_down": {"key": "Alt+Down", "description": "Move line down"},
        "comment_line": {"key": "Ctrl+/", "description": "Toggle comment"},
        "format_document": {"key": "Shift+Alt+F", "description": "Format document"},
        
        # Search
        "find": {"key": "Ctrl+F", "description": "Find"},
        "find_replace": {"key": "Ctrl+H", "description": "Find and replace"},
        "find_in_files": {"key": "Ctrl+Shift+F", "description": "Find in files"},
        
        # Code
        "code_predict": {"key": "Ctrl+Space", "description": "Code prediction"},
        "code_review": {"key": "Ctrl+Shift+R", "description": "Review code"},
        "code_translate": {"key": "Ctrl+Shift+T", "description": "Translate code"},
        "generate_docs": {"key": "Ctrl+Shift+D", "description": "Generate docs"},
        "run_code": {"key": "Ctrl+Enter", "description": "Run code"},
        "debug": {"key": "F5", "description": "Start debugging"},
        
        # Terminal
        "toggle_terminal": {"key": "Ctrl+`", "description": "Toggle terminal"},
        "new_terminal": {"key": "Ctrl+Shift+`", "description": "New terminal"},
        
        # View
        "toggle_sidebar": {"key": "Ctrl+B", "description": "Toggle sidebar"},
        "toggle_panel": {"key": "Ctrl+J", "description": "Toggle panel"},
        "zoom_in": {"key": "Ctrl+=", "description": "Zoom in"},
        "zoom_out": {"key": "Ctrl+-", "description": "Zoom out"},
        "zoom_reset": {"key": "Ctrl+0", "description": "Reset zoom"},
        
        # Git
        "git_commit": {"key": "Ctrl+Shift+G", "description": "Git commit"},
        "git_push": {"key": "Ctrl+Shift+P", "description": "Git push"},
        "git_pull": {"key": "Ctrl+Shift+L", "description": "Git pull"},
        
        # Snippets
        "insert_snippet": {"key": "Ctrl+Shift+I", "description": "Insert snippet"},
        "save_snippet": {"key": "Ctrl+Shift+N", "description": "Save as snippet"},
        
        # AI Features
        "ai_chat": {"key": "Ctrl+Shift+A", "description": "Open AI chat"},
        "ai_explain": {"key": "Ctrl+Shift+E", "description": "Explain code"},
        "ai_fix": {"key": "Ctrl+Shift+X", "description": "AI fix"},
        
        # Project
        "new_file": {"key": "Ctrl+N", "description": "New file"},
        "open_file": {"key": "Ctrl+O", "description": "Open file"},
        "close_file": {"key": "Ctrl+W", "description": "Close file"},
        "close_all": {"key": "Ctrl+Shift+W", "description": "Close all files"},
        
        # Misc
        "command_palette": {"key": "Ctrl+Shift+P", "description": "Command palette"},
        "quick_actions": {"key": "Ctrl+Q", "description": "Quick actions"},
        "settings": {"key": "Ctrl+,", "description": "Open settings"},
    }
    
    def __init__(self, config_path: str = "shortcuts_config.json"):
        """
        Initialize shortcuts manager
        
        Args:
            config_path: Path to shortcuts configuration file
        """
        self.config_path = config_path
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self._load_custom_shortcuts()
        logger.info("Shortcuts Manager initialized")
    
    def _load_custom_shortcuts(self):
        """Load custom shortcuts from config file"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    custom = json.load(f)
                    self.shortcuts.update(custom)
                logger.info(f"Loaded {len(custom)} custom shortcuts")
        except Exception as e:
            logger.error(f"Error loading custom shortcuts: {e}")
    
    def _save_shortcuts(self):
        """Save shortcuts to config file"""
        try:
            # Only save non-default shortcuts
            custom_shortcuts = {}
            for action, shortcut in self.shortcuts.items():
                default = self.DEFAULT_SHORTCUTS.get(action)
                if not default or shortcut != default:
                    custom_shortcuts[action] = shortcut
            
            with open(self.config_path, 'w') as f:
                json.dump(custom_shortcuts, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving shortcuts: {e}")
            return False
    
    def get_all_shortcuts(self) -> Dict[str, Dict[str, str]]:
        """Get all shortcuts"""
        return self.shortcuts.copy()
    
    def get_shortcuts_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get shortcuts organized by category"""
        categories = {
            "Navigation": [],
            "Editing": [],
            "Search": [],
            "Code": [],
            "Terminal": [],
            "View": [],
            "Git": [],
            "Snippets": [],
            "AI Features": [],
            "Project": [],
            "Misc": []
        }
        
        # Categorize shortcuts
        category_map = {
            "goto_": "Navigation",
            "find": "Search",
            "save": "Editing",
            "undo": "Editing",
            "redo": "Editing",
            "cut": "Editing",
            "copy": "Editing",
            "paste": "Editing",
            "select": "Editing",
            "duplicate": "Editing",
            "delete": "Editing",
            "move": "Editing",
            "comment": "Editing",
            "format": "Editing",
            "code_": "Code",
            "terminal": "Terminal",
            "toggle": "View",
            "zoom": "View",
            "git_": "Git",
            "snippet": "Snippets",
            "ai_": "AI Features",
            "new_": "Project",
            "open_": "Project",
            "close_": "Project",
        }
        
        for action, shortcut in self.shortcuts.items():
            category = "Misc"
            for prefix, cat in category_map.items():
                if action.startswith(prefix):
                    category = cat
                    break
            
            categories[category].append({
                "action": action,
                "key": shortcut["key"],
                "description": shortcut["description"]
            })
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def get_shortcut(self, action: str) -> Optional[Dict[str, str]]:
        """Get shortcut for specific action"""
        return self.shortcuts.get(action)
    
    def set_shortcut(
        self,
        action: str,
        key: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Set custom shortcut
        
        Args:
            action: Action name
            key: Keyboard shortcut (e.g., "Ctrl+S")
            description: Optional description
            
        Returns:
            Success status
        """
        try:
            # Check for conflicts
            conflict = self.find_conflict(key, exclude_action=action)
            if conflict:
                logger.warning(f"Shortcut conflict: {key} already used for {conflict}")
                return False
            
            # Set shortcut
            if description is None and action in self.shortcuts:
                description = self.shortcuts[action]["description"]
            
            self.shortcuts[action] = {
                "key": key,
                "description": description or action.replace("_", " ").title()
            }
            
            return self._save_shortcuts()
            
        except Exception as e:
            logger.error(f"Error setting shortcut: {e}")
            return False
    
    def remove_shortcut(self, action: str) -> bool:
        """Remove custom shortcut (reset to default)"""
        try:
            if action in self.DEFAULT_SHORTCUTS:
                self.shortcuts[action] = self.DEFAULT_SHORTCUTS[action]
            elif action in self.shortcuts:
                del self.shortcuts[action]
            
            return self._save_shortcuts()
            
        except Exception as e:
            logger.error(f"Error removing shortcut: {e}")
            return False
    
    def find_conflict(
        self,
        key: str,
        exclude_action: Optional[str] = None
    ) -> Optional[str]:
        """Find if shortcut key is already in use"""
        for action, shortcut in self.shortcuts.items():
            if action != exclude_action and shortcut["key"] == key:
                return action
        return None
    
    def reset_to_defaults(self) -> bool:
        """Reset all shortcuts to defaults"""
        try:
            self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
            
            # Remove custom config file
            if Path(self.config_path).exists():
                Path(self.config_path).unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting shortcuts: {e}")
            return False
    
    def export_shortcuts(self, file_path: str) -> bool:
        """Export shortcuts to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.shortcuts, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exporting shortcuts: {e}")
            return False
    
    def import_shortcuts(self, file_path: str) -> bool:
        """Import shortcuts from file"""
        try:
            with open(file_path, 'r') as f:
                imported = json.load(f)
            
            self.shortcuts.update(imported)
            return self._save_shortcuts()
            
        except Exception as e:
            logger.error(f"Error importing shortcuts: {e}")
            return False
    
    def search_shortcuts(self, query: str) -> List[Dict[str, Any]]:
        """Search shortcuts by action or description"""
        query_lower = query.lower()
        results = []
        
        for action, shortcut in self.shortcuts.items():
            if (query_lower in action.lower() or 
                query_lower in shortcut["description"].lower() or
                query_lower in shortcut["key"].lower()):
                results.append({
                    "action": action,
                    "key": shortcut["key"],
                    "description": shortcut["description"]
                })
        
        return results
