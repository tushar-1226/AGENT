"""
Code Intelligence Module
Advanced code analysis and suggestions
"""

import ast
import re
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class CodeIntelligence:
    """Advanced code intelligence and analysis"""
    
    def __init__(self, llm_processor=None):
        self.llm = llm_processor
        self.code_smells = self._initialize_code_smells()
    
    def _initialize_code_smells(self) -> Dict:
        """Initialize code smell patterns"""
        return {
            "long_method": {
                "threshold": 50,
                "severity": "medium",
                "message": "Method is too long (>{} lines)"
            },
            "too_many_parameters": {
                "threshold": 5,
                "severity": "medium",
                "message": "Too many parameters (>{})"
            },
            "deep_nesting": {
                "threshold": 4,
                "severity": "high",
                "message": "Too many nested blocks (>{})"
            },
            "duplicate_code": {
                "threshold": 10,
                "severity": "medium",
                "message": "Potential code duplication detected"
            }
        }
    
    async def analyze_code_quality(self, code: str, language: str = "python") -> Dict:
        """Comprehensive code quality analysis"""
        if language == "python":
            return await self._analyze_python_code(code)
        elif language in ["javascript", "typescript"]:
            return await self._analyze_javascript_code(code)
        else:
            return {"success": False, "error": f"Unsupported language: {language}"}
    
    async def _analyze_python_code(self, code: str) -> Dict:
        """Analyze Python code quality"""
        try:
            tree = ast.parse(code)
            
            issues = []
            metrics = {
                "total_lines": len(code.split("\n")),
                "functions": 0,
                "classes": 0,
                "complexity_score": 0
            }
            
            for node in ast.walk(tree):
                # Count functions and classes
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    
                    # Check function length
                    func_lines = node.end_lineno - node.lineno
                    if func_lines > self.code_smells["long_method"]["threshold"]:
                        issues.append({
                            "type": "long_method",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": f"Function '{node.name}' is {func_lines} lines long",
                            "suggestion": "Consider breaking into smaller functions"
                        })
                    
                    # Check parameter count
                    param_count = len(node.args.args)
                    if param_count > self.code_smells["too_many_parameters"]["threshold"]:
                        issues.append({
                            "type": "too_many_parameters",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": f"Function '{node.name}' has {param_count} parameters",
                            "suggestion": "Consider using a config object or class"
                        })
                
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                    
                    # Check class size
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 20:
                        issues.append({
                            "type": "god_class",
                            "severity": "high",
                            "line": node.lineno,
                            "message": f"Class '{node.name}' has {len(methods)} methods",
                            "suggestion": "Consider splitting into multiple classes"
                        })
            
            # Calculate complexity score
            metrics["complexity_score"] = self._calculate_complexity(tree)
            
            # Detect code smells
            smells = self._detect_python_smells(code, tree)
            issues.extend(smells)
            
            return {
                "success": True,
                "metrics": metrics,
                "issues": issues,
                "quality_score": self._calculate_quality_score(metrics, issues)
            }
        
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {e}",
                "line": e.lineno if hasattr(e, 'lineno') else None
            }
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_javascript_code(self, code: str) -> Dict:
        """Analyze JavaScript/TypeScript code quality"""
        issues = []
        metrics = {
            "total_lines": len(code.split("\n")),
            "functions": len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(.*?\)\s*=>', code)),
            "classes": len(re.findall(r'class\s+\w+', code))
        }
        
        # Check for console.log (should be removed in production)
        console_logs = re.finditer(r'console\.log', code)
        for match in console_logs:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "type": "console_log",
                "severity": "low",
                "line": line_num,
                "message": "console.log found",
                "suggestion": "Remove console.log statements before production"
            })
        
        # Check for var usage (prefer let/const)
        var_usage = re.finditer(r'\bvar\s+\w+', code)
        for match in var_usage:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "type": "var_usage",
                "severity": "low",
                "line": line_num,
                "message": "Using 'var' instead of 'let'/'const'",
                "suggestion": "Use 'let' or 'const' for better scoping"
            })
        
        return {
            "success": True,
            "metrics": metrics,
            "issues": issues,
            "quality_score": self._calculate_quality_score(metrics, issues)
        }
    
    def _detect_python_smells(self, code: str, tree: ast.AST) -> List[Dict]:
        """Detect specific Python code smells"""
        smells = []
        
        # Check for bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    smells.append({
                        "type": "bare_except",
                        "severity": "high",
                        "line": node.lineno,
                        "message": "Bare 'except' clause catches all exceptions",
                        "suggestion": "Catch specific exceptions"
                    })
        
        # Check for mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        smells.append({
                            "type": "mutable_default",
                            "severity": "high",
                            "line": node.lineno,
                            "message": f"Mutable default argument in '{node.name}'",
                            "suggestion": "Use None as default and initialize inside function"
                        })
        
        return smells
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_quality_score(self, metrics: Dict, issues: List[Dict]) -> float:
        """Calculate overall quality score (0-100)"""
        base_score = 100.0
        
        # Deduct points for issues
        for issue in issues:
            if issue["severity"] == "high":
                base_score -= 5
            elif issue["severity"] == "medium":
                base_score -= 3
            else:
                base_score -= 1
        
        # Deduct for high complexity
        if metrics.get("complexity_score", 0) > 50:
            base_score -= 10
        elif metrics.get("complexity_score", 0) > 30:
            base_score -= 5
        
        return max(0.0, min(100.0, base_score))
    
    async def suggest_refactoring(self, code: str, language: str = "python") -> Dict:
        """Suggest refactoring opportunities"""
        analysis = await self.analyze_code_quality(code, language)
        
        if not analysis["success"]:
            return analysis
        
        refactorings = []
        
        for issue in analysis["issues"]:
            if issue["type"] == "long_method":
                refactorings.append({
                    "type": "extract_method",
                    "priority": "high",
                    "description": "Extract method to reduce function length",
                    "line": issue["line"]
                })
            elif issue["type"] == "duplicate_code":
                refactorings.append({
                    "type": "extract_common",
                    "priority": "medium",
                    "description": "Extract duplicate code into shared function",
                    "line": issue["line"]
                })
        
        return {
            "success": True,
            "refactorings": refactorings,
            "analysis": analysis
        }
    
    async def get_context_aware_completions(
        self,
        code: str,
        cursor_position: int,
        project_context: Optional[Dict] = None
    ) -> Dict:
        """Get smart code completions based on context"""
        try:
            # Extract context around cursor
            lines = code[:cursor_position].split('\n')
            current_line = lines[-1] if lines else ""
            
            suggestions = []
            
            # Detect import statements
            if current_line.strip().startswith('import ') or current_line.strip().startswith('from '):
                suggestions.extend(self._suggest_imports(code, project_context))
            
            # Detect function calls
            elif '(' in current_line and ')' not in current_line:
                suggestions.extend(self._suggest_parameters(code, current_line))
            
            # Detect variable assignments
            elif '=' in current_line and not '==' in current_line:
                suggestions.extend(self._suggest_values(code, current_line))
            
            return {
                "success": True,
                "suggestions": suggestions[:10],  # Limit to top 10
                "context": {
                    "current_line": current_line,
                    "line_number": len(lines)
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating completions: {e}")
            return {"success": False, "error": str(e)}
    
    def _suggest_imports(self, code: str, context: Optional[Dict]) -> List[Dict]:
        """Suggest relevant imports"""
        # Common imports based on code content
        suggestions = []
        
        if 'async ' in code or 'await ' in code:
            suggestions.append({
                "text": "import asyncio",
                "description": "Async support",
                "priority": 9
            })
        
        if 'Dict' in code or 'List' in code:
            suggestions.append({
                "text": "from typing import Dict, List, Optional",
                "description": "Type hints",
                "priority": 9
            })
        
        if 'FastAPI' in code:
            suggestions.append({
                "text": "from fastapi import APIRouter, HTTPException",
                "description": "FastAPI components",
                "priority": 10
            })
        
        return suggestions
    
    def _suggest_parameters(self, code: str, current_line: str) -> List[Dict]:
        """Suggest function parameters"""
        return []
    
    def _suggest_values(self, code: str, current_line: str) -> List[Dict]:
        """Suggest values for assignments"""
        return []
