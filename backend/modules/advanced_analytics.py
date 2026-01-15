"""
Advanced Analytics Module
Time tracking, burnout prediction, code quality trends, productivity scoring,
project health dashboard, and AI-powered sprint planning
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import statistics
import subprocess

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class TimeTracker:
    """Track developer time from Git commits"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def get_commit_history(self, days: int = 30, author: str = None) -> List[Dict]:
        """Get commit history from Git"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            cmd = [
                "git", "-C", self.repo_path, "log",
                f"--since={cutoff_date}",
                "--pretty=format:%H|%an|%ae|%at|%s",
                "--numstat"
            ]
            
            if author:
                cmd.extend(["--author", author])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            commits = []
            current_commit = None
            
            for line in result.stdout.split('\n'):
                if '|' in line and len(line.split('|')) == 5:
                    # New commit
                    if current_commit:
                        commits.append(current_commit)
                    
                    parts = line.split('|')
                    current_commit = {
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'timestamp': datetime.fromtimestamp(int(parts[3])),
                        'message': parts[4],
                        'files_changed': 0,
                        'lines_added': 0,
                        'lines_removed': 0,
                        'files': []
                    }
                elif line.strip() and current_commit:
                    # File stats
                    parts = line.split('\t')
                    if len(parts) == 3:
                        added = parts[0] if parts[0] != '-' else '0'
                        removed = parts[1] if parts[1] != '-' else '0'
                        filename = parts[2]
                        
                        current_commit['files_changed'] += 1
                        current_commit['lines_added'] += int(added)
                        current_commit['lines_removed'] += int(removed)
                        current_commit['files'].append(filename)
            
            if current_commit:
                commits.append(current_commit)
            
            return commits
        except Exception as e:
            print(f"Error getting commit history: {e}")
            return []
    
    def calculate_time_tracking(self, commits: List[Dict]) -> Dict:
        """Calculate time tracking metrics from commits"""
        if not commits:
            return {
                'total_commits': 0,
                'total_hours_estimate': 0,
                'daily_breakdown': [],
                'hourly_distribution': {},
                'work_patterns': {}
            }
        
        # Group commits by day
        daily_commits = defaultdict(list)
        hourly_commits = defaultdict(int)
        
        for commit in commits:
            date_key = commit['timestamp'].strftime('%Y-%m-%d')
            hour_key = commit['timestamp'].hour
            
            daily_commits[date_key].append(commit)
            hourly_commits[hour_key] += 1
        
        # Calculate estimated hours (rough heuristic: ~2-4 hours per commit session)
        # Group commits within 2 hours as same session
        total_sessions = 0
        daily_breakdown = []
        
        for date, day_commits in sorted(daily_commits.items()):
            day_commits_sorted = sorted(day_commits, key=lambda x: x['timestamp'])
            sessions = 1
            last_time = day_commits_sorted[0]['timestamp']
            
            for commit in day_commits_sorted[1:]:
                time_diff = (commit['timestamp'] - last_time).total_seconds() / 3600
                if time_diff > 2:  # More than 2 hours gap = new session
                    sessions += 1
                last_time = commit['timestamp']
            
            total_sessions += sessions
            estimated_hours = sessions * 2.5  # Average 2.5 hours per session
            
            daily_breakdown.append({
                'date': date,
                'commits': len(day_commits),
                'sessions': sessions,
                'estimated_hours': round(estimated_hours, 1),
                'lines_changed': sum(c['lines_added'] + c['lines_removed'] for c in day_commits)
            })
        
        # Analyze work patterns
        work_patterns = self._analyze_work_patterns(commits)
        
        return {
            'total_commits': len(commits),
            'total_sessions': total_sessions,
            'total_hours_estimate': round(total_sessions * 2.5, 1),
            'daily_breakdown': daily_breakdown,
            'hourly_distribution': dict(hourly_commits),
            'work_patterns': work_patterns
        }
    
    def _analyze_work_patterns(self, commits: List[Dict]) -> Dict:
        """Analyze work patterns for insights"""
        late_night_commits = 0  # 11 PM - 6 AM
        weekend_commits = 0
        weekday_commits = 0
        
        for commit in commits:
            hour = commit['timestamp'].hour
            weekday = commit['timestamp'].weekday()
            
            if hour >= 23 or hour < 6:
                late_night_commits += 1
            
            if weekday >= 5:  # Saturday, Sunday
                weekend_commits += 1
            else:
                weekday_commits += 1
        
        return {
            'late_night_commits': late_night_commits,
            'late_night_percentage': round(late_night_commits / len(commits) * 100, 1) if commits else 0,
            'weekend_commits': weekend_commits,
            'weekend_percentage': round(weekend_commits / len(commits) * 100, 1) if commits else 0,
            'weekday_commits': weekday_commits,
            'weekday_percentage': round(weekday_commits / len(commits) * 100, 1) if commits else 0
        }


class BurnoutPredictor:
    """Predict burnout risk based on commit patterns and work habits"""
    
    def __init__(self):
        self.risk_factors = {
            'high_late_night_work': 15,  # Weight
            'weekend_overwork': 12,
            'inconsistent_schedule': 10,
            'high_commit_frequency': 8,
            'large_code_changes': 7,
            'lack_of_breaks': 15
        }
    
    def analyze_burnout_risk(self, time_tracking: Dict, commits: List[Dict]) -> Dict:
        """Analyze burnout risk from work patterns"""
        risk_score = 0
        risk_indicators = []
        
        work_patterns = time_tracking.get('work_patterns', {})
        
        # Factor 1: Late night work
        late_night_pct = work_patterns.get('late_night_percentage', 0)
        if late_night_pct > 20:
            risk_score += self.risk_factors['high_late_night_work']
            risk_indicators.append({
                'factor': 'High late-night work',
                'severity': 'high' if late_night_pct > 40 else 'medium',
                'description': f'{late_night_pct}% of commits made between 11 PM - 6 AM',
                'recommendation': 'Consider establishing better work-life boundaries'
            })
        
        # Factor 2: Weekend overwork
        weekend_pct = work_patterns.get('weekend_percentage', 0)
        if weekend_pct > 25:
            risk_score += self.risk_factors['weekend_overwork']
            risk_indicators.append({
                'factor': 'Weekend overwork',
                'severity': 'high' if weekend_pct > 40 else 'medium',
                'description': f'{weekend_pct}% of commits made on weekends',
                'recommendation': 'Take regular breaks and weekends off to recharge'
            })
        
        # Factor 3: Commit frequency spikes
        daily_breakdown = time_tracking.get('daily_breakdown', [])
        if daily_breakdown:
            daily_commits = [day['commits'] for day in daily_breakdown]
            if len(daily_commits) > 7:
                avg_commits = statistics.mean(daily_commits)
                max_commits = max(daily_commits)
                
                if max_commits > avg_commits * 3:
                    risk_score += self.risk_factors['high_commit_frequency']
                    risk_indicators.append({
                        'factor': 'Inconsistent workload',
                        'severity': 'medium',
                        'description': 'Large spikes in daily commit count detected',
                        'recommendation': 'Try to distribute work more evenly across days'
                    })
        
        # Factor 4: Lack of breaks (consecutive work days)
        consecutive_days = self._calculate_consecutive_work_days(daily_breakdown)
        if consecutive_days > 10:
            risk_score += self.risk_factors['lack_of_breaks']
            risk_indicators.append({
                'factor': 'Lack of breaks',
                'severity': 'high' if consecutive_days > 14 else 'medium',
                'description': f'{consecutive_days} consecutive days without a break',
                'recommendation': 'Schedule regular days off to prevent burnout'
            })
        
        # Normalize risk score to 0-100
        max_possible_score = sum(self.risk_factors.values())
        normalized_score = min(100, (risk_score / max_possible_score) * 100)
        
        # Determine risk level
        if normalized_score < 30:
            risk_level = 'low'
            risk_color = 'green'
        elif normalized_score < 60:
            risk_level = 'medium'
            risk_color = 'yellow'
        else:
            risk_level = 'high'
            risk_color = 'red'
        
        return {
            'risk_score': round(normalized_score, 1),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_indicators': risk_indicators,
            'overall_recommendation': self._generate_recommendation(risk_level, risk_indicators)
        }
    
    def _calculate_consecutive_work_days(self, daily_breakdown: List[Dict]) -> int:
        """Calculate longest streak of consecutive work days"""
        if not daily_breakdown:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        sorted_days = sorted(daily_breakdown, key=lambda x: x['date'])
        
        for i in range(len(sorted_days)):
            if i == 0:
                current_streak = 1
            else:
                prev_date = datetime.strptime(sorted_days[i-1]['date'], '%Y-%m-%d')
                curr_date = datetime.strptime(sorted_days[i]['date'], '%Y-%m-%d')
                
                if (curr_date - prev_date).days == 1:
                    current_streak += 1
                else:
                    max_streak = max(max_streak, current_streak)
                    current_streak = 1
        
        return max(max_streak, current_streak)
    
    def _generate_recommendation(self, risk_level: str, indicators: List[Dict]) -> str:
        """Generate overall recommendation based on risk level"""
        if risk_level == 'low':
            return "Your work patterns look healthy! Keep maintaining a good work-life balance."
        elif risk_level == 'medium':
            return "Some concerning patterns detected. Consider the recommendations to maintain sustainability."
        else:
            return "⚠️ High burnout risk detected! Please prioritize rest and work-life balance. Consider discussing workload with your team."


class CodeQualityTrends:
    """Track code quality metrics over time"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize quality trends database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                complexity_score REAL,
                test_coverage REAL,
                code_smells INTEGER,
                duplications REAL,
                maintainability_rating TEXT,
                security_issues INTEGER,
                total_lines INTEGER,
                comment_ratio REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_snapshot(self, metrics: Dict) -> bool:
        """Record a quality snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO quality_snapshots
                (complexity_score, test_coverage, code_smells, duplications,
                 maintainability_rating, security_issues, total_lines, comment_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('complexity_score', 0),
                metrics.get('test_coverage', 0),
                metrics.get('code_smells', 0),
                metrics.get('duplications', 0),
                metrics.get('maintainability_rating', 'C'),
                metrics.get('security_issues', 0),
                metrics.get('total_lines', 0),
                metrics.get('comment_ratio', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error recording quality snapshot: {e}")
            return False
    
    def get_quality_trends(self, days: int = 30) -> Dict:
        """Get quality trends over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT timestamp, complexity_score, test_coverage, code_smells,
                       duplications, maintainability_rating, security_issues
                FROM quality_snapshots
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {'trend_data': [], 'summary': {}}
            
            trend_data = []
            for row in rows:
                trend_data.append({
                    'timestamp': row[0],
                    'complexity_score': row[1],
                    'test_coverage': row[2],
                    'code_smells': row[3],
                    'duplications': row[4],
                    'maintainability_rating': row[5],
                    'security_issues': row[6]
                })
            
            # Calculate trend direction
            summary = self._calculate_trend_summary(trend_data)
            
            return {
                'trend_data': trend_data,
                'summary': summary
            }
        except Exception as e:
            print(f"Error getting quality trends: {e}")
            return {'trend_data': [], 'summary': {}}
    
    def _calculate_trend_summary(self, trend_data: List[Dict]) -> Dict:
        """Calculate trend direction and summary"""
        if len(trend_data) < 2:
            return {}
        
        first = trend_data[0]
        last = trend_data[-1]
        
        complexity_change = last['complexity_score'] - first['complexity_score']
        coverage_change = last['test_coverage'] - first['test_coverage']
        smells_change = last['code_smells'] - first['code_smells']
        
        return {
            'complexity_trend': 'improving' if complexity_change < 0 else 'degrading',
            'complexity_change': round(complexity_change, 2),
            'coverage_trend': 'improving' if coverage_change > 0 else 'degrading',
            'coverage_change': round(coverage_change, 2),
            'code_smells_trend': 'improving' if smells_change < 0 else 'degrading',
            'code_smells_change': smells_change,
            'overall_health': 'good' if (coverage_change > 0 and smells_change < 0) else 'needs_attention'
        }


