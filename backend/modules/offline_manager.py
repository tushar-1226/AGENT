"""
Offline Mode Manager
Response caching, local-first database sync, offline code editing, and action queuing
"""

import os
import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class ActionType(Enum):
    """Types of queued actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CUSTOM = "custom"


class SyncStatus(Enum):
    """Sync status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ResponseCache:
    """Cache API responses with TTL for offline access"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cached_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                response_data TEXT NOT NULL,
                content_type TEXT,
                status_code INTEGER DEFAULT 200,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                etag TEXT,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cache_key 
            ON cached_responses(cache_key)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires_at 
            ON cached_responses(expires_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def _generate_cache_key(self, endpoint: str, method: str, params: Dict = None) -> str:
        """Generate unique cache key"""
        key_data = f"{method}:{endpoint}"
        if params:
            key_data += f":{json.dumps(params, sort_keys=True)}"
        
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def set(self, endpoint: str, method: str, response_data: Any,
            ttl_seconds: int = 3600, params: Dict = None,
            content_type: str = "application/json", status_code: int = 200) -> bool:
        """Cache a response"""
        try:
            cache_key = self._generate_cache_key(endpoint, method, params)
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            # Serialize response data
            if isinstance(response_data, (dict, list)):
                data_str = json.dumps(response_data)
            else:
                data_str = str(response_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cached_responses
                (cache_key, endpoint, method, response_data, content_type, 
                 status_code, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cache_key, endpoint, method, data_str, content_type, 
                  status_code, expires_at))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error caching response: {e}")
            return False
    
    def get(self, endpoint: str, method: str, params: Dict = None) -> Optional[Dict]:
        """Get cached response if valid"""
        try:
            cache_key = self._generate_cache_key(endpoint, method, params)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT response_data, content_type, status_code, expires_at
                FROM cached_responses
                WHERE cache_key = ? AND expires_at > ?
            ''', (cache_key, datetime.now()))
            
            result = cursor.fetchone()
            
            if result:
                # Update last accessed time
                cursor.execute('''
                    UPDATE cached_responses
                    SET last_accessed = ?
                    WHERE cache_key = ?
                ''', (datetime.now(), cache_key))
                conn.commit()
            
            conn.close()
            
            if result:
                response_data, content_type, status_code, expires_at = result
                
                # Parse JSON if applicable
                if content_type == "application/json":
                    try:
                        response_data = json.loads(response_data)
                    except:
                        pass
                
                return {
                    'data': response_data,
                    'content_type': content_type,
                    'status_code': status_code,
                    'cached': True,
                    'expires_at': expires_at
                }
            
            return None
        except Exception as e:
            print(f"Error retrieving cached response: {e}")
            return None
    
    def invalidate(self, endpoint: str = None, method: str = None) -> bool:
        """Invalidate cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if endpoint and method:
                # Invalidate specific endpoint
                cursor.execute('''
                    DELETE FROM cached_responses
                    WHERE endpoint = ? AND method = ?
                ''', (endpoint, method))
            elif endpoint:
                # Invalidate all methods for endpoint
                cursor.execute('''
                    DELETE FROM cached_responses
                    WHERE endpoint = ?
                ''', (endpoint,))
            else:
                # Clear all cache
                cursor.execute('DELETE FROM cached_responses')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error invalidating cache: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM cached_responses
                WHERE expires_at < ?
            ''', (datetime.now(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM cached_responses')
            total_entries = cursor.fetchone()[0]
            
            # Valid entries
            cursor.execute('''
                SELECT COUNT(*) FROM cached_responses
                WHERE expires_at > ?
            ''', (datetime.now(),))
            valid_entries = cursor.fetchone()[0]
            
            # Expired entries
            expired_entries = total_entries - valid_entries
            
            # Total size (approximate)
            cursor.execute('''
                SELECT SUM(LENGTH(response_data)) FROM cached_responses
            ''')
            total_size = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {}


class OfflineQueue:
    """Queue POST/PUT/DELETE operations for offline mode"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize offline queue database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                payload TEXT,
                headers TEXT,
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                user_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_queue_status 
            ON offline_queue(status)
        ''')
        
        conn.commit()
        conn.close()
    
    def enqueue(self, action_type: ActionType, endpoint: str, method: str,
                payload: Dict = None, headers: Dict = None, priority: int = 5,
                user_id: int = None) -> int:
        """Add action to offline queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            payload_str = json.dumps(payload) if payload else None
            headers_str = json.dumps(headers) if headers else None
            
            cursor.execute('''
                INSERT INTO offline_queue
                (action_type, endpoint, method, payload, headers, priority, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (action_type.value, endpoint, method, payload_str, 
                  headers_str, priority, user_id))
            
            action_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return action_id
        except Exception as e:
            print(f"Error enqueueing action: {e}")
            return -1
    
    def get_pending_actions(self, limit: int = 50) -> List[Dict]:
        """Get pending actions from queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, action_type, endpoint, method, payload, headers, 
                       priority, created_at, attempts
                FROM offline_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            actions = []
            for row in rows:
                actions.append({
                    'id': row[0],
                    'action_type': row[1],
                    'endpoint': row[2],
                    'method': row[3],
                    'payload': json.loads(row[4]) if row[4] else None,
                    'headers': json.loads(row[5]) if row[5] else None,
                    'priority': row[6],
                    'created_at': row[7],
                    'attempts': row[8]
                })
            
            return actions
        except Exception as e:
            print(f"Error getting pending actions: {e}")
            return []
    
    def mark_completed(self, action_id: int) -> bool:
        """Mark action as completed"""
        return self._update_status(action_id, SyncStatus.COMPLETED)
    
    def mark_failed(self, action_id: int, error_message: str) -> bool:
        """Mark action as failed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE offline_queue
                SET status = ?, error_message = ?, attempts = attempts + 1,
                    last_attempt = ?
                WHERE id = ?
            ''', (SyncStatus.FAILED.value, error_message, datetime.now(), action_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking action as failed: {e}")
            return False
    
    def _update_status(self, action_id: int, status: SyncStatus) -> bool:
        """Update action status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE offline_queue
                SET status = ?, last_attempt = ?
                WHERE id = ?
            ''', (status.value, datetime.now(), action_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False
    
    def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count by status
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM offline_queue
                GROUP BY status
            ''')
            
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total actions
            total = sum(status_counts.values())
            
            conn.close()
            
            return {
                'total_actions': total,
                'pending': status_counts.get('pending', 0),
                'completed': status_counts.get('completed', 0),
                'failed': status_counts.get('failed', 0),
                'in_progress': status_counts.get('in_progress', 0)
            }
        except Exception as e:
            print(f"Error getting queue stats: {e}")
            return {}
    
    def clear_completed(self, days_old: int = 7) -> int:
        """Clear completed actions older than N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor.execute('''
                DELETE FROM offline_queue
                WHERE status = 'completed' AND created_at < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
        except Exception as e:
            print(f"Error clearing completed actions: {e}")
            return 0


class SyncManager:
    """Manage synchronization of offline actions when online"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.queue = OfflineQueue(db_path)
        self.cache = ResponseCache(db_path)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize sync status database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_started TIMESTAMP,
                sync_completed TIMESTAMP,
                actions_synced INTEGER DEFAULT 0,
                actions_failed INTEGER DEFAULT 0,
                status TEXT DEFAULT 'idle',
                last_error TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_sync(self) -> Dict:
        """Start synchronization process"""
        sync_id = self._create_sync_record()
        
        pending_actions = self.queue.get_pending_actions()
        
        if not pending_actions:
            return {
                'sync_id': sync_id,
                'status': 'no_actions',
                'message': 'No pending actions to sync'
            }
        
        synced = 0
        failed = 0
        
        for action in pending_actions:
            success, error = self._sync_action(action)
            
            if success:
                self.queue.mark_completed(action['id'])
                synced += 1
            else:
                self.queue.mark_failed(action['id'], error)
                failed += 1
        
        self._complete_sync_record(sync_id, synced, failed)
        
        return {
            'sync_id': sync_id,
            'status': 'completed',
            'actions_synced': synced,
            'actions_failed': failed,
            'total_actions': len(pending_actions)
        }
    
    def _sync_action(self, action: Dict) -> Tuple[bool, str]:
        """Sync a single action (placeholder - actual implementation would make HTTP request)"""
        # In a real implementation, this would:
        # 1. Make the actual HTTP request to the endpoint
        # 2. Handle the response
        # 3. Deal with conflicts
        
        # For now, we'll simulate success
        # In production, you'd use requests or httpx here
        
        try:
            # Simulate API call
            # response = requests.request(
            #     method=action['method'],
            #     url=action['endpoint'],
            #     json=action['payload'],
            #     headers=action['headers']
            # )
            
            # Placeholder: assume success
            return (True, None)
        except Exception as e:
            return (False, str(e))
    
    def _create_sync_record(self) -> int:
        """Create a new sync record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sync_status (sync_started, status)
                VALUES (?, 'in_progress')
            ''', (datetime.now(),))
            
            sync_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return sync_id
        except Exception as e:
            print(f"Error creating sync record: {e}")
            return -1
    
    def _complete_sync_record(self, sync_id: int, synced: int, failed: int) -> bool:
        """Complete a sync record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sync_status
                SET sync_completed = ?, status = 'completed',
                    actions_synced = ?, actions_failed = ?
                WHERE id = ?
            ''', (datetime.now(), synced, failed, sync_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error completing sync record: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest sync
            cursor.execute('''
                SELECT sync_started, sync_completed, actions_synced, 
                       actions_failed, status
                FROM sync_status
                ORDER BY id DESC
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'last_sync_started': result[0],
                    'last_sync_completed': result[1],
                    'actions_synced': result[2],
                    'actions_failed': result[3],
                    'status': result[4],
                    'pending_actions': self.queue.get_queue_stats().get('pending', 0)
                }
            
            return {
                'status': 'never_synced',
                'pending_actions': self.queue.get_queue_stats().get('pending', 0)
            }
        except Exception as e:
            print(f"Error getting sync status: {e}")
            return {}


