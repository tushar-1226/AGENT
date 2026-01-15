"""
Learning Path Generator
Personalized education and skill development
"""
from typing import Dict, List, Optional
from datetime import datetime
import json

class LearningEngine:
    def __init__(self):
        self.learning_paths = {}
        self.user_progress = {}
    
    def assess_skill_level(self, topic: str, answers: List[Dict]) -> Dict:
        """Assess user's current skill level"""
        correct = sum(1 for a in answers if a.get('correct', False))
        total = len(answers)
        
        percentage = (correct / total * 100) if total > 0 else 0
        
        if percentage >= 80:
            level = 'advanced'
        elif percentage >= 50:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        return {
            'topic': topic,
            'level': level,
            'score': percentage,
            'correct': correct,
            'total': total
        }
    
    def generate_learning_path(self, topic: str, current_level: str = 'beginner', goal: str = 'advanced') -> Dict:
        """Generate personalized learning path"""
        
        # Predefined learning paths for common topics
        paths = {
            'react': {
                'beginner': [
                    {'title': 'JavaScript Fundamentals', 'duration': '2 weeks', 'resources': ['MDN Web Docs', 'JavaScript.info']},
                    {'title': 'React Basics', 'duration': '1 week', 'resources': ['Official React Tutorial', 'React Docs']},
                    {'title': 'Components & Props', 'duration': '1 week', 'resources': ['React Components Guide']},
                    {'title': 'State & Lifecycle', 'duration': '1 week', 'resources': ['State Management Guide']}
                ],
                'intermediate': [
                    {'title': 'Hooks Deep Dive', 'duration': '2 weeks', 'resources': ['Hooks API Reference']},
                    {'title': 'Context API', 'duration': '1 week', 'resources': ['Context Guide']},
                    {'title': 'React Router', 'duration': '1 week', 'resources': ['React Router Docs']},
                    {'title': 'Performance Optimization', 'duration': '1 week', 'resources': ['React Performance']}
                ],
                'advanced': [
                    {'title': 'Advanced Patterns', 'duration': '2 weeks', 'resources': ['React Patterns']},
                    {'title': 'Server Components', 'duration': '2 weeks', 'resources': ['Next.js Docs']},
                    {'title': 'Testing', 'duration': '1 week', 'resources': ['Testing Library']},
                    {'title': 'Production Deployment', 'duration': '1 week', 'resources': ['Deployment Guide']}
                ]
            },
            'python': {
                'beginner': [
                    {'title': 'Python Syntax', 'duration': '1 week', 'resources': ['Python.org Tutorial']},
                    {'title': 'Data Types & Structures', 'duration': '1 week', 'resources': ['Python Data Structures']},
                    {'title': 'Functions & Modules', 'duration': '1 week', 'resources': ['Python Functions']},
                    {'title': 'File I/O', 'duration': '1 week', 'resources': ['File Handling']}
                ],
                'intermediate': [
                    {'title': 'OOP in Python', 'duration': '2 weeks', 'resources': ['Python OOP']},
                    {'title': 'Error Handling', 'duration': '1 week', 'resources': ['Exception Handling']},
                    {'title': 'Decorators & Generators', 'duration': '1 week', 'resources': ['Advanced Python']},
                    {'title': 'Working with APIs', 'duration': '1 week', 'resources': ['Requests Library']}
                ],
                'advanced': [
                    {'title': 'Async Programming', 'duration': '2 weeks', 'resources': ['Asyncio Guide']},
                    {'title': 'Metaprogramming', 'duration': '2 weeks', 'resources': ['Python Metaclasses']},
                    {'title': 'Performance Optimization', 'duration': '1 week', 'resources': ['Python Performance']},
                    {'title': 'Testing & CI/CD', 'duration': '1 week', 'resources': ['Pytest Guide']}
                ]
            }
        }
        
        # Get path for topic
        topic_paths = paths.get(topic.lower(), {})
        
        # Build complete path from current level to goal
        levels = ['beginner', 'intermediate', 'advanced']
        start_idx = levels.index(current_level)
        end_idx = levels.index(goal)
        
        complete_path = []
        for i in range(start_idx, end_idx + 1):
            level = levels[i]
            if level in topic_paths:
                complete_path.extend(topic_paths[level])
        
        return {
            'topic': topic,
            'current_level': current_level,
            'goal_level': goal,
            'total_modules': len(complete_path),
            'estimated_duration': f"{sum(int(m['duration'].split()[0]) for m in complete_path)} weeks",
            'modules': complete_path
        }
    
    def generate_quiz(self, topic: str, level: str = 'beginner', count: int = 5) -> List[Dict]:
        """Generate quiz questions"""
        
        # Sample questions (in production, use Gemini to generate)
        questions = {
            'react': {
                'beginner': [
                    {'question': 'What is JSX?', 'options': ['JavaScript XML', 'Java Syntax Extension', 'JSON XML', 'JavaScript Extension'], 'correct': 0},
                    {'question': 'What hook is used for state?', 'options': ['useEffect', 'useState', 'useContext', 'useRef'], 'correct': 1},
                    {'question': 'How do you pass data to child components?', 'options': ['State', 'Props', 'Context', 'Redux'], 'correct': 1}
                ]
            },
            'python': {
                'beginner': [
                    {'question': 'What is the correct way to create a list?', 'options': ['list = ()', 'list = []', 'list = {}', 'list = <>'], 'correct': 1},
                    {'question': 'Which keyword is used for functions?', 'options': ['func', 'def', 'function', 'define'], 'correct': 1},
                    {'question': 'What is the output of print(type([]))?', 'options': ['<class \'list\'>', '<class \'array\'>', '<class \'tuple\'>', '<class \'dict\'>'], 'correct': 0}
                ]
            }
        }
        
        topic_questions = questions.get(topic.lower(), {}).get(level, [])
        return topic_questions[:count]
    
    def track_progress(self, user_id: str, topic: str, module: str, completed: bool = True) -> Dict:
        """Track learning progress"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if topic not in self.user_progress[user_id]:
            self.user_progress[user_id][topic] = {
                'modules_completed': [],
                'started_at': datetime.now().isoformat()
            }
        
        if completed and module not in self.user_progress[user_id][topic]['modules_completed']:
            self.user_progress[user_id][topic]['modules_completed'].append(module)
        
        return self.user_progress[user_id][topic]
    
    def get_recommendations(self, user_id: str) -> List[Dict]:
        """Get personalized recommendations"""
        if user_id not in self.user_progress:
            return [
                {'topic': 'React', 'reason': 'Popular frontend framework'},
                {'topic': 'Python', 'reason': 'Versatile programming language'},
                {'topic': 'TypeScript', 'reason': 'Type-safe JavaScript'}
            ]
        
        # Analyze progress and recommend next steps
        progress = self.user_progress[user_id]
        recommendations = []
        
        for topic, data in progress.items():
            completed_count = len(data['modules_completed'])
            if completed_count > 0:
                recommendations.append({
                    'topic': topic,
                    'reason': f'Continue learning - {completed_count} modules completed',
                    'next_module': f'Module {completed_count + 1}'
                })
        
        return recommendations
