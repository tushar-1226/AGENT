"""
Performance Profiler & Optimization Engine
Real-time performance monitoring and automatic optimization
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import time
import ast


class PerformanceIssueType(Enum):
    """Types of performance issues"""
    MEMORY_LEAK = "memory_leak"
    N_PLUS_ONE_QUERY = "n_plus_one_query"
    INEFFICIENT_LOOP = "inefficient_loop"
    BLOCKING_IO = "blocking_io"
    LARGE_BUNDLE = "large_bundle"
    UNOPTIMIZED_IMAGE = "unoptimized_image"
    SYNCHRONOUS_OPERATION = "synchronous_operation"
    REDUNDANT_COMPUTATION = "redundant_computation"


@dataclass
class PerformanceIssue:
    """Performance issue"""
    id: str
    type: PerformanceIssueType
    severity: str
    description: str
    file_path: str
    line_number: int
    impact: str
    suggestion: str
    estimated_improvement: str
    detected_at: str = ""
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()


class CodePerformanceAnalyzer:
    """Analyze code for performance issues"""
    
    def __init__(self):
        self.performance_patterns = {
            'n_plus_one': [
                r'for.*in.*:.*\.query\(',
                r'for.*in.*:.*\.get\(',
            ],
            'inefficient_loop': [
                r'for.*in.*:.*\.append\(.*\[.*\]',
            ],
            'blocking_io': [
                r'requests\.get\(',
                r'urllib\.request',
            ],
        }
    
    def analyze_python_code(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Analyze Python code for performance issues"""
        issues = []
        
        try:
            tree = ast.parse(code)
            issues.extend(self._analyze_ast(tree, file_path))
        except:
            pass
        
        return issues
    
    def _analyze_ast(self, tree: ast.AST, file_path: str) -> List[PerformanceIssue]:
        """Analyze AST for performance issues"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for N+1 queries
            if isinstance(node, ast.For):
                # Check if there's a database call in the loop
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr in ['query', 'get', 'filter']:
                                issues.append(PerformanceIssue(
                                    id=f"perf_{node.lineno}",
                                    type=PerformanceIssueType.N_PLUS_ONE_QUERY,
                                    severity="high",
                                    description="Potential N+1 query in loop",
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    impact="Can cause severe performance degradation with large datasets",
                                    suggestion="Use batch queries or eager loading",
                                    estimated_improvement="10-100x faster"
                                ))
            
            # Check for list concatenation in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node.body[0] if node.body else node):
                    if isinstance(child, ast.AugAssign):
                        if isinstance(child.op, ast.Add):
                            issues.append(PerformanceIssue(
                                id=f"perf_{node.lineno}",
                                type=PerformanceIssueType.INEFFICIENT_LOOP,
                                severity="medium",
                                description="List concatenation in loop",
                                file_path=file_path,
                                line_number=node.lineno,
                                impact="O(n²) complexity instead of O(n)",
                                suggestion="Use list.append() or list comprehension",
                                estimated_improvement="10x faster for large lists"
                            ))
        
        return issues
    
    def suggest_optimizations(self, code: str) -> List[Dict]:
        """Suggest code optimizations"""
        suggestions = []
        
        # Check for list comprehension opportunities
        if 'for' in code and '.append(' in code:
            suggestions.append({
                'type': 'list_comprehension',
                'description': 'Use list comprehension instead of append in loop',
                'before': 'result = []\nfor x in items:\n    result.append(x*2)',
                'after': 'result = [x*2 for x in items]',
                'improvement': '20-30% faster'
            })
        
        # Check for generator opportunities
        if 'return [' in code:
            suggestions.append({
                'type': 'generator',
                'description': 'Use generator for memory efficiency',
                'before': 'return [process(x) for x in large_list]',
                'after': 'return (process(x) for x in large_list)',
                'improvement': 'Reduces memory usage significantly'
            })
        
        return suggestions


class RuntimeProfiler:
    """Profile code execution at runtime"""
    
    def __init__(self):
        self.profiles = []
        self.active_timers = {}
    
    def start_profiling(self, label: str) -> str:
        """Start profiling a code section"""
        timer_id = f"{label}_{time.time()}"
        self.active_timers[timer_id] = {
            'label': label,
            'start_time': time.time(),
            'start_memory': self._get_memory_usage()
        }
        return timer_id
    
    def stop_profiling(self, timer_id: str) -> Dict:
        """Stop profiling and return results"""
        if timer_id not in self.active_timers:
            return {'error': 'Timer not found'}
        
        timer = self.active_timers[timer_id]
        duration = time.time() - timer['start_time']
        memory_delta = self._get_memory_usage() - timer['start_memory']
        
        profile = {
            'label': timer['label'],
            'duration_ms': duration * 1000,
            'memory_delta_mb': memory_delta,
            'timestamp': datetime.now().isoformat()
        }
        
        self.profiles.append(profile)
        del self.active_timers[timer_id]
        
        return profile
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0
    
    def get_performance_report(self) -> Dict:
        """Get performance profiling report"""
        if not self.profiles:
            return {'message': 'No profiling data available'}
        
        durations = [p['duration_ms'] for p in self.profiles]
        
        return {
            'total_profiles': len(self.profiles),
            'average_duration_ms': sum(durations) / len(durations),
            'slowest_operations': sorted(self.profiles, 
                                        key=lambda x: x['duration_ms'], 
                                        reverse=True)[:5],
            'generated_at': datetime.now().isoformat()
        }


class BundleOptimizer:
    """Optimize bundle sizes for web applications"""
    
    def __init__(self):
        self.bundle_analysis = {}
    
    def analyze_bundle(self, file_path: str, size_bytes: int) -> Dict:
        """Analyze bundle size"""
        size_mb = size_bytes / 1024 / 1024
        
        rating = 'excellent' if size_mb < 0.25 else \
                'good' if size_mb < 0.5 else \
                'fair' if size_mb < 1.0 else 'poor'
        
        suggestions = []
        
        if size_mb > 0.5:
            suggestions.append("Enable code splitting")
            suggestions.append("Use dynamic imports for large modules")
        
        if size_mb > 1.0:
            suggestions.append("Implement tree shaking")
            suggestions.append("Remove unused dependencies")
        
        return {
            'file_path': file_path,
            'size_mb': size_mb,
            'rating': rating,
            'suggestions': suggestions,
            'potential_savings': f"{size_mb * 0.3:.2f} MB" if size_mb > 0.5 else "0 MB"
        }


class PerformanceProfiler:
    """Main performance profiler"""
    
    def __init__(self):
        self.code_analyzer = CodePerformanceAnalyzer()
        self.runtime_profiler = RuntimeProfiler()
        self.bundle_optimizer = BundleOptimizer()
    
    def analyze_file(self, file_path: str, code: Optional[str] = None) -> Dict:
        """Comprehensive performance analysis"""
        if code is None:
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
            except:
                return {'error': 'Could not read file'}
        
        issues = []
        
        if file_path.endswith('.py'):
            issues = self.code_analyzer.analyze_python_code(code, file_path)
        
        optimizations = self.code_analyzer.suggest_optimizations(code)
        
        return {
            'file_path': file_path,
            'performance_issues': [asdict(issue) for issue in issues],
            'optimization_suggestions': optimizations,
            'performance_score': self._calculate_score(issues),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _calculate_score(self, issues: List[PerformanceIssue]) -> float:
        """Calculate performance score"""
        if not issues:
            return 100.0
        
        severity_weights = {'critical': 20, 'high': 10, 'medium': 5, 'low': 2}
        total_impact = sum(severity_weights.get(issue.severity, 1) for issue in issues)
        
        return max(0, 100 - total_impact)