class ConflictResolver:
    """Handle merge conflicts during sync"""
    
    def __init__(self):
        self.resolution_strategies = {
            'client_wins': self._client_wins,
            'server_wins': self._server_wins,
            'manual': self._manual_resolution,
            'merge': self._merge_strategy
        }
    
    def resolve_conflict(self, local_data: Dict, server_data: Dict,
                        strategy: str = 'client_wins') -> Dict:
        """Resolve conflict between local and server data"""
        
        resolver = self.resolution_strategies.get(strategy, self._client_wins)
        return resolver(local_data, server_data)
    
    def _client_wins(self, local_data: Dict, server_data: Dict) -> Dict:
        """Client data takes precedence"""
        return {
            'resolved_data': local_data,
            'strategy_used': 'client_wins',
            'conflicts': []
        }
    
    def _server_wins(self, local_data: Dict, server_data: Dict) -> Dict:
        """Server data takes precedence"""
        return {
            'resolved_data': server_data,
            'strategy_used': 'server_wins',
            'conflicts': []
        }
    
    def _manual_resolution(self, local_data: Dict, server_data: Dict) -> Dict:
        """Flag for manual resolution"""
        return {
            'resolved_data': None,
            'strategy_used': 'manual',
            'requires_manual_resolution': True,
            'conflicts': self._detect_conflicts(local_data, server_data)
        }
    
    def _merge_strategy(self, local_data: Dict, server_data: Dict) -> Dict:
        """Attempt to merge both datasets"""
        merged = server_data.copy()
        conflicts = []
        
        for key, local_value in local_data.items():
            if key in server_data:
                if server_data[key] != local_value:
                    conflicts.append({
                        'field': key,
                        'local_value': local_value,
                        'server_value': server_data[key]
                    })
                    # For simple merge, prefer local changes
                    merged[key] = local_value
            else:
                merged[key] = local_value
        
        return {
            'resolved_data': merged,
            'strategy_used': 'merge',
            'conflicts': conflicts
        }
    
    def _detect_conflicts(self, local_data: Dict, server_data: Dict) -> List[Dict]:
        """Detect conflicts between local and server data"""
        conflicts = []
        
        all_keys = set(local_data.keys()) | set(server_data.keys())
        
        for key in all_keys:
            local_value = local_data.get(key)
            server_value = server_data.get(key)
            
            if local_value != server_value:
                conflicts.append({
                    'field': key,
                    'local_value': local_value,
                    'server_value': server_value,
                    'conflict_type': 'value_mismatch'
                })
        
        return conflicts


# Export classes
__all__ = [
    'ResponseCache',
    'OfflineQueue',
    'SyncManager',
    'ConflictResolver',
    'ActionType',
    'SyncStatus'
]
