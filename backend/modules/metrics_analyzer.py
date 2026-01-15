"""
Metrics Analyzer - Code Metrics Dashboard
Analyze and visualize code complexity, coverage, and quality metrics
"""

import logging
import ast
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """Analyze code metrics for dashboard visualization"""
    
    def __init__(self):
        """Initialize metrics analyzer"""
        logger.info("Metrics Analyzer initialized")
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze entire project for metrics
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Complete metrics report
        """
        try:
            project_path = Path(project_path)
            
            metrics = {
                "overview": {},
                "files": [],
                "complexity": {},
                "quality": {},
                "languages": {},
                "trends": {}
            }
            
            # Scan Python files
            python_files = list(project_path.rglob("*.py"))
            
            total_lines = 0
            total_functions = 0
            total_classes = 0
            complexity_scores = []
            
            for file_path in python_files:
                if any(skip in file_path.parts for skip in ['venv', 'node_modules', '__pycache__']):
                    continue
                
                file_metrics = self.analyze_file(str(file_path))
                
                if "error" not in file_metrics:
                    metrics["files"].append(file_metrics)
                    total_lines += file_metrics["lines_of_code"]
                    total_functions += file_metrics["functions"]
                    total_classes += file_metrics["classes"]
                    complexity_scores.append(file_metrics["complexity"]["cyclomatic"])
            
            # Overview
            metrics["overview"] = {
                "total_files": len(metrics["files"]),
                "total_lines": total_lines,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "avg_complexity": sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
            }
            
            # Complexity distribution
            metrics["complexity"] = self._calculate_complexity_distribution(metrics["files"])
            
            # Quality score
            metrics["quality"] = self._calculate_quality_metrics(metrics["files"])
            
            # Language statistics
            metrics["languages"] = self._calculate_language_stats(project_path)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return {"error": str(e)}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze single file for metrics
        
        Args:
            file_path: Path to file
            
        Returns:
            File metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return {"error": "Syntax error in file"}
            
            metrics = {
                "file_path": file_path,
                "lines_of_code": len(content.splitlines()),
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "docstrings": 0,
                "comments": 0,
                "complexity": {},
                "maintainability_index": 0
            }
            
            # Count elements
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    if ast.get_docstring(node):
                        metrics["docstrings"] += 1
                
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                    if ast.get_docstring(node):
                        metrics["docstrings"] += 1
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics["imports"] += 1
            
            # Count comments
            import re
            metrics["comments"] = len(re.findall(r'#.*$', content, re.MULTILINE))
            
            # Calculate complexity
            metrics["complexity"] = self._calculate_complexity(tree)
            
            # Calculate maintainability index
            metrics["maintainability_index"] = self._calculate_maintainability_index(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {"error": str(e)}
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code complexity metrics"""
        
        complexity = {
            "cyclomatic": 1,
            "cognitive": 0,
            "max_depth": 0,
            "avg_function_length": 0
        }
        
        function_lengths = []
        
        for node in ast.walk(tree):
            # Cyclomatic complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity["cyclomatic"] += 1
            elif isinstance(node, ast.BoolOp):
                complexity["cyclomatic"] += len(node.values) - 1
            
            # Function lengths
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    func_length = node.end_lineno - node.lineno
                    function_lengths.append(func_length)
        
        if function_lengths:
            complexity["avg_function_length"] = sum(function_lengths) / len(function_lengths)
        
        return complexity
    
    def _calculate_maintainability_index(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate maintainability index (0-100)
        Higher is better
        """
        import math
        
        loc = metrics["lines_of_code"]
        if loc == 0:
            return 100.0
        
        cyclomatic = metrics["complexity"]["cyclomatic"]
        
        # Simplified maintainability index
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Where V = volume, G = cyclomatic complexity, LOC = lines of code
        
        volume = loc * math.log(loc + 1)
        mi = 171 - 5.2 * math.log(volume + 1) - 0.23 * cyclomatic - 16.2 * math.log(loc)
        
        # Normalize to 0-100
        mi = max(0, min(100, mi))
        
        return round(mi, 2)
    
    def _calculate_complexity_distribution(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate complexity distribution"""
        
        distribution = {
            "low": 0,      # 1-5
            "medium": 0,   # 6-10
            "high": 0,     # 11-20
            "very_high": 0 # 21+
        }
        
        for file_metrics in files:
            if "error" in file_metrics:
                continue
            
            complexity = file_metrics["complexity"]["cyclomatic"]
            
            if complexity <= 5:
                distribution["low"] += 1
            elif complexity <= 10:
                distribution["medium"] += 1
            elif complexity <= 20:
                distribution["high"] += 1
            else:
                distribution["very_high"] += 1
        
        return distribution
    
    def _calculate_quality_metrics(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall quality metrics"""
        
        if not files:
            return {}
        
        total_functions = sum(f.get("functions", 0) for f in files if "error" not in f)
        total_docstrings = sum(f.get("docstrings", 0) for f in files if "error" not in f)
        total_lines = sum(f.get("lines_of_code", 0) for f in files if "error" not in f)
        total_comments = sum(f.get("comments", 0) for f in files if "error" not in f)
        
        maintainability_scores = [
            f.get("maintainability_index", 0) 
            for f in files if "error" not in f and f.get("maintainability_index", 0) > 0
        ]
        
        return {
            "documentation_coverage": (total_docstrings / total_functions * 100) if total_functions > 0 else 0,
            "comment_density": (total_comments / total_lines * 100) if total_lines > 0 else 0,
            "avg_maintainability": sum(maintainability_scores) / len(maintainability_scores) if maintainability_scores else 0,
            "total_files_analyzed": len([f for f in files if "error" not in f])
        }
    
    def _calculate_language_stats(self, project_path: Path) -> Dict[str, Any]:
        """Calculate language statistics"""
        
        language_lines = defaultdict(int)
        language_files = defaultdict(int)
        
        # Language mappings
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
        }
        
        for ext, lang in extensions.items():
            for file_path in project_path.rglob(f'*{ext}'):
                if any(skip in file_path.parts for skip in ['venv', 'node_modules', '__pycache__']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    
                    language_lines[lang] += lines
                    language_files[lang] += 1
                except:
                    pass
        
        # Calculate percentages
        total_lines = sum(language_lines.values())
        
        languages = []
        for lang in language_lines:
            languages.append({
                "language": lang,
                "files": language_files[lang],
                "lines": language_lines[lang],
                "percentage": (language_lines[lang] / total_lines * 100) if total_lines > 0 else 0
            })
        
        # Sort by lines
        languages.sort(key=lambda x: x["lines"], reverse=True)
        
        return {
            "languages": languages,
            "total_lines": total_lines,
            "primary_language": languages[0]["language"] if languages else None
        }
    
    def get_file_hotspots(
        self,
        files: List[Dict[str, Any]],
        metric: str = "complexity",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get files with highest values for specific metric
        
        Args:
            files: List of file metrics
            metric: Metric to sort by (complexity, lines, functions)
            limit: Number of results
            
        Returns:
            Top files for metric
        """
        valid_files = [f for f in files if "error" not in f]
        
        if metric == "complexity":
            sorted_files = sorted(
                valid_files,
                key=lambda x: x["complexity"]["cyclomatic"],
                reverse=True
            )
        elif metric == "lines":
            sorted_files = sorted(
                valid_files,
                key=lambda x: x["lines_of_code"],
                reverse=True
            )
        elif metric == "functions":
            sorted_files = sorted(
                valid_files,
                key=lambda x: x["functions"],
                reverse=True
            )
        else:
            return []
        
        return sorted_files[:limit]
