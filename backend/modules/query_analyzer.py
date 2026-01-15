"""
Query Complexity Analyzer
Analyzes query complexity to determine optimal routing (local vs cloud)
"""
import re
from typing import Literal

ComplexityLevel = Literal['simple', 'medium', 'complex']


class QueryAnalyzer:
    """Analyzes query complexity for intelligent routing"""
    
    # Keywords that indicate simple queries
    SIMPLE_KEYWORDS = [
        'hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye',
        'what is', 'who is', 'when is', 'where is',
        'define', 'meaning of', 'explain briefly'
    ]
    
    # Keywords that indicate complex queries
    COMPLEX_KEYWORDS = [
        'generate', 'create', 'build', 'develop', 'implement',
        'analyze in detail', 'comprehensive', 'step by step',
        'write a', 'design', 'architect', 'refactor',
        'optimize', 'debug complex', 'multi-step'
    ]
    
    # Code-related keywords (medium complexity, good for local coding models)
    CODE_KEYWORDS = [
        'code', 'function', 'class', 'method', 'variable',
        'bug', 'error', 'debug', 'fix', 'syntax',
        'python', 'javascript', 'typescript', 'java', 'c++',
        'react', 'node', 'django', 'flask'
    ]
    
    def __init__(self):
        self.stats = {
            'simple': 0,
            'medium': 0,
            'complex': 0
        }
    
    def analyze_complexity(self, query: str) -> ComplexityLevel:
        """
        Analyze query complexity
        
        Args:
            query: User query string
            
        Returns:
            'simple', 'medium', or 'complex'
        """
        query_lower = query.lower().strip()
        
        # Check for simple patterns
        if self._is_simple_query(query_lower):
            self.stats['simple'] += 1
            return 'simple'
        
        # Check for complex patterns
        if self._is_complex_query(query_lower):
            self.stats['complex'] += 1
            return 'complex'
        
        # Default to medium
        self.stats['medium'] += 1
        return 'medium'
    
    def _is_simple_query(self, query: str) -> bool:
        """Check if query is simple"""
        # Very short queries
        if len(query) < 20:
            return True
        
        # Starts with simple keywords
        for keyword in self.SIMPLE_KEYWORDS:
            if query.startswith(keyword):
                return True
        
        # Simple greetings or thanks
        if query in ['hi', 'hello', 'hey', 'thanks', 'thank you', 'ok', 'okay']:
            return True
        
        return False
    
    def _is_complex_query(self, query: str) -> bool:
        """Check if query is complex"""
        # Very long queries
        if len(query) > 200:
            return True
        
        # Contains complex keywords
        for keyword in self.COMPLEX_KEYWORDS:
            if keyword in query:
                return True
        
        # Multiple sentences (likely complex)
        if query.count('.') > 2 or query.count('?') > 1:
            return True
        
        # Asks for code generation (large blocks)
        if re.search(r'write (a|an|the)? ?(complete|full|entire)? ?(class|component|function|program|script)', query):
            return True
        
        return False
    
    def is_code_related(self, query: str) -> bool:
        """Check if query is code-related (good for local coding models)"""
        query_lower = query.lower()
        
        for keyword in self.CODE_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # Check for code patterns
        if re.search(r'[{}\[\]();]', query):  # Contains code syntax
            return True
        
        return False
    
    def get_stats(self) -> dict:
        """Get usage statistics"""
        total = sum(self.stats.values())
        if total == 0:
            return self.stats
        
        return {
            'simple': self.stats['simple'],
            'medium': self.stats['medium'],
            'complex': self.stats['complex'],
            'total': total,
            'simple_percentage': round(self.stats['simple'] / total * 100, 1),
            'medium_percentage': round(self.stats['medium'] / total * 100, 1),
            'complex_percentage': round(self.stats['complex'] / total * 100, 1)
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'simple': 0,
            'medium': 0,
            'complex': 0
        }