class ProductivityScorer:
    """Calculate developer productivity scores with AI recommendations"""
    
    def __init__(self):
        self.gemini_model = None
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def calculate_productivity_score(self, time_tracking: Dict, commits: List[Dict],
                                     tasks_data: Dict = None) -> Dict:
        """Calculate comprehensive productivity score"""
        
        # Factor 1: Commit activity (0-30 points)
        commit_score = min(30, len(commits) * 1.5)
        
        # Factor 2: Code volume (0-25 points)
        total_lines = sum(c.get('lines_added', 0) + c.get('lines_removed', 0) for c in commits)
        code_volume_score = min(25, total_lines / 20)
        
        # Factor 3: Consistency (0-20 points)
        daily_breakdown = time_tracking.get('daily_breakdown', [])
        if len(daily_breakdown) > 1:
            daily_commits = [day['commits'] for day in daily_breakdown]
            consistency = 1 - (statistics.stdev(daily_commits) / statistics.mean(daily_commits)) if statistics.mean(daily_commits) > 0 else 0
            consistency_score = max(0, consistency * 20)
        else:
            consistency_score = 0
        
        # Factor 4: Work-life balance (0-15 points)
        work_patterns = time_tracking.get('work_patterns', {})
        late_night_pct = work_patterns.get('late_night_percentage', 0)
        weekend_pct = work_patterns.get('weekend_percentage', 0)
        balance_score = 15 - (late_night_pct * 0.2) - (weekend_pct * 0.15)
        balance_score = max(0, balance_score)
        
        # Factor 5: Task completion (0-10 points) if task data provided
        task_score = 0
        if tasks_data:
            completed = tasks_data.get('completed', 0)
            total = tasks_data.get('total', 1)
            task_score = (completed / total) * 10 if total > 0 else 0
        
        # Calculate total score
        total_score = commit_score + code_volume_score + consistency_score + balance_score + task_score
        
        # Normalize to 0-100
        normalized_score = min(100, total_score)
        
        return {
            'overall_score': round(normalized_score, 1),
            'grade': self._score_to_grade(normalized_score),
            'breakdown': {
                'commit_activity': round(commit_score, 1),
                'code_volume': round(code_volume_score, 1),
                'consistency': round(consistency_score, 1),
                'work_life_balance': round(balance_score, 1),
                'task_completion': round(task_score, 1)
            },
            'recommendations': self._generate_recommendations(normalized_score, {
                'commits': len(commits),
                'consistency': consistency_score,
                'balance': balance_score
            })
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
    
    def _generate_recommendations(self, score: float, metrics: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.append("📊 Overall productivity is low. Consider reviewing your workflow and eliminating blockers.")
        
        if metrics['commits'] < 10:
            recommendations.append("💡 Low commit frequency. Try breaking work into smaller, more frequent commits.")
        
        if metrics['consistency'] < 10:
            recommendations.append("📈 Work pattern is inconsistent. Establish a regular development routine.")
        
        if metrics['balance'] < 10:
            recommendations.append("⚖️ Work-life balance needs attention. Avoid late-night and weekend coding sessions.")
        
        if score >= 80:
            recommendations.append("🎉 Excellent productivity! Keep up the great work while maintaining balance.")
        
        return recommendations


class AISprintPlanner:
    """AI-powered sprint planning suggestions using Gemini"""
    
    def __init__(self):
        self.gemini_model = None
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def generate_sprint_plan(self, velocity_data: Dict, backlog: List[Dict],
                            team_capacity: int = 100) -> Dict:
        """Generate AI-powered sprint planning suggestions"""
        
        if not self.gemini_model:
            return {
                'success': False,
                'error': 'Gemini AI not available. Please configure GEMINI_API_KEY.'
            }
        
        try:
            # Prepare context for AI
            prompt = f"""
You are an expert Agile sprint planner. Based on the following data, suggest an optimal sprint plan:

**Team Velocity Data:**
- Average velocity: {velocity_data.get('average_velocity', 0)} story points
- Last 3 sprints: {velocity_data.get('recent_velocities', [])}
- Velocity trend: {velocity_data.get('trend', 'stable')}

**Team Capacity:** {team_capacity} hours available

**Backlog Items ({len(backlog)} total):**
{self._format_backlog(backlog[:15])}  # Limit to top 15

**Please provide:**
1. Recommended story points for this sprint
2. Which backlog items to include (by priority and estimated effort)
3. Risk assessment and mitigation strategies
4. Sprint goal suggestion
5. Capacity allocation recommendations

Format your response as a structured JSON with these keys:
- recommended_points
- selected_items (list of item IDs)
- sprint_goal
- risks
- recommendations
"""
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse AI response
            suggestion = self._parse_ai_response(response.text)
            
            return {
                'success': True,
                'ai_suggestion': suggestion,
                'velocity_context': velocity_data,
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating sprint plan: {str(e)}'
            }
    
    def _format_backlog(self, backlog: List[Dict]) -> str:
        """Format backlog items for AI prompt"""
        formatted = []
        for i, item in enumerate(backlog, 1):
            formatted.append(
                f"{i}. [{item.get('id', 'N/A')}] {item.get('title', 'Untitled')} "
                f"(Priority: {item.get('priority', 'medium')}, "
                f"Estimate: {item.get('story_points', 'TBD')} pts)"
            )
        return '\n'.join(formatted)
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Return raw text if JSON parsing fails
                return {
                    'raw_response': response_text,
                    'parsed': False
                }
        except Exception as e:
            return {
                'raw_response': response_text,
                'parsed': False,
                'error': str(e)
            }


class ProjectHealthDashboard:
    """Aggregate project health metrics"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.time_tracker = TimeTracker()
        self.burnout_predictor = BurnoutPredictor()
        self.quality_trends = CodeQualityTrends(db_path)
        self.productivity_scorer = ProductivityScorer()
    
    def get_project_health(self, days: int = 30, repo_path: str = ".") -> Dict:
        """Get comprehensive project health dashboard"""
        
        # Get commit data
        commits = self.time_tracker.get_commit_history(days=days)
        time_tracking = self.time_tracker.calculate_time_tracking(commits)
        
        # Burnout analysis
        burnout_risk = self.burnout_predictor.analyze_burnout_risk(time_tracking, commits)
        
        # Quality trends
        quality = self.quality_trends.get_quality_trends(days=days)
        
        # Productivity score
        productivity = self.productivity_scorer.calculate_productivity_score(time_tracking, commits)
        
        # Calculate overall health score
        health_score = self._calculate_health_score(burnout_risk, quality, productivity)
        
        return {
            'overall_health_score': health_score,
            'time_tracking': time_tracking,
            'burnout_risk': burnout_risk,
            'code_quality': quality,
            'productivity': productivity,
            'summary': self._generate_summary(health_score, burnout_risk, quality, productivity),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_health_score(self, burnout: Dict, quality: Dict, productivity: Dict) -> Dict:
        """Calculate overall project health score"""
        
        # Invert burnout risk (lower is better)
        burnout_component = 100 - burnout.get('risk_score', 50)
        
        # Quality component (based on trends)
        quality_summary = quality.get('summary', {})
        if quality_summary.get('overall_health') == 'good':
            quality_component = 80
        else:
            quality_component = 50
        
        # Productivity component
        productivity_component = productivity.get('overall_score', 60)
        
        # Weighted average
        overall = (burnout_component * 0.3 + quality_component * 0.3 + productivity_component * 0.4)
        
        return {
            'score': round(overall, 1),
            'rating': 'excellent' if overall >= 80 else 'good' if overall >= 60 else 'needs_attention',
            'components': {
                'team_wellbeing': round(burnout_component, 1),
                'code_quality': round(quality_component, 1),
                'productivity': round(productivity_component, 1)
            }
        }
    
    def _generate_summary(self, health_score: Dict, burnout: Dict,
                         quality: Dict, productivity: Dict) -> str:
        """Generate executive summary"""
        rating = health_score['rating']
        
        if rating == 'excellent':
            return "🎉 Project health is excellent! Team is productive, code quality is high, and work-life balance is maintained."
        elif rating == 'good':
            return "✅ Project health is good overall. Review specific metrics for areas of improvement."
        else:
            return "⚠️ Project health needs attention. Focus on burnout prevention, code quality, and sustainable productivity."


# Export all classes
__all__ = [
    'TimeTracker',
    'BurnoutPredictor',
    'CodeQualityTrends',
    'ProductivityScorer',
    'AISprintPlanner',
    'ProjectHealthDashboard'
]
