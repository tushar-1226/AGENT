"""
Code Reviewer - AI-Powered Code Review Bot
Analyzes code quality, security, performance, and best practices
"""

import logging
import ast
import re
from typing import List, Dict, Optional, Any
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class CodeReviewer:
    """AI-powered code review system with quality metrics"""
    
    def __init__(self, gemini_processor=None):
        """
        Initialize code reviewer
        
        Args:
            gemini_processor: Gemini AI processor for analysis
        """
        self.gemini = gemini_processor
        self.review_history = []
        logger.info("Code Reviewer initialized")
    
    async def review_code(
        self,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        review_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review
        
        Args:
            code: Code to review
            language: Programming language
            file_path: Optional file path
            review_type: Type of review (quick, comprehensive, security)
            
        Returns:
            Review report with issues, suggestions, and quality score
        """
        try:
            logger.info(f"Starting {review_type} code review for {language}")
            
            review_report = {
                "language": language,
                "file_path": file_path,
                "review_type": review_type,
                "issues": [],
                "suggestions": [],
                "metrics": {},
                "quality_score": 0.0,
                "summary": ""
            }
            
            # Perform language-specific analysis
            if language == "python":
                review_report = await self._review_python(code, review_report)
            elif language in ["javascript", "typescript"]:
                review_report = await self._review_javascript(code, review_report)
            else:
                review_report = await self._review_generic(code, review_report, language)
            
            # Calculate overall quality score
            review_report["quality_score"] = self._calculate_quality_score(review_report)
            
            # Generate AI summary
            if self.gemini:
                review_report["summary"] = await self._generate_summary(review_report)
            
            # Store in history
            self.review_history.append(review_report)
            
            return review_report
            
        except Exception as e:
            logger.error(f"Error reviewing code: {e}")
            return {
                "error": str(e),
                "quality_score": 0.0
            }
    
    async def _review_python(
        self, code: str, report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform Python-specific code review"""
        
        # AST Analysis
        try:
            tree = ast.parse(code)
            report["metrics"]["ast_valid"] = True
            
            # Analyze AST
            report = self._analyze_python_ast(tree, code, report)
            
        except SyntaxError as e:
            report["issues"].append({
                "severity": "error",
                "type": "syntax",
                "message": f"Syntax error: {e.msg}",
                "line": e.lineno,
                "fix": None
            })
            report["metrics"]["ast_valid"] = False
            return report
        
        # Complexity Analysis
        report["metrics"]["complexity"] = self._calculate_complexity(tree)
        
        # Code Smell Detection
        report["issues"].extend(self._detect_python_code_smells(code, tree))
        
        # Security Analysis
        report["issues"].extend(self._detect_python_security_issues(code, tree))
        
        # Best Practices Check
        report["suggestions"].extend(self._check_python_best_practices(code, tree))
        
        # Performance Analysis
        report["suggestions"].extend(self._analyze_python_performance(code, tree))
        
        return report
    
    def _analyze_python_ast(
        self, tree: ast.AST, code: str, report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze Python AST for metrics"""
        
        metrics = {
            "functions": 0,
            "classes": 0,
            "lines": len(code.split('\n')),
            "imports": 0,
            "docstrings": 0,
            "comments": 0
        }
        
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
        metrics["comments"] = len(re.findall(r'#.*$', code, re.MULTILINE))
        
        report["metrics"].update(metrics)
        return report
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code complexity metrics"""
        
        complexity = {
            "cyclomatic": 1,  # Base complexity
            "cognitive": 0,
            "max_depth": 0,
            "avg_function_length": 0
        }
        
        function_lengths = []
        
        for node in ast.walk(tree):
            # Cyclomatic complexity (decision points)
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity["cyclomatic"] += 1
            
            elif isinstance(node, ast.BoolOp):
                complexity["cyclomatic"] += len(node.values) - 1
            
            # Function length
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                function_lengths.append(func_lines)
        
        if function_lengths:
            complexity["avg_function_length"] = sum(function_lengths) / len(function_lengths)
        
        return complexity
    
    def _detect_python_code_smells(
        self, code: str, tree: ast.AST
    ) -> List[Dict[str, Any]]:
        """Detect Python code smells"""
        
        issues = []
        
        for node in ast.walk(tree):
            # Long functions (>50 lines)
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        issues.append({
                            "severity": "warning",
                            "type": "code_smell",
                            "message": f"Function '{node.name}' is too long ({func_length} lines)",
                            "line": node.lineno,
                            "fix": "Consider breaking into smaller functions"
                        })
                
                # Too many parameters
                if len(node.args.args) > 5:
                    issues.append({
                        "severity": "warning",
                        "type": "code_smell",
                        "message": f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        "line": node.lineno,
                        "fix": "Consider using a configuration object or dataclass"
                    })
            
            # Nested complexity
            if isinstance(node, ast.If):
                depth = self._get_nesting_depth(node)
                if depth > 3:
                    issues.append({
                        "severity": "warning",
                        "type": "complexity",
                        "message": f"Deeply nested if statement (depth: {depth})",
                        "line": node.lineno,
                        "fix": "Consider extracting to separate functions or using early returns"
                    })
        
        # Check for missing docstrings
        module_docstring = ast.get_docstring(tree)
        if not module_docstring:
            issues.append({
                "severity": "info",
                "type": "documentation",
                "message": "Module is missing a docstring",
                "line": 1,
                "fix": "Add a module-level docstring describing the file's purpose"
            })
        
        return issues
    
    def _detect_python_security_issues(
        self, code: str, tree: ast.AST
    ) -> List[Dict[str, Any]]:
        """Detect Python security vulnerabilities"""
        
        issues = []
        
        for node in ast.walk(tree):
            # Dangerous eval/exec usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            "severity": "critical",
                            "type": "security",
                            "message": f"Dangerous use of {node.func.id}()",
                            "line": node.lineno,
                            "fix": "Avoid eval/exec. Use safer alternatives like ast.literal_eval"
                        })
            
            # SQL injection risk
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'executemany']:
                        # Check for string formatting in SQL
                        if node.args and isinstance(node.args[0], ast.JoinedStr):
                            issues.append({
                                "severity": "critical",
                                "type": "security",
                                "message": "Potential SQL injection vulnerability",
                                "line": node.lineno,
                                "fix": "Use parameterized queries instead of string formatting"
                            })
        
        # Check for hardcoded secrets (basic patterns)
        secret_patterns = [
            (r'password\s*=\s*["\'].*["\']', "Hardcoded password detected"),
            (r'api[_-]?key\s*=\s*["\'].*["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'].*["\']', "Hardcoded secret detected"),
        ]
        
        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    "severity": "critical",
                    "type": "security",
                    "message": message,
                    "line": line_num,
                    "fix": "Use environment variables or secure configuration management"
                })
        
        return issues
    
    def _check_python_best_practices(
        self, code: str, tree: ast.AST
    ) -> List[Dict[str, Any]]:
        """Check Python best practices"""
        
        suggestions = []
        
        # Check for type hints
        has_type_hints = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    has_type_hints = True
                    break
        
        if not has_type_hints:
            suggestions.append({
                "type": "best_practice",
                "message": "Consider adding type hints for better code clarity",
                "priority": "medium"
            })
        
        # Check for exception handling
        has_exception_handling = any(
            isinstance(node, ast.Try) for node in ast.walk(tree)
        )
        
        if not has_exception_handling and len(code.split('\n')) > 20:
            suggestions.append({
                "type": "best_practice",
                "message": "Consider adding exception handling for robustness",
                "priority": "medium"
            })
        
        # Check for list comprehensions vs loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Simple pattern: for x in y: result.append(...)
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Call)):
                    suggestions.append({
                        "type": "best_practice",
                        "message": "Consider using list comprehension for better performance",
                        "line": node.lineno,
                        "priority": "low"
                    })
        
        return suggestions
    
    def _analyze_python_performance(
        self, code: str, tree: ast.AST
    ) -> List[Dict[str, Any]]:
        """Analyze Python performance issues"""
        
        suggestions = []
        
        for node in ast.walk(tree):
            # Inefficient string concatenation in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            suggestions.append({
                                "type": "performance",
                                "message": "String concatenation in loop is inefficient",
                                "line": node.lineno,
                                "fix": "Use list.append() and ''.join() instead",
                                "priority": "medium"
                            })
        
        return suggestions
    
    def _get_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate nesting depth of a node"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    async def _review_javascript(
        self, code: str, report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform JavaScript/TypeScript code review"""
        
        # Basic metrics
        lines = code.split('\n')
        report["metrics"]["lines"] = len(lines)
        report["metrics"]["comments"] = len([l for l in lines if l.strip().startswith('//')])
        
        # Common issues
        issues = []
        
        # Check for var usage (should use let/const)
        var_matches = re.finditer(r'\bvar\s+\w+', code)
        for match in var_matches:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "severity": "warning",
                "type": "best_practice",
                "message": "Use 'let' or 'const' instead of 'var'",
                "line": line_num,
                "fix": "Replace 'var' with 'const' (or 'let' if reassignment needed)"
            })
        
        # Check for == instead of ===
        loose_equality = re.finditer(r'[^=!]==[^=]', code)
        for match in loose_equality:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "severity": "warning",
                "type": "best_practice",
                "message": "Use strict equality (===) instead of loose equality (==)",
                "line": line_num,
                "fix": "Replace '==' with '==='"
            })
        
        # Check for console.log (should be removed in production)
        console_logs = re.finditer(r'console\.log\(', code)
        for match in console_logs:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "severity": "info",
                "type": "code_smell",
                "message": "Remove console.log before production",
                "line": line_num,
                "fix": "Use proper logging library or remove"
            })
        
        report["issues"].extend(issues)
        
        return report
    
    async def _review_generic(
        self, code: str, report: Dict[str, Any], language: str
    ) -> Dict[str, Any]:
        """Perform generic code review using AI"""
        
        if not self.gemini:
            return report
        
        try:
            prompt = f"""Review this {language} code and identify issues:

