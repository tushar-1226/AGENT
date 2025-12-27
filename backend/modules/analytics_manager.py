"""
Analytics Module
Track API calls, performance metrics, and user activity
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os


class AnalyticsManager:
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # API Calls tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT,
                request_size INTEGER,
                response_size INTEGER
            )
        ''')

        # User activity tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                unit TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Error logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message TEXT,
                stack_trace TEXT,
                endpoint TEXT,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def log_api_call(self, endpoint: str, method: str, status_code: int,
                     response_time: float, user_id: int = None,
                     error_message: str = None, request_size: int = 0,
                     response_size: int = 0) -> bool:
        """Log an API call"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO api_calls
                (endpoint, method, status_code, response_time, user_id, error_message, request_size, response_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (endpoint, method, status_code, response_time, user_id, error_message, request_size, response_size))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging API call: {e}")
            return False

    def log_user_activity(self, user_id: int, action: str, details: str = None) -> bool:
        """Log user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO user_activity (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging user activity: {e}")
            return False

    def log_performance_metric(self, metric_name: str, metric_value: float, unit: str = None) -> bool:
        """Log a performance metric"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO performance_metrics (metric_name, metric_value, unit)
                VALUES (?, ?, ?)
            ''', (metric_name, metric_value, unit))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging performance metric: {e}")
            return False

    def log_error(self, error_type: str, error_message: str, stack_trace: str = None,
                  endpoint: str = None, user_id: int = None) -> bool:
        """Log an error"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO error_logs (error_type, error_message, stack_trace, endpoint, user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (error_type, error_message, stack_trace, endpoint, user_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging error: {e}")
            return False

    def get_api_call_stats(self, hours: int = 24) -> Dict:
        """Get API call statistics for the last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Total calls
            cursor.execute('''
                SELECT COUNT(*) FROM api_calls
                WHERE timestamp > ?
            ''', (cutoff_time,))
            total_calls = cursor.fetchone()[0]

            # Calls by status
            cursor.execute('''
                SELECT
                    CASE
                        WHEN status_code >= 200 AND status_code < 300 THEN 'success'
                        WHEN status_code >= 400 AND status_code < 500 THEN 'client_error'
                        WHEN status_code >= 500 THEN 'server_error'
                        ELSE 'other'
                    END as status,
                    COUNT(*) as count
                FROM api_calls
                WHERE timestamp > ?
                GROUP BY status
            ''', (cutoff_time,))

            status_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

            # Average response time
            cursor.execute('''
                SELECT AVG(response_time) FROM api_calls
                WHERE timestamp > ?
            ''', (cutoff_time,))
            avg_response_time = cursor.fetchone()[0] or 0

            # Most called endpoints
            cursor.execute('''
                SELECT endpoint, COUNT(*) as count
                FROM api_calls
                WHERE timestamp > ?
                GROUP BY endpoint
                ORDER BY count DESC
                LIMIT 10
            ''', (cutoff_time,))

            top_endpoints = [{"endpoint": row[0], "count": row[1]} for row in cursor.fetchall()]

            # Calls over time (hourly)
            cursor.execute('''
                SELECT
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count
                FROM api_calls
                WHERE timestamp > ?
                GROUP BY hour
                ORDER BY hour
            ''', (cutoff_time,))

            calls_over_time = [{"time": row[0], "count": row[1]} for row in cursor.fetchall()]

            conn.close()

            return {
                "total_calls": total_calls,
                "status_breakdown": status_breakdown,
                "avg_response_time": round(avg_response_time, 2),
                "top_endpoints": top_endpoints,
                "calls_over_time": calls_over_time,
                "time_period_hours": hours
            }
        except Exception as e:
            print(f"Error getting API call stats: {e}")
            return {}

    def get_user_activity_stats(self, hours: int = 24) -> Dict:
        """Get user activity statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Total activities
            cursor.execute('''
                SELECT COUNT(*) FROM user_activity
                WHERE timestamp > ?
            ''', (cutoff_time,))
            total_activities = cursor.fetchone()[0]

            # Active users
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM user_activity
                WHERE timestamp > ?
            ''', (cutoff_time,))
            active_users = cursor.fetchone()[0]

            # Top actions
            cursor.execute('''
                SELECT action, COUNT(*) as count
                FROM user_activity
                WHERE timestamp > ?
                GROUP BY action
                ORDER BY count DESC
                LIMIT 10
            ''', (cutoff_time,))

            top_actions = [{"action": row[0], "count": row[1]} for row in cursor.fetchall()]

            # Activity over time
            cursor.execute('''
                SELECT
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count
                FROM user_activity
                WHERE timestamp > ?
                GROUP BY hour
                ORDER BY hour
            ''', (cutoff_time,))

            activity_over_time = [{"time": row[0], "count": row[1]} for row in cursor.fetchall()]

            conn.close()

            return {
                "total_activities": total_activities,
                "active_users": active_users,
                "top_actions": top_actions,
                "activity_over_time": activity_over_time,
                "time_period_hours": hours
            }
        except Exception as e:
            print(f"Error getting user activity stats: {e}")
            return {}

    def get_error_stats(self, hours: int = 24) -> Dict:
        """Get error statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Total errors
            cursor.execute('''
                SELECT COUNT(*) FROM error_logs
                WHERE timestamp > ?
            ''', (cutoff_time,))
            total_errors = cursor.fetchone()[0]

            # Errors by type
            cursor.execute('''
                SELECT error_type, COUNT(*) as count
                FROM error_logs
                WHERE timestamp > ?
                GROUP BY error_type
                ORDER BY count DESC
            ''', (cutoff_time,))

            errors_by_type = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]

            # Recent errors
            cursor.execute('''
                SELECT error_type, error_message, endpoint, timestamp
                FROM error_logs
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 20
            ''', (cutoff_time,))

            recent_errors = [{
                "type": row[0],
                "message": row[1],
                "endpoint": row[2],
                "timestamp": row[3]
            } for row in cursor.fetchall()]

            conn.close()

            return {
                "total_errors": total_errors,
                "errors_by_type": errors_by_type,
                "recent_errors": recent_errors,
                "time_period_hours": hours
            }
        except Exception as e:
            print(f"Error getting error stats: {e}")
            return {}

    def get_performance_stats(self, hours: int = 24) -> Dict:
        """Get performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Average metrics
            cursor.execute('''
                SELECT metric_name, AVG(metric_value) as avg_value, unit
                FROM performance_metrics
                WHERE timestamp > ?
                GROUP BY metric_name, unit
            ''', (cutoff_time,))

            avg_metrics = [{
                "name": row[0],
                "value": round(row[1], 2),
                "unit": row[2]
            } for row in cursor.fetchall()]

            conn.close()

            return {
                "avg_metrics": avg_metrics,
                "time_period_hours": hours
            }
        except Exception as e:
            print(f"Error getting performance stats: {e}")
            return {}

    def get_complete_analytics(self, hours: int = 24) -> Dict:
        """Get complete analytics overview"""
        return {
            "timestamp": datetime.now().isoformat(),
            "api_calls": self.get_api_call_stats(hours),
            "user_activity": self.get_user_activity_stats(hours),
            "errors": self.get_error_stats(hours),
            "performance": self.get_performance_stats(hours)
        }

    def get_quality_metrics(self) -> Dict:
        """Get quality metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Success rate (last 24 hours)
            cursor.execute('''
                SELECT
                    COUNT(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM api_calls
                WHERE timestamp > datetime('now', '-24 hours')
            ''')
            success_rate = cursor.fetchone()[0] or 0

            # Average response time (last 24 hours)
            cursor.execute('''
                SELECT AVG(response_time)
                FROM api_calls
                WHERE timestamp > datetime('now', '-24 hours')
            ''')
            avg_response_time = cursor.fetchone()[0] or 0

            # Error rate (last 24 hours)
            cursor.execute('''
                SELECT
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) * 100.0 / COUNT(*) as error_rate
                FROM api_calls
                WHERE timestamp > datetime('now', '-24 hours')
            ''')
            error_rate = cursor.fetchone()[0] or 0

            # Uptime calculation (based on successful calls)
            cursor.execute('''
                SELECT
                    COUNT(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 END) * 100.0 /
                    COUNT(*) as uptime
                FROM api_calls
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            uptime = cursor.fetchone()[0] or 0

            conn.close()

            return {
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 2),
                "error_rate": round(error_rate, 2),
                "uptime": round(uptime, 2)
            }
        except Exception as e:
            print(f"Error getting quality metrics: {e}")
            return {}
