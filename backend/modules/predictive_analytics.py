"""
Predictive Analytics Dashboard
DORA metrics, project forecasting, and developer productivity insights
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics


class MetricType(Enum):
    """Types of metrics"""
    DORA = "dora"
    PRODUCTIVITY = "productivity"
    QUALITY = "quality"
    VELOCITY = "velocity"
    TECHNICAL_DEBT = "technical_debt"


@dataclass
class Deployment:
    """Deployment record"""
    id: str
    timestamp: datetime
    success: bool
    duration_minutes: float
    environment: str
    commit_count: int


@dataclass
class Incident:
    """Incident/failure record"""
    id: str
    timestamp: datetime
    resolved_at: Optional[datetime]
    severity: str
    related_deployment: Optional[str]


class DORAMetrics:
    """Calculate DORA (DevOps Research and Assessment) metrics"""
    
    def __init__(self):
        self.deployments: List[Deployment] = []
        self.incidents: List[Incident] = []
    
    def add_deployment(self, deployment: Deployment):
        """Add deployment record"""
        self.deployments.append(deployment)
    
    def add_incident(self, incident: Incident):
        """Add incident record"""
        self.incidents.append(incident)
    
    def calculate_deployment_frequency(self, days: int = 30) -> Dict:
        """Calculate deployment frequency"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_deployments = [d for d in self.deployments if d.timestamp >= cutoff]
        
        if not recent_deployments:
            return {
                'deployments_per_day': 0,
                'total_deployments': 0,
                'rating': 'low',
                'trend': 'stable'
            }
        
        deployments_per_day = len(recent_deployments) / days
        
        # Rating based on DORA research
        if deployments_per_day >= 1:
            rating = 'elite'
        elif deployments_per_day >= 0.14:  # Weekly
            rating = 'high'
        elif deployments_per_day >= 0.03:  # Monthly
            rating = 'medium'
        else:
            rating = 'low'
        
        return {
            'deployments_per_day': deployments_per_day,
            'total_deployments': len(recent_deployments),
            'rating': rating,
            'period_days': days,
            'trend': self._calculate_trend(recent_deployments)
        }
    
    def calculate_lead_time(self, days: int = 30) -> Dict:
        """Calculate lead time for changes"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_deployments = [d for d in self.deployments if d.timestamp >= cutoff]
        
        if not recent_deployments:
            return {
                'average_hours': 0,
                'median_hours': 0,
                'rating': 'low'
            }
        
        # In a real system, we'd calculate time from commit to deployment
        # For now, using deployment duration as proxy
        durations = [d.duration_minutes / 60 for d in recent_deployments]
        
        avg_hours = statistics.mean(durations)
        median_hours = statistics.median(durations)
        
        # Rating based on DORA research
        if avg_hours <= 24:
            rating = 'elite'
        elif avg_hours <= 168:  # 1 week
            rating = 'high'
        elif avg_hours <= 720:  # 1 month
            rating = 'medium'
        else:
            rating = 'low'
        
        return {
            'average_hours': avg_hours,
            'median_hours': median_hours,
            'rating': rating,
            'percentile_90': self._percentile(durations, 90) if durations else 0
        }
    
    def calculate_mttr(self, days: int = 30) -> Dict:
        """Calculate Mean Time to Recovery"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_incidents = [i for i in self.incidents 
                           if i.timestamp >= cutoff and i.resolved_at]
        
        if not recent_incidents:
            return {
                'average_hours': 0,
                'median_hours': 0,
                'rating': 'unknown',
                'total_incidents': 0
            }
        
        recovery_times = [
            (i.resolved_at - i.timestamp).total_seconds() / 3600
            for i in recent_incidents
        ]
        
        avg_hours = statistics.mean(recovery_times)
        median_hours = statistics.median(recovery_times)
        
        # Rating based on DORA research
        if avg_hours <= 1:
            rating = 'elite'
        elif avg_hours <= 24:
            rating = 'high'
        elif avg_hours <= 168:  # 1 week
            rating = 'medium'
        else:
            rating = 'low'
        
        return {
            'average_hours': avg_hours,
            'median_hours': median_hours,
            'rating': rating,
            'total_incidents': len(recent_incidents)
        }
    
    def calculate_change_failure_rate(self, days: int = 30) -> Dict:
        """Calculate change failure rate"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_deployments = [d for d in self.deployments if d.timestamp >= cutoff]
        
        if not recent_deployments:
            return {
                'failure_rate': 0,
                'rating': 'unknown',
                'total_deployments': 0,
                'failed_deployments': 0
            }
        
        failed = sum(1 for d in recent_deployments if not d.success)
        failure_rate = (failed / len(recent_deployments)) * 100
        
        # Rating based on DORA research
        if failure_rate <= 15:
            rating = 'elite'
        elif failure_rate <= 20:
            rating = 'high'
        elif failure_rate <= 30:
            rating = 'medium'
        else:
            rating = 'low'
        
        return {
            'failure_rate': failure_rate,
            'rating': rating,
            'total_deployments': len(recent_deployments),
            'failed_deployments': failed
        }
    
    def get_dora_summary(self, days: int = 30) -> Dict:
        """Get complete DORA metrics summary"""
        return {
            'deployment_frequency': self.calculate_deployment_frequency(days),
            'lead_time': self.calculate_lead_time(days),
            'mttr': self.calculate_mttr(days),
            'change_failure_rate': self.calculate_change_failure_rate(days),
            'overall_rating': self._calculate_overall_rating(days),
            'period_days': days,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_overall_rating(self, days: int) -> str:
        """Calculate overall DORA rating"""
        ratings = [
            self.calculate_deployment_frequency(days)['rating'],
            self.calculate_lead_time(days)['rating'],
            self.calculate_mttr(days)['rating'],
            self.calculate_change_failure_rate(days)['rating']
        ]
        
        rating_scores = {'elite': 4, 'high': 3, 'medium': 2, 'low': 1, 'unknown': 0}
        avg_score = statistics.mean([rating_scores.get(r, 0) for r in ratings if r != 'unknown'])
        
        if avg_score >= 3.5:
            return 'elite'
        elif avg_score >= 2.5:
            return 'high'
        elif avg_score >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_trend(self, deployments: List[Deployment]) -> str:
        """Calculate deployment trend"""
        if len(deployments) < 7:
            return 'stable'
        
        # Split into two halves and compare
        mid = len(deployments) // 2
        first_half = deployments[:mid]
        second_half = deployments[mid:]
        
        if len(second_half) > len(first_half) * 1.2:
            return 'increasing'
        elif len(second_half) < len(first_half) * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]


class VelocityTracker:
    """Track team velocity and predict completion dates"""
    
    def __init__(self):
        self.sprints: List[Dict] = []
        self.tasks: List[Dict] = []
    
    def add_sprint(self, sprint: Dict):
        """Add sprint data"""
        self.sprints.append({
            'id': sprint['id'],
            'points_planned': sprint.get('points_planned', 0),
            'points_completed': sprint.get('points_completed', 0),
            'start_date': sprint['start_date'],
            'end_date': sprint['end_date'],
            'team_size': sprint.get('team_size', 1)
        })
    
    def calculate_velocity(self, last_n_sprints: int = 3) -> Dict:
        """Calculate team velocity"""
        recent_sprints = self.sprints[-last_n_sprints:]
        
        if not recent_sprints:
            return {
                'average_velocity': 0,
                'trend': 'unknown',
                'consistency': 0
            }
        
        velocities = [s['points_completed'] for s in recent_sprints]
        avg_velocity = statistics.mean(velocities)
        std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
        
        # Calculate consistency (lower std dev = more consistent)
        consistency = max(0, 100 - (std_dev / avg_velocity * 100)) if avg_velocity > 0 else 0
        
        return {
            'average_velocity': avg_velocity,
            'median_velocity': statistics.median(velocities),
            'std_deviation': std_dev,
            'consistency': consistency,
            'trend': self._velocity_trend(velocities),
            'sprints_analyzed': len(recent_sprints)
        }
    
    def predict_completion(self, remaining_points: int, 
                          confidence_level: float = 0.8) -> Dict:
        """Predict project completion date"""
        velocity_data = self.calculate_velocity()
        avg_velocity = velocity_data['average_velocity']
        
        if avg_velocity == 0:
            return {
                'error': 'Insufficient velocity data',
                'estimated_sprints': None
            }
        
        # Calculate sprints needed
        estimated_sprints = remaining_points / avg_velocity
        
        # Add buffer based on consistency
        consistency = velocity_data['consistency']
        buffer_factor = 1.0 + ((100 - consistency) / 100 * 0.5)
        
        conservative_sprints = estimated_sprints * buffer_factor
        
        # Calculate dates (assuming 2-week sprints)
        sprint_duration_days = 14
        estimated_days = int(conservative_sprints * sprint_duration_days)
        estimated_completion = datetime.now() + timedelta(days=estimated_days)
        
        return {
            'remaining_points': remaining_points,
            'estimated_sprints': conservative_sprints,
            'estimated_completion_date': estimated_completion.isoformat(),
            'confidence_level': confidence_level,
            'assumptions': {
                'average_velocity': avg_velocity,
                'sprint_duration_days': sprint_duration_days,
                'buffer_factor': buffer_factor
            }
        }
    
    def identify_bottlenecks(self) -> List[Dict]:
        """Identify workflow bottlenecks"""
        bottlenecks = []
        
        recent_sprints = self.sprints[-5:]
        
        for sprint in recent_sprints:
            completion_rate = (sprint['points_completed'] / sprint['points_planned'] * 100
                             if sprint['points_planned'] > 0 else 0)
            
            if completion_rate < 70:
                bottlenecks.append({
                    'sprint_id': sprint['id'],
                    'completion_rate': completion_rate,
                    'points_missed': sprint['points_planned'] - sprint['points_completed'],
                    'severity': 'high' if completion_rate < 50 else 'medium'
                })
        
        return bottlenecks
    
    def _velocity_trend(self, velocities: List[float]) -> str:
        """Calculate velocity trend"""
        if len(velocities) < 2:
            return 'stable'
        
        # Simple linear trend
        first_half_avg = statistics.mean(velocities[:len(velocities)//2])
        second_half_avg = statistics.mean(velocities[len(velocities)//2:])
        
        if second_half_avg > first_half_avg * 1.1:
            return 'increasing'
        elif second_half_avg < first_half_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'


class TechnicalDebtAnalyzer:
    """Analyze and quantify technical debt"""
    
    def __init__(self):
        self.debt_items: List[Dict] = []
        self.code_metrics: Dict = {}
    
    def add_debt_item(self, item: Dict):
        """Add technical debt item"""
        self.debt_items.append({
            'id': item['id'],
            'type': item.get('type', 'code_smell'),
            'severity': item.get('severity', 'medium'),
            'effort_hours': item.get('effort_hours', 0),
            'interest_rate': item.get('interest_rate', 0.1),  # Cost increase per sprint
            'created_at': item.get('created_at', datetime.now())
        })
    
    def calculate_total_debt(self) -> Dict:
        """Calculate total technical debt"""
        total_effort = sum(item['effort_hours'] for item in self.debt_items)
        
        # Calculate by severity
        by_severity = defaultdict(float)
        for item in self.debt_items:
            by_severity[item['severity']] += item['effort_hours']
        
        # Calculate by type
        by_type = defaultdict(float)
        for item in self.debt_items:
            by_type[item['type']] += item['effort_hours']
        
        return {
            'total_hours': total_effort,
            'total_days': total_effort / 8,
            'by_severity': dict(by_severity),
            'by_type': dict(by_type),
            'item_count': len(self.debt_items),
            'high_priority_items': len([i for i in self.debt_items if i['severity'] == 'high'])
        }
    
    def calculate_interest(self, sprints_passed: int = 1) -> float:
        """Calculate accumulated interest on technical debt"""
        total_interest = 0
        
        for item in self.debt_items:
            base_cost = item['effort_hours']
            interest_rate = item['interest_rate']
            accumulated_interest = base_cost * interest_rate * sprints_passed
            total_interest += accumulated_interest
        
        return total_interest
    
    def prioritize_debt(self) -> List[Dict]:
        """Prioritize technical debt items"""
        # Score based on severity and age
        severity_weights = {'critical': 10, 'high': 5, 'medium': 3, 'low': 1}
        
        scored_items = []
        for item in self.debt_items:
            age_days = (datetime.now() - item['created_at']).days
            severity_score = severity_weights.get(item['severity'], 1)
            
            # Priority score considers severity, age, and effort
            priority_score = (severity_score * 10) + (age_days * 0.1) - (item['effort_hours'] * 0.5)
            
            scored_items.append({
                **item,
                'priority_score': priority_score,
                'age_days': age_days
            })
        
        # Sort by priority score (descending)
        return sorted(scored_items, key=lambda x: x['priority_score'], reverse=True)
    
    def forecast_debt_growth(self, months: int = 6) -> Dict:
        """Forecast technical debt growth"""
        current_debt = self.calculate_total_debt()['total_hours']
        
        # Assume debt grows at 5% per month if not addressed
        monthly_growth_rate = 0.05
        projected_debt = current_debt * ((1 + monthly_growth_rate) ** months)
        
        return {
            'current_debt_hours': current_debt,
            'projected_debt_hours': projected_debt,
            'increase_hours': projected_debt - current_debt,
            'increase_percentage': ((projected_debt - current_debt) / current_debt * 100
                                   if current_debt > 0 else 0),
            'forecast_months': months,
            'monthly_growth_rate': monthly_growth_rate * 100
        }


class ProductivityAnalyzer:
    """Analyze developer productivity"""
    
    def __init__(self):
        self.activities: List[Dict] = []
        self.code_contributions: List[Dict] = []
    
    def track_activity(self, activity: Dict):
        """Track developer activity"""
        self.activities.append({
            'user': activity['user'],
            'type': activity['type'],  # commit, review, issue, etc.
            'timestamp': activity.get('timestamp', datetime.now()),
            'value': activity.get('value', 1)  # lines changed, files, etc.
        })
    
    def calculate_productivity_score(self, user: str, days: int = 30) -> Dict:
        """Calculate productivity score for a developer"""
        cutoff = datetime.now() - timedelta(days=days)
        user_activities = [a for a in self.activities 
                          if a['user'] == user and a['timestamp'] >= cutoff]
        
        if not user_activities:
            return {
                'score': 0,
                'rating': 'unknown',
                'activities': {}
            }
        
        # Count activities by type
        activity_counts = defaultdict(int)
        for activity in user_activities:
            activity_counts[activity['type']] += activity['value']
        
        # Calculate score (weighted)
        weights = {
            'commit': 2,
            'review': 3,
            'issue_closed': 5,
            'documentation': 1,
            'test': 2
        }
        
        score = sum(activity_counts[act_type] * weights.get(act_type, 1)
                   for act_type in activity_counts)
        
        # Normalize to 0-100 scale
        normalized_score = min(100, (score / days) * 10)
        
        return {
            'score': normalized_score,
            'rating': self._score_to_rating(normalized_score),
            'activities': dict(activity_counts),
            'total_activities': len(user_activities),
            'period_days': days
        }
    
    def identify_patterns(self, user: str) -> Dict:
        """Identify productivity patterns"""
        user_activities = [a for a in self.activities if a['user'] == user]
        
        if not user_activities:
            return {'patterns': []}
        
        # Analyze timing patterns
        hours = [a['timestamp'].hour for a in user_activities]
        peak_hours = self._find_peak_hours(hours)
        
        # Analyze day-of-week patterns
        days = [a['timestamp'].weekday() for a in user_activities]
        productive_days = self._find_productive_days(days)
        
        return {
            'peak_hours': peak_hours,
            'productive_days': productive_days,
            'patterns': [
                f'Most active during {peak_hours}',
                f'Most productive on {productive_days}'
            ]
        }
    
    def _score_to_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'average'
        else:
            return 'needs_improvement'
    
    def _find_peak_hours(self, hours: List[int]) -> str:
        """Find peak productivity hours"""
        if not hours:
            return 'unknown'
        
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        if 9 <= peak_hour <= 12:
            return 'morning'
        elif 13 <= peak_hour <= 17:
            return 'afternoon'
        elif 18 <= peak_hour <= 22:
            return 'evening'
        else:
            return 'night'
    
    def _find_productive_days(self, days: List[int]) -> str:
        """Find most productive days"""
        if not days:
            return 'unknown'
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = defaultdict(int)
        
        for day in days:
            day_counts[day] += 1
        
        most_productive_day = max(day_counts.items(), key=lambda x: x[1])[0]
        return day_names[most_productive_day]


class PredictiveAnalyticsDashboard:
    """Main predictive analytics system"""
    
    def __init__(self):
        self.dora_metrics = DORAMetrics()
        self.velocity_tracker = VelocityTracker()
        self.debt_analyzer = TechnicalDebtAnalyzer()
        self.productivity_analyzer = ProductivityAnalyzer()
    
    def get_comprehensive_dashboard(self, days: int = 30) -> Dict:
        """Get comprehensive analytics dashboard"""
        return {
            'dora_metrics': self.dora_metrics.get_dora_summary(days),
            'velocity': self.velocity_tracker.calculate_velocity(),
            'technical_debt': self.debt_analyzer.calculate_total_debt(),
            'bottlenecks': self.velocity_tracker.identify_bottlenecks(),
            'debt_priorities': self.debt_analyzer.prioritize_debt()[:5],
            'generated_at': datetime.now().isoformat(),
            'period_days': days
        }
    
    def get_project_forecast(self, remaining_points: int) -> Dict:
        """Get project completion forecast"""
        completion_forecast = self.velocity_tracker.predict_completion(remaining_points)
        debt_forecast = self.debt_analyzer.forecast_debt_growth()
        
        return {
            'completion': completion_forecast,
            'technical_debt': debt_forecast,
            'risks': self._assess_risks(completion_forecast, debt_forecast)
        }
    
    def get_team_insights(self, team_members: List[str]) -> Dict:
        """Get team productivity insights"""
        team_scores = {}
        team_patterns = {}
        
        for member in team_members:
            team_scores[member] = self.productivity_analyzer.calculate_productivity_score(member)
            team_patterns[member] = self.productivity_analyzer.identify_patterns(member)
        
        return {
            'individual_scores': team_scores,
            'patterns': team_patterns,
            'team_average': statistics.mean([s['score'] for s in team_scores.values()]) 
                          if team_scores else 0
        }
    
    def _assess_risks(self, completion: Dict, debt: Dict) -> List[Dict]:
        """Assess project risks"""
        risks = []
        
        # Check if debt is growing faster than progress
        if debt.get('increase_percentage', 0) > 20:
            risks.append({
                'type': 'technical_debt',
                'severity': 'high',
                'message': 'Technical debt growing rapidly',
                'recommendation': 'Allocate time for debt reduction'
            })
        
        # Check velocity consistency
        if completion.get('assumptions', {}).get('buffer_factor', 1) > 1.3:
            risks.append({
                'type': 'velocity_inconsistent',
                'severity': 'medium',
                'message': 'Team velocity is inconsistent',
                'recommendation': 'Review sprint planning and capacity'
            })
        
        return risks