```{language}
{code}
```

Provide a JSON array of issues with this format:
[
  {{
    "severity": "critical|warning|info",
    "type": "security|performance|best_practice|code_smell",
    "message": "Description of issue",
    "line": line_number,
    "fix": "Suggested fix"
  }}
]

Only return valid JSON."""
            
            response = await self.gemini.generate_content(prompt)
            
            # Parse AI response
            import json
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                issues = json.loads(json_match.group(0))
                report["issues"].extend(issues)
        
        except Exception as e:
            logger.error(f"Error in generic review: {e}")
        
        return report
    
    def _calculate_quality_score(self, report: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)"""
        
        score = 100.0
        
        # Deduct points for issues
        for issue in report.get("issues", []):
            if issue["severity"] == "critical":
                score -= 15
            elif issue["severity"] == "error":
                score -= 10
            elif issue["severity"] == "warning":
                score -= 5
            elif issue["severity"] == "info":
                score -= 2
        
        # Bonus for good metrics
        metrics = report.get("metrics", {})
        
        # Bonus for documentation
        if metrics.get("docstrings", 0) > 0:
            score += 5
        
        if metrics.get("comments", 0) > 0:
            score += 3
        
        # Penalty for high complexity
        complexity = metrics.get("complexity", {})
        if complexity.get("cyclomatic", 0) > 10:
            score -= 10
        
        # Ensure score is in valid range
        return max(0.0, min(100.0, score))
    
    async def _generate_summary(self, report: Dict[str, Any]) -> str:
        """Generate AI summary of review"""
        
        try:
            critical_issues = [i for i in report["issues"] if i["severity"] == "critical"]
            warnings = [i for i in report["issues"] if i["severity"] == "warning"]
            
            prompt = f"""Summarize this code review in 2-3 sentences:

Quality Score: {report['quality_score']}/100
Critical Issues: {len(critical_issues)}
Warnings: {len(warnings)}
Metrics: {report['metrics']}

Focus on the most important findings and overall code quality."""
            
            summary = await self.gemini.generate_content(prompt)
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Code quality score: {report['quality_score']}/100"
    
    def get_review_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent review history"""
        return self.review_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reviewer statistics"""
        return {
            "total_reviews": len(self.review_history),
            "avg_quality_score": sum(r.get("quality_score", 0) for r in self.review_history) / len(self.review_history) if self.review_history else 0,
            "has_gemini": self.gemini is not None
        }
