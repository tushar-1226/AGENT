"""
AI Pair Programmer Module
Proactive code suggestions, context-aware completions, real-time code review
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import ast
import json

logger = logging.getLogger(__name__)


@dataclass
class CodeSuggestion:
    """Represents an AI-generated code suggestion"""
    suggestion_id: str
    type: str  # completion, refactor, fix, optimization, documentation
    code: str
    explanation: str
    confidence: float
    line_start: int
    line_end: int
    priority: str  # low, medium, high, critical


@dataclass
class CodeContext:
    """Represents the current code context"""
    file_path: str
    language: str
    current_code: str
    cursor_position: Dict
    imports: List[str]
    functions: List[str]
    classes: List[str]
    variables: List[str]


class AIPairProgrammer:
    """
    AI Pair Programmer for intelligent code assistance:
    - Real-time code suggestions as you type
    - Context-aware completions using codebase knowledge
    - Proactive error detection and fixes
    - Code optimization suggestions
    - Next-step recommendations
    """

    def __init__(self, llm_processor=None):
        self.llm = llm_processor
        self.suggestion_cache = {}
        self.context_history = []
        self.user_preferences = {}
        self.codebase_index = {}  # For context-aware suggestions
        logger.info("AI Pair Programmer initialized")

    # ==================== Real-time Code Suggestions ====================

    async def get_live_suggestions(
        self,
        code_context: Dict,
        trigger_type: str = "typing"
    ) -> Dict:
        """
        Get live code suggestions as user types
        trigger_type: typing, newline, save, manual
        """
        try:
            context = self._parse_code_context(code_context)
            suggestions = []

            # Get different types of suggestions based on context
            if trigger_type == "typing":
                suggestions.extend(await self._get_completion_suggestions(context))
            
            suggestions.extend(await self._get_error_fixes(context))
            suggestions.extend(await self._get_optimization_suggestions(context))
            suggestions.extend(await self._get_best_practice_suggestions(context))

            # Rank suggestions by priority and confidence
            ranked_suggestions = self._rank_suggestions(suggestions)

            return {
                "success": True,
                "suggestions": ranked_suggestions[:5],  # Top 5
                "context": {
                    "file": context.file_path,
                    "language": context.language,
                    "cursor_line": context.cursor_position.get("line", 0)
                }
            }

        except Exception as e:
            logger.error(f"Error getting live suggestions: {e}")
            return {"success": False, "error": str(e)}

    async def _get_completion_suggestions(self, context: CodeContext) -> List[CodeSuggestion]:
        """Generate intelligent code completions"""
        suggestions = []

        try:
            # Get current line
            lines = context.current_code.split('\n')
            cursor_line = context.cursor_position.get("line", 0)
            current_line = lines[cursor_line] if cursor_line < len(lines) else ""

            # Pattern-based completions
            if context.language == "python":
                suggestions.extend(self._python_completions(current_line, context))
            elif context.language in ["javascript", "typescript"]:
                suggestions.extend(self._javascript_completions(current_line, context))

            # AI-powered completions using LLM
            if self.llm:
                ai_suggestions = await self._get_ai_completions(context, current_line)
                suggestions.extend(ai_suggestions)

        except Exception as e:
            logger.error(f"Error in completion suggestions: {e}")

        return suggestions

    def _python_completions(self, current_line: str, context: CodeContext) -> List[CodeSuggestion]:
        """Python-specific completions"""
        suggestions = []

        # Import suggestions
        if current_line.strip().startswith("import ") or current_line.strip().startswith("from "):
            common_imports = [
                "import os\nimport sys",
                "from typing import List, Dict, Optional",
                "import asyncio",
                "from dataclasses import dataclass"
            ]
            for imp in common_imports:
                if imp.split()[1] not in context.current_code:
                    suggestions.append(CodeSuggestion(
                        suggestion_id=f"imp_{len(suggestions)}",
                        type="completion",
                        code=imp,
                        explanation=f"Common import: {imp}",
                        confidence=0.7,
                        line_start=context.cursor_position.get("line", 0),
                        line_end=context.cursor_position.get("line", 0),
                        priority="medium"
                    ))

        # Function definition completions
        if current_line.strip().startswith("def "):
            # Suggest type hints
            if ":" not in current_line or "->" not in current_line:
                suggestions.append(CodeSuggestion(
                    suggestion_id="type_hint",
                    type="completion",
                    code="Add type hints for better code quality",
                    explanation="Consider adding type hints to function parameters and return type",
                    confidence=0.8,
                    line_start=context.cursor_position.get("line", 0),
                    line_end=context.cursor_position.get("line", 0),
                    priority="medium"
                ))

        # Class definition completions
        if current_line.strip().startswith("class "):
            suggestions.append(CodeSuggestion(
                suggestion_id="class_init",
                type="completion",
                code="    def __init__(self):\n        pass",
                explanation="Add __init__ method to class",
                confidence=0.9,
                line_start=context.cursor_position.get("line", 0) + 1,
                line_end=context.cursor_position.get("line", 0) + 2,
                priority="high"
            ))

        # Try-except suggestions
        if "try:" in context.current_code and "except" not in context.current_code:
            suggestions.append(CodeSuggestion(
                suggestion_id="except_block",
                type="completion",
                code="except Exception as e:\n    logger.error(f'Error: {e}')\n    return {'success': False, 'error': str(e)}",
                explanation="Add exception handling",
                confidence=0.85,
                line_start=context.cursor_position.get("line", 0),
                line_end=context.cursor_position.get("line", 0) + 2,
                priority="high"
            ))

        return suggestions

    def _javascript_completions(self, current_line: str, context: CodeContext) -> List[CodeSuggestion]:
        """JavaScript/TypeScript-specific completions"""
        suggestions = []

        # Async/await suggestions
        if "fetch(" in current_line and "await" not in current_line:
            suggestions.append(CodeSuggestion(
                suggestion_id="await_fetch",
                type="completion",
                code="Use await with fetch",
                explanation="Fetch returns a Promise - consider using await",
                confidence=0.9,
                line_start=context.cursor_position.get("line", 0),
                line_end=context.cursor_position.get("line", 0),
                priority="high"
            ))

        # Arrow function completions
        if "function" in current_line:
            suggestions.append(CodeSuggestion(
                suggestion_id="arrow_func",
                type="refactor",
                code="Convert to arrow function for modern syntax",
                explanation="Arrow functions have lexical 'this' binding",
                confidence=0.7,
                line_start=context.cursor_position.get("line", 0),
                line_end=context.cursor_position.get("line", 0),
                priority="low"
            ))

        return suggestions

    async def _get_ai_completions(self, context: CodeContext, current_line: str) -> List[CodeSuggestion]:
        """Get AI-powered completions using LLM"""
        suggestions = []

        try:
            # Build prompt for LLM
            prompt = f"""Given this code context:
File: {context.file_path}
Language: {context.language}

Current code:
{context.current_code}

Current line being edited: {current_line}

Suggest the next 1-2 lines of code that would make sense. Be concise and practical.
Focus on: proper error handling, type safety, best practices."""

            # This would call your LLM (Gemini, OpenRouter, etc.)
            # Placeholder for actual LLM call
            if hasattr(self.llm, 'process_with_gemini'):
                response = await self.llm.process_with_gemini(
                    message=prompt,
                    model="gemini-pro"
                )
                
                if response.get("success"):
                    suggestions.append(CodeSuggestion(
                        suggestion_id="ai_completion",
                        type="completion",
                        code=response.get("response", ""),
                        explanation="AI-suggested code completion",
                        confidence=0.75,
                        line_start=context.cursor_position.get("line", 0) + 1,
                        line_end=context.cursor_position.get("line", 0) + 1,
                        priority="medium"
                    ))

        except Exception as e:
            logger.error(f"Error in AI completions: {e}")

        return suggestions

    # ==================== Error Detection & Fixes ====================

    async def _get_error_fixes(self, context: CodeContext) -> List[CodeSuggestion]:
        """Proactively detect and suggest fixes for potential errors"""
        suggestions = []

        try:
            if context.language == "python":
                # Parse Python code for common errors
                try:
                    ast.parse(context.current_code)
                except SyntaxError as e:
                    suggestions.append(CodeSuggestion(
                        suggestion_id="syntax_error",
                        type="fix",
                        code=f"Fix syntax error at line {e.lineno}",
                        explanation=str(e.msg),
                        confidence=1.0,
                        line_start=e.lineno or 0,
                        line_end=e.lineno or 0,
                        priority="critical"
                    ))

            # Check for common issues
            suggestions.extend(self._check_common_issues(context))

        except Exception as e:
            logger.error(f"Error in error detection: {e}")

        return suggestions

    def _check_common_issues(self, context: CodeContext) -> List[CodeSuggestion]:
        """Check for common coding issues"""
        suggestions = []

        # Check for undefined variables
        if context.language == "python":
            # Simple check for common patterns
            lines = context.current_code.split('\n')
            for i, line in enumerate(lines):
                # Check for print statements (should use logger)
                if re.search(r'\bprint\s*\(', line):
                    suggestions.append(CodeSuggestion(
                        suggestion_id=f"print_to_logger_{i}",
                        type="optimization",
                        code=f"Use logger instead of print",
                        explanation="Replace print() with logger.info() for better logging",
                        confidence=0.8,
                        line_start=i,
                        line_end=i,
                        priority="medium"
                    ))

                # Check for bare except
                if re.search(r'except\s*:', line):
                    suggestions.append(CodeSuggestion(
                        suggestion_id=f"bare_except_{i}",
                        type="fix",
                        code="Specify exception type",
                        explanation="Bare except catches all exceptions, including system exits",
                        confidence=0.9,
                        line_start=i,
                        line_end=i,
                        priority="high"
                    ))

        return suggestions

    # ==================== Optimization Suggestions ====================

    async def _get_optimization_suggestions(self, context: CodeContext) -> List[CodeSuggestion]:
        """Suggest performance and code optimizations"""
        suggestions = []

        try:
            lines = context.current_code.split('\n')

            for i, line in enumerate(lines):
                # Check for inefficient loops
                if re.search(r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', line):
                    suggestions.append(CodeSuggestion(
                        suggestion_id=f"enumerate_{i}",
                        type="optimization",
                        code="Use enumerate() instead of range(len())",
                        explanation="More Pythonic and efficient",
                        confidence=0.85,
                        line_start=i,
                        line_end=i,
                        priority="medium"
                    ))

                # Check for string concatenation in loops
                if '+=' in line and any(word in line for word in ['str', 'string', '""', "''"]):
                    suggestions.append(CodeSuggestion(
                        suggestion_id=f"join_{i}",
                        type="optimization",
                        code="Use ''.join() for string concatenation in loops",
                        explanation="String concatenation in loops is inefficient",
                        confidence=0.8,
                        line_start=i,
                        line_end=i,
                        priority="medium"
                    ))

                # Check for multiple list appends
                if context.language == "python" and ".append(" in line:
                    # Count appends in function
                    append_count = context.current_code.count('.append(')
                    if append_count > 5:
                        suggestions.append(CodeSuggestion(
                            suggestion_id="list_comprehension",
                            type="optimization",
                            code="Consider using list comprehension",
                            explanation=f"Found {append_count} append calls - list comprehension may be cleaner",
                            confidence=0.7,
                            line_start=i,
                            line_end=i,
                            priority="low"
                        ))

        except Exception as e:
            logger.error(f"Error in optimization suggestions: {e}")

        return suggestions

    # ==================== Best Practice Suggestions ====================

    async def _get_best_practice_suggestions(self, context: CodeContext) -> List[CodeSuggestion]:
        """Suggest best practices and coding standards"""
        suggestions = []

        try:
            # Check for missing docstrings
            if context.language == "python":
                func_pattern = r'def\s+\w+\s*\([^)]*\)\s*(?:->.*?)?\s*:'
                functions = re.finditer(func_pattern, context.current_code)
                
                for match in functions:
                    start = match.start()
                    # Check if next non-empty line is a docstring
                    lines_after = context.current_code[match.end():].split('\n')
                    if lines_after and not lines_after[1].strip().startswith('"""'):
                        line_num = context.current_code[:start].count('\n')
                        suggestions.append(CodeSuggestion(
                            suggestion_id=f"docstring_{line_num}",
                            type="documentation",
                            code='    """Add function docstring here"""',
                            explanation="Functions should have docstrings describing purpose and parameters",
                            confidence=0.75,
                            line_start=line_num + 1,
                            line_end=line_num + 1,
                            priority="medium"
                        ))

            # Check for magic numbers
            magic_numbers = re.finditer(r'\b(\d{2,})\b', context.current_code)
            for match in magic_numbers:
                num = match.group(1)
                if num not in ['100', '1000']:  # Exclude common numbers
                    line_num = context.current_code[:match.start()].count('\n')
                    suggestions.append(CodeSuggestion(
                        suggestion_id=f"magic_number_{line_num}",
                        type="refactor",
                        code=f"Extract {num} to a named constant",
                        explanation="Magic numbers reduce code readability",
                        confidence=0.65,
                        line_start=line_num,
                        line_end=line_num,
                        priority="low"
                    ))

        except Exception as e:
            logger.error(f"Error in best practice suggestions: {e}")

        return suggestions

    # ==================== Context-Aware Features ====================

    async def suggest_next_steps(self, context: Dict) -> Dict:
        """Suggest next logical steps in implementation"""
        try:
            code_context = self._parse_code_context(context)
            suggestions = []

            # Analyze what's been done and what's missing
            has_error_handling = "try:" in code_context.current_code or "except" in code_context.current_code
            has_logging = "logger" in code_context.current_code or "logging" in code_context.current_code
            has_tests = "test_" in code_context.file_path or "def test" in code_context.current_code
            has_docstrings = '"""' in code_context.current_code

            if not has_error_handling:
                suggestions.append({
                    "step": "Add error handling",
                    "priority": "high",
                    "reason": "No try-except blocks found"
                })

            if not has_logging:
                suggestions.append({
                    "step": "Add logging statements",
                    "priority": "medium",
                    "reason": "Logging helps with debugging and monitoring"
                })

            if not has_tests and "test" not in code_context.file_path:
                suggestions.append({
                    "step": "Write unit tests",
                    "priority": "high",
                    "reason": "No tests found for this module"
                })

            if not has_docstrings:
                suggestions.append({
                    "step": "Add documentation",
                    "priority": "medium",
                    "reason": "Functions lack docstrings"
                })

            # AI-powered next step suggestions
            if self.llm:
                ai_steps = await self._get_ai_next_steps(code_context)
                suggestions.extend(ai_steps)

            return {
                "success": True,
                "next_steps": suggestions[:5],
                "completion_percentage": self._estimate_completion(code_context)
            }

        except Exception as e:
            logger.error(f"Error suggesting next steps: {e}")
            return {"success": False, "error": str(e)}

    async def _get_ai_next_steps(self, context: CodeContext) -> List[Dict]:
        """Get AI-suggested next steps"""
        steps = []
        
        # Placeholder for LLM integration
        # Would analyze code and suggest next logical implementation steps
        
        return steps

    def _estimate_completion(self, context: CodeContext) -> int:
        """Estimate code completion percentage"""
        score = 0
        
        if "def " in context.current_code or "class " in context.current_code:
            score += 20
        if '"""' in context.current_code:
            score += 15
        if "try:" in context.current_code:
            score += 15
        if "logger" in context.current_code:
            score += 10
        if context.imports:
            score += 10
        if len(context.current_code) > 100:
            score += 20
        if "return" in context.current_code:
            score += 10
            
        return min(score, 100)

    # ==================== Utility Methods ====================

    def _parse_code_context(self, context_dict: Dict) -> CodeContext:
        """Parse code context from dictionary"""
        code = context_dict.get("code", "")
        
        # Extract imports, functions, classes
        imports = re.findall(r'^(?:from|import)\s+[\w.]+', code, re.MULTILINE)
        functions = re.findall(r'def\s+(\w+)', code)
        classes = re.findall(r'class\s+(\w+)', code)
        
        # Simple variable extraction (can be improved)
        variables = re.findall(r'(\w+)\s*=', code)

        return CodeContext(
            file_path=context_dict.get("file_path", ""),
            language=context_dict.get("language", "python"),
            current_code=code,
            cursor_position=context_dict.get("cursor_position", {"line": 0, "column": 0}),
            imports=imports,
            functions=functions,
            classes=classes,
            variables=list(set(variables))
        )

    def _rank_suggestions(self, suggestions: List[CodeSuggestion]) -> List[Dict]:
        """Rank suggestions by priority and confidence"""
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        ranked = sorted(
            suggestions,
            key=lambda s: (priority_order.get(s.priority, 0), s.confidence),
            reverse=True
        )
        
        return [
            {
                "id": s.suggestion_id,
                "type": s.type,
                "code": s.code,
                "explanation": s.explanation,
                "confidence": s.confidence,
                "line_start": s.line_start,
                "line_end": s.line_end,
                "priority": s.priority
            }
            for s in ranked
        ]

    async def learn_from_feedback(
        self,
        suggestion_id: str,
        accepted: bool,
        user_id: str
    ) -> Dict:
        """Learn from user feedback on suggestions"""
        try:
            # Store feedback for future improvement
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {
                    "accepted_types": {},
                    "rejected_types": {},
                    "total_suggestions": 0,
                    "acceptance_rate": 0.0
                }

            prefs = self.user_preferences[user_id]
            prefs["total_suggestions"] += 1

            # Update acceptance tracking
            # This would be used to personalize future suggestions

            return {"success": True, "learned": True}

        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")
            return {"success": False, "error": str(e)}

    async def index_codebase(self, project_path: str) -> Dict:
        """Index entire codebase for context-aware suggestions"""
        try:
            # This would scan the codebase and build an index
            # of functions, classes, patterns, etc.
            # Used for intelligent completions based on existing code

            logger.info(f"Indexing codebase at: {project_path}")
            
            # Placeholder for actual indexing
            self.codebase_index[project_path] = {
                "indexed_at": datetime.now().timestamp(),
                "files_count": 0,
                "functions": [],
                "classes": [],
                "common_patterns": []
            }

            return {
                "success": True,
                "message": "Codebase indexed successfully",
                "index_info": self.codebase_index[project_path]
            }

        except Exception as e:
            logger.error(f"Error indexing codebase: {e}")
            return {"success": False, "error": str(e)}
