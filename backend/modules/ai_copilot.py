"""
AI Code Copilot Module
Provides real-time code suggestions, context-aware completions, and function signature help
Enhanced with AI-powered suggestions, error detection, and intelligent code analysis
"""

import os
import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Optional AI integration
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_AVAILABLE = bool(os.getenv('GEMINI_API_KEY'))
    if GEMINI_AVAILABLE:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    GEMINI_AVAILABLE = False

# OpenRouter integration
try:
    from modules.openrouter_integration import OpenRouterAPI
    OPENROUTER_AVAILABLE = bool(os.getenv('OPENROUTER_API_KEY'))
except ImportError:
    OPENROUTER_AVAILABLE = False


class AICopilot:
    """AI-powered code completion and suggestions with advanced features"""
    
    def __init__(self):
        self.gemini_model = None
        self.openrouter = None
        self.ai_provider = None  # Track which AI is active
        
        # Try Gemini first
        if GEMINI_AVAILABLE:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.ai_provider = 'gemini'
                logger.info("✅ Gemini AI integration enabled for enhanced copilot features")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        
        # Fallback to OpenRouter if Gemini fails
        if not self.ai_provider and OPENROUTER_AVAILABLE:
            try:
                self.openrouter = OpenRouterAPI()
                self.ai_provider = 'openrouter'
                logger.info("✅ OpenRouter AI integration enabled as fallback for copilot features")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenRouter: {e}")
        
        if not self.ai_provider:
            logger.warning("⚠️  No AI provider available - using pattern-based suggestions only")
        
        # Cache for code analysis
        self.project_context_cache = {}
        self.file_analysis_cache = {}
        
        self.language_patterns = {
            'python': {
                'imports': [
                    'import numpy as np',
                    'import pandas as pd',
                    'from typing import List, Dict, Optional',
                    'import logging',
                    'from datetime import datetime',
                ],
                'common_patterns': {
                    'class': 'class {name}:\n    """Docstring"""\n    \n    def __init__(self):\n        pass',
                    'function': 'def {name}(self, {params}):\n    """Docstring"""\n    pass',
                    'async_function': 'async def {name}(self, {params}):\n    """Docstring"""\n    pass',
                    'try_except': 'try:\n    {code}\nexcept Exception as e:\n    logger.error(f"Error: {e}")',
                    'with_open': 'with open({file}, "r") as f:\n    {code}',
                },
                'signatures': {
                    'print': 'print(*values, sep=" ", end="\\n", file=sys.stdout, flush=False)',
                    'open': 'open(file, mode="r", buffering=-1, encoding=None)',
                    'range': 'range(stop) or range(start, stop[, step])',
                    'len': 'len(s) -> int',
                }
            },
            'javascript': {
                'imports': [
                    'import React from "react";',
                    'import { useState, useEffect } from "react";',
                    'import axios from "axios";',
                ],
                'common_patterns': {
                    'function': 'function {name}({params}) {\n  {code}\n}',
                    'arrow': 'const {name} = ({params}) => {\n  {code}\n};',
                    'async': 'async function {name}({params}) {\n  {code}\n}',
                    'component': 'const {name} = () => {\n  return (\n    <div>{code}</div>\n  );\n};',
                    'try_catch': 'try {\n  {code}\n} catch (error) {\n  console.error(error);\n}',
                },
                'signatures': {
                    'console.log': 'console.log(...data: any[]): void',
                    'setTimeout': 'setTimeout(callback: Function, delay: number): number',
                    'fetch': 'fetch(input: RequestInfo, init?: RequestInit): Promise<Response>',
                }
            },
            'typescript': {
                'imports': [
                    'import React from "react";',
                    'import { FC } from "react";',
                    'import type { } from "";',
                ],
                'common_patterns': {
                    'interface': 'interface {name} {\n  {properties}\n}',
                    'type': 'type {name} = {\n  {properties}\n};',
                    'function': 'function {name}({params}): {return} {\n  {code}\n}',
                    'component': 'const {name}: FC = () => {\n  return (\n    <div>{code}</div>\n  );\n};',
                },
                'signatures': {}
            }
        }
        
        # Error patterns for detection
        self.error_patterns = {
            'python': [
                (r'print\s+[^(]', 'Missing parentheses in print statement (Python 3)'),
                (r'except\s*:', 'Bare except clause - consider catching specific exceptions'),
                (r'==\s*None', 'Use "is None" instead of "== None"'),
                (r'!=\s*None', 'Use "is not None" instead of "!= None"'),
                (r'[\w\s]+\s*=\s*\[\s*\].*\.append', 'Consider using list comprehension'),
            ],
            'javascript': [
                (r'var\s+', 'Consider using "let" or "const" instead of "var"'),
                (r'==(?!=)', 'Consider using strict equality "===" instead of "=="'),
                (r'!=(?!=)', 'Consider using strict inequality "!==" instead of "!="'),
            ]
        }
        
        # Code quality suggestions
        self.quality_patterns = {
            'python': {
                'missing_docstring': r'^(?:def|class)\s+\w+[^:]*:\s*(?!"""|\'\'\')(?!\s*#)',
                'long_line': lambda line: len(line) > 100,
                'complex_condition': r'if\s+.*(?:and|or).*(?:and|or).*:',
            }
        }
        
    def get_completions(self, code: str, cursor_position: int, language: str = 'python', 
                       file_path: str = None, project_path: str = None) -> List[Dict]:
        """
        Get code completion suggestions based on context
        Enhanced with AI-powered suggestions and project-wide context
        """
        try:
            # Get context around cursor
            before_cursor = code[:cursor_position]
            after_cursor = code[cursor_position:]
            
            # Get current line
            lines = before_cursor.split('\n')
            current_line = lines[-1] if lines else ''
            
            suggestions = []
            
            # Priority 1: AI-powered intelligent suggestions (if available)
            if self.gemini_model and len(current_line.strip()) > 3:
                ai_suggestions = self._get_ai_suggestions(
                    code, cursor_position, current_line, language, before_cursor
                )
                suggestions.extend(ai_suggestions[:5])  # Top 5 AI suggestions
            
            # Priority 2: Context-aware suggestions
            context_suggestions = self._get_context_aware_suggestions(
                code, current_line, language, file_path, project_path
            )
            suggestions.extend(context_suggestions)
            
            # Priority 3: Check for import suggestions
            if current_line.strip().startswith('import') or current_line.strip().startswith('from'):
                suggestions.extend(self._get_import_suggestions(current_line, language))
            
            # Priority 4: Check for function/method suggestions
            if '.' in current_line:
                suggestions.extend(self._get_method_suggestions(current_line, language, code))
            
            # Priority 5: Check for keyword suggestions
            suggestions.extend(self._get_keyword_suggestions(current_line, language))
            
            # Priority 6: Add common patterns
            suggestions.extend(self._get_pattern_suggestions(current_line, language))
            
            # Priority 7: Variable and function suggestions from current file
            suggestions.extend(self._get_defined_symbols(code, current_line, language))
            
            # Remove duplicates and sort by score
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            sorted_suggestions = sorted(unique_suggestions, key=lambda x: x.get('score', 0), reverse=True)
            
            return sorted_suggestions[:20]  # Return top 20
            
        except Exception as e:
            logger.error(f"Error getting completions: {e}")
            return []
    
    def get_signature_help(self, code: str, cursor_position: int, language: str = 'python') -> Optional[Dict]:
        """Get function signature help"""
        try:
            before_cursor = code[:cursor_position]
            
            # Find the current function call
            match = re.search(r'(\w+)\s*\([^)]*$', before_cursor)
            if not match:
                return None
            
            function_name = match.group(1)
            lang_config = self.language_patterns.get(language, {})
            signatures = lang_config.get('signatures', {})
            
            if function_name in signatures:
                return {
                    'function': function_name,
                    'signature': signatures[function_name],
                    'active_parameter': self._get_active_parameter(before_cursor)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting signature help: {e}")
            return None
    
    def get_context_suggestions(self, code: str, file_path: str, language: str = 'python') -> List[Dict]:
        """Get context-aware suggestions based on entire file"""
        try:
            suggestions = []
            
            # Analyze imports
            imports = self._extract_imports(code, language)
            
            # Analyze defined functions/classes
            definitions = self._extract_definitions(code, language)
            
            # Suggest missing imports
            suggestions.extend(self._suggest_missing_imports(code, language))
            
            # Suggest related functions
            suggestions.extend(self._suggest_related_functions(code, definitions, language))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting context suggestions: {e}")
            return []
    
    def _get_import_suggestions(self, line: str, language: str) -> List[Dict]:
        """Get import suggestions"""
        suggestions = []
        lang_config = self.language_patterns.get(language, {})
        imports = lang_config.get('imports', [])
        
        for imp in imports:
            suggestions.append({
                'type': 'import',
                'label': imp,
                'insert_text': imp,
                'detail': 'Common import',
                'score': 0.9
            })
        
        return suggestions
    
    def _get_method_suggestions(self, line: str, language: str, full_code: str = '') -> List[Dict]:
        """Get method suggestions for objects with enhanced type inference"""
        suggestions = []
        
        # Extract object before dot
        match = re.search(r'(\w+)\.$', line)
        if match:
            obj_name = match.group(1)
            
            # Try to infer type from code context
            inferred_type = self._infer_variable_type(obj_name, full_code, language)
            
            # Common methods based on object patterns
            if language == 'python':
                if inferred_type == 'list' or obj_name in ['list', 'arr', 'items', 'data']:
                    methods = [
                        ('append', 'append(item)', 'Add item to end'),
                        ('extend', 'extend(iterable)', 'Extend list'),
                        ('insert', 'insert(index, item)', 'Insert at index'),
                        ('remove', 'remove(item)', 'Remove first occurrence'),
                        ('pop', 'pop(index=-1)', 'Remove and return item'),
                        ('sort', 'sort(key=None, reverse=False)', 'Sort list'),
                        ('reverse', 'reverse()', 'Reverse list'),
                        ('count', 'count(item)', 'Count occurrences'),
                        ('index', 'index(item)', 'Find index'),
                        ('clear', 'clear()', 'Remove all items'),
                    ]
                elif inferred_type == 'dict' or obj_name in ['dict', 'obj', 'config', 'params']:
                    methods = [
                        ('get', 'get(key, default=None)', 'Get value safely'),
                        ('keys', 'keys()', 'Get all keys'),
                        ('values', 'values()', 'Get all values'),
                        ('items', 'items()', 'Get key-value pairs'),
                        ('update', 'update(dict)', 'Update dictionary'),
                        ('pop', 'pop(key, default)', 'Remove and return'),
                        ('setdefault', 'setdefault(key, default)', 'Get or set default'),
                        ('clear', 'clear()', 'Remove all items'),
                    ]
                elif inferred_type == 'str' or obj_name in ['str', 'text', 'name', 'msg', 'message']:
                    methods = [
                        ('split', 'split(sep=None)', 'Split string'),
                        ('strip', 'strip(chars=None)', 'Remove whitespace'),
                        ('replace', 'replace(old, new)', 'Replace substring'),
                        ('upper', 'upper()', 'Convert to uppercase'),
                        ('lower', 'lower()', 'Convert to lowercase'),
                        ('startswith', 'startswith(prefix)', 'Check prefix'),
                        ('endswith', 'endswith(suffix)', 'Check suffix'),
                        ('join', 'join(iterable)', 'Join strings'),
                        ('format', 'format(*args, **kwargs)', 'Format string'),
                        ('find', 'find(sub)', 'Find substring'),
                    ]
                elif inferred_type == 'set':
                    methods = [
                        ('add', 'add(item)', 'Add element'),
                        ('remove', 'remove(item)', 'Remove element'),
                        ('discard', 'discard(item)', 'Remove if present'),
                        ('union', 'union(other)', 'Set union'),
                        ('intersection', 'intersection(other)', 'Set intersection'),
                        ('difference', 'difference(other)', 'Set difference'),
                    ]
                else:
                    # Generic object methods
                    methods = [
                        ('__str__', '__str__()', 'String representation'),
                        ('__repr__', '__repr__()', 'Official representation'),
                    ]
                
                for method, signature, description in methods:
                    suggestions.append({
                        'type': 'method',
                        'label': method,
                        'insert_text': f'{method}()',
                        'detail': signature,
                        'documentation': description,
                        'score': 0.9
                    })
        
        return suggestions
    
    def _get_keyword_suggestions(self, line: str, language: str) -> List[Dict]:
        """Get keyword suggestions"""
        suggestions = []
        
        keywords = {
            'python': ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'import', 'from', 'return', 'yield', 'async', 'await'],
            'javascript': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'try', 'catch', 'return', 'async', 'await', 'import', 'export'],
            'typescript': ['interface', 'type', 'function', 'const', 'let', 'if', 'else', 'for', 'while', 'try', 'catch', 'return', 'async', 'await']
        }
        
        lang_keywords = keywords.get(language, [])
        current_word = line.split()[-1] if line.split() else ''
        
        for keyword in lang_keywords:
            if keyword.startswith(current_word.lower()):
                suggestions.append({
                    'type': 'keyword',
                    'label': keyword,
                    'insert_text': keyword,
                    'detail': 'Keyword',
                    'score': 0.8
                })
        
        return suggestions
    
    def _get_pattern_suggestions(self, line: str, language: str) -> List[Dict]:
        """Get common pattern suggestions"""
        suggestions = []
        lang_config = self.language_patterns.get(language, {})
        patterns = lang_config.get('common_patterns', {})
        
        for pattern_name, pattern_code in patterns.items():
            suggestions.append({
                'type': 'snippet',
                'label': pattern_name,
                'insert_text': pattern_code,
                'detail': f'Pattern: {pattern_name}',
                'score': 0.7
            })
        
        return suggestions
    
    def _get_active_parameter(self, code: str) -> int:
        """Get the active parameter index in function call"""
        # Count commas after opening parenthesis
        match = re.search(r'\([^)]*$', code)
        if match:
            param_text = match.group(0)
            return param_text.count(',')
        return 0
    
    def _extract_imports(self, code: str, language: str) -> List[str]:
        """Extract imports from code"""
        imports = []
        
        if language == 'python':
            import_pattern = r'^(?:import|from)\s+[\w.]+'
        elif language in ['javascript', 'typescript']:
            import_pattern = r'^import\s+.*from\s+["\'].*["\']'
        else:
            return imports
        
        for line in code.split('\n'):
            if re.match(import_pattern, line.strip()):
                imports.append(line.strip())
        
        return imports
    
    def _extract_definitions(self, code: str, language: str) -> List[Dict]:
        """Extract function and class definitions"""
        definitions = []
        
        if language == 'python':
            # Extract functions
            func_pattern = r'def\s+(\w+)\s*\('
            for match in re.finditer(func_pattern, code):
                definitions.append({
                    'type': 'function',
                    'name': match.group(1)
                })
            
            # Extract classes
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, code):
                definitions.append({
                    'type': 'class',
                    'name': match.group(1)
                })
        
        return definitions
    
    def _suggest_missing_imports(self, code: str, language: str) -> List[Dict]:
        """Suggest missing imports based on code usage"""
        suggestions = []
        
        if language == 'python':
            # Check for common library usage without imports
            patterns = {
                r'\bnp\.': 'import numpy as np',
                r'\bpd\.': 'import pandas as pd',
                r'\bplt\.': 'import matplotlib.pyplot as plt',
                r'\brequests\.': 'import requests',
            }
            
            current_imports = self._extract_imports(code, language)
            
            for pattern, import_statement in patterns.items():
                if re.search(pattern, code) and import_statement not in current_imports:
                    suggestions.append({
                        'type': 'import',
                        'label': import_statement,
                        'insert_text': import_statement,
                        'detail': 'Missing import',
                        'score': 0.95
                    })
        
        return suggestions
    
    def _suggest_related_functions(self, code: str, definitions: List[Dict], language: str) -> List[Dict]:
        """Suggest related functions based on context"""
        suggestions = []
        
        # Add defined functions as suggestions
        for definition in definitions:
            suggestions.append({
                'type': definition['type'],
                'label': definition['name'],
                'insert_text': definition['name'],
                'detail': f'{definition["type"]}: {definition["name"]}',
                'score': 0.9
            })
        
        return suggestions
    
    # ============ ENHANCED FEATURES ============
    
    def _get_ai_suggestions(self, code: str, cursor_pos: int, current_line: str, 
                           language: str, before_cursor: str) -> List[Dict]:
        """Get AI-powered intelligent code suggestions using Gemini or OpenRouter"""
        # Try Gemini first
        if self.gemini_model:
            try:
                return self._get_gemini_suggestions(code, cursor_pos, current_line, language, before_cursor)
            except Exception as e:
                logger.debug(f"Gemini suggestions failed, trying OpenRouter: {e}")
        
        # Fallback to OpenRouter
        if self.openrouter:
            return self._get_openrouter_suggestions(code, cursor_pos, current_line, language, before_cursor)
        
        return []
    
    def _get_gemini_suggestions(self, code: str, cursor_pos: int, current_line: str,
                               language: str, before_cursor: str) -> List[Dict]:
        """Get suggestions from Gemini"""
        if not self.gemini_model:
            return []
        
        try:
            # Create context for AI
            lines = before_cursor.split('\n')
            context_lines = lines[-10:] if len(lines) > 10 else lines  # Last 10 lines
            context = '\n'.join(context_lines)
            
            prompt = f"""You are an expert {language} code completion AI. Given the code context, suggest the most likely code continuation.

Context:
```{language}
{context}
```

Current incomplete line: {current_line}

Provide 3-5 highly relevant code completions. Return ONLY a JSON array with this structure:
[{{"text": "suggested_code", "type": "function|variable|keyword|method", "description": "brief explanation", "confidence": 0.0-1.0}}]

Focus on:
- Variable/function names from context
- Common {language} patterns
- Logical next steps based on code flow

Return only the JSON array, no other text."""

            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if result_text.startswith('```'):
                result_text = re.sub(r'```json?\n?', '', result_text)
                result_text = re.sub(r'\n?```', '', result_text)
            
            suggestions_data = json.loads(result_text)
            
            # Convert to our format
            suggestions = []
            for item in suggestions_data[:5]:
                suggestions.append({
                    'type': item.get('type', 'ai'),
                    'label': item['text'],
                    'insert_text': item['text'],
                    'detail': item.get('description', 'AI suggestion'),
                    'documentation': f"AI-powered suggestion (confidence: {item.get('confidence', 0.8):.0%})",
                    'score': 0.95 * item.get('confidence', 0.8),
                    'source': 'ai'
                })
            
            return suggestions
            
        except Exception as e:
            logger.debug(f"AI suggestions failed: {e}")
            return []
    
    def _get_openrouter_suggestions(self, code: str, cursor_pos: int, current_line: str,
                                   language: str, before_cursor: str) -> List[Dict]:
        """Get AI-powered suggestions using OpenRouter as fallback"""
        if not self.openrouter:
            return []
        
        try:
            lines = before_cursor.split('\n')
            context_lines = lines[-10:] if len(lines) > 10 else lines
            context = '\n'.join(context_lines)
            
            prompt = f"""Code completion for {language}. Context:
```{language}
{context}
```
Incomplete line: {current_line}

Suggest 3 code completions as JSON array:
[{{"text": "code", "type": "type", "description": "desc", "confidence": 0.9}}]
JSON only."""

            response_text = self.openrouter.simple_query(prompt, model="meta-llama/llama-3.2-3b-instruct:free")
            result_text = response_text.strip()
            
            if result_text.startswith('```'):
                result_text = re.sub(r'```json?\n?', '', result_text)
                result_text = re.sub(r'\n?```', '', result_text)
            
            suggestions_data = json.loads(result_text)
            
            suggestions = []
            for item in suggestions_data[:3]:
                suggestions.append({
                    'type': item.get('type', 'ai'),
                    'label': item['text'],
                    'insert_text': item['text'],
                    'detail': f"🌐 {item.get('description', 'OpenRouter AI')}",
                    'documentation': f"OpenRouter suggestion (confidence: {item.get('confidence', 0.8):.0%})",
                    'score': 0.90 * item.get('confidence', 0.8),
                    'source': 'openrouter'
                })
            
            return suggestions
            
        except Exception as e:
            logger.debug(f"OpenRouter suggestions failed: {e}")
            return []
    
    def _get_context_aware_suggestions(self, code: str, current_line: str, 
                                      language: str, file_path: str = None,
                                      project_path: str = None) -> List[Dict]:
        """Get suggestions based on project and file context"""
        suggestions = []
        
        try:
            # Analyze imports and suggest related items
            if language == 'python':
                # Check if using FastAPI
                if 'from fastapi import' in code or 'import fastapi' in code:
                    if 'router' in current_line.lower() or '@' in current_line:
                        suggestions.append({
                            'type': 'decorator',
                            'label': '@router.get',
                            'insert_text': '@router.get("/")',
                            'detail': 'FastAPI GET endpoint',
                            'score': 0.92
                        })
                        suggestions.append({
                            'type': 'decorator',
                            'label': '@router.post',
                            'insert_text': '@router.post("/")',
                            'detail': 'FastAPI POST endpoint',
                            'score': 0.92
                        })
                
                # Check if using typing
                if 'from typing import' in code:
                    if 'def ' in current_line or '->' in current_line:
                        suggestions.extend([
                            {'type': 'type', 'label': 'List', 'insert_text': 'List', 'detail': 'Type hint', 'score': 0.88},
                            {'type': 'type', 'label': 'Dict', 'insert_text': 'Dict', 'detail': 'Type hint', 'score': 0.88},
                            {'type': 'type', 'label': 'Optional', 'insert_text': 'Optional', 'detail': 'Type hint', 'score': 0.88},
                        ])
                
                # Check for async patterns
                if 'async def' in code or 'await ' in code:
                    if current_line.strip().startswith(''):
                        suggestions.append({
                            'type': 'keyword',
                            'label': 'await',
                            'insert_text': 'await ',
                            'detail': 'Async await',
                            'score': 0.90
                        })
            
            # JavaScript/TypeScript React patterns
            elif language in ['javascript', 'typescript']:
                if 'import React' in code or 'from "react"' in code:
                    if current_line.strip().startswith('const') or current_line.strip().startswith('function'):
                        suggestions.append({
                            'type': 'snippet',
                            'label': 'useState',
                            'insert_text': 'const [state, setState] = useState()',
                            'detail': 'React useState hook',
                            'score': 0.91
                        })
                        suggestions.append({
                            'type': 'snippet',
                            'label': 'useEffect',
                            'insert_text': 'useEffect(() => {\n  \n}, [])',
                            'detail': 'React useEffect hook',
                            'score': 0.91
                        })
        
        except Exception as e:
            logger.debug(f"Context-aware suggestions error: {e}")
        
        return suggestions
    
    def _get_defined_symbols(self, code: str, current_line: str, language: str) -> List[Dict]:
        """Extract and suggest variables and functions defined in current file"""
        suggestions = []
        
        try:
            if language == 'python':
                # Find variable assignments
                var_pattern = r'^(\s*)(\w+)\s*='
                for match in re.finditer(var_pattern, code, re.MULTILINE):
                    var_name = match.group(2)
                    if var_name not in ['self', 'cls'] and len(var_name) > 1:
                        suggestions.append({
                            'type': 'variable',
                            'label': var_name,
                            'insert_text': var_name,
                            'detail': 'Variable from file',
                            'score': 0.85
                        })
                
                # Find function definitions
                func_pattern = r'def\s+(\w+)\s*\('
                for match in re.finditer(func_pattern, code):
                    func_name = match.group(1)
                    if not func_name.startswith('_'):
                        suggestions.append({
                            'type': 'function',
                            'label': func_name,
                            'insert_text': f'{func_name}()',
                            'detail': 'Function from file',
                            'score': 0.87
                        })
                
                # Find class definitions
                class_pattern = r'class\s+(\w+)'
                for match in re.finditer(class_pattern, code):
                    class_name = match.group(1)
                    suggestions.append({
                        'type': 'class',
                        'label': class_name,
                        'insert_text': class_name,
                        'detail': 'Class from file',
                        'score': 0.87
                    })
        
        except Exception as e:
            logger.debug(f"Symbol extraction error: {e}")
        
        return suggestions
    
    def _infer_variable_type(self, var_name: str, code: str, language: str) -> Optional[str]:
        """Infer the type of a variable from code context"""
        try:
            if language == 'python':
                # Look for assignments
                patterns = [
                    (rf'{var_name}\s*=\s*\[', 'list'),
                    (rf'{var_name}\s*=\s*\{{', 'dict'),
                    (rf'{var_name}\s*=\s*set\(', 'set'),
                    (rf'{var_name}\s*=\s*["\']', 'str'),
                    (rf'{var_name}\s*=\s*\(', 'tuple'),
                    (rf'{var_name}\s*:\s*List', 'list'),
                    (rf'{var_name}\s*:\s*Dict', 'dict'),
                    (rf'{var_name}\s*:\s*str', 'str'),
                ]
                
                for pattern, var_type in patterns:
                    if re.search(pattern, code):
                        return var_type
        
        except Exception:
            pass
        
        return None
    
    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Remove duplicate suggestions, keeping highest scored ones"""
        seen = {}
        for suggestion in suggestions:
            label = suggestion.get('label', '')
            if label not in seen or suggestion.get('score', 0) > seen[label].get('score', 0):
                seen[label] = suggestion
        
        return list(seen.values())
    
    def detect_errors(self, code: str, language: str = 'python') -> List[Dict]:
        """Detect potential errors and code quality issues"""
        issues = []
        
        try:
            # Check error patterns
            patterns = self.error_patterns.get(language, [])
            for pattern, message in patterns:
                for match in re.finditer(pattern, code, re.MULTILINE):
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'warning',
                        'line': line_num,
                        'message': message,
                        'severity': 'medium',
                        'start': match.start(),
                        'end': match.end()
                    })
            
            # Python-specific AST analysis
            if language == 'python':
                try:
                    tree = ast.parse(code)
                    
                    # Check for unused imports (simple check)
                    # Check for missing return statements in functions
                    # etc.
                    
                except SyntaxError as e:
                    issues.append({
                        'type': 'error',
                        'line': e.lineno or 0,
                        'message': f'Syntax error: {e.msg}',
                        'severity': 'high'
                    })
            
            # Check code quality patterns
            quality = self.quality_patterns.get(language, {})
            
            # Check for missing docstrings
            if 'missing_docstring' in quality:
                for match in re.finditer(quality['missing_docstring'], code, re.MULTILINE):
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'info',
                        'line': line_num,
                        'message': 'Consider adding a docstring',
                        'severity': 'low'
                    })
        
        except Exception as e:
            logger.error(f"Error detection failed: {e}")
        
        return issues
    
    def get_code_improvements(self, code: str, language: str = 'python') -> List[Dict]:
        """Suggest code improvements and refactoring opportunities"""
        improvements = []
        
        try:
            if self.gemini_model:
                prompt = f"""Analyze this {language} code and suggest improvements. Focus on:
- Code efficiency
- Best practices
- Readability
- Potential bugs

Code:
```{language}
{code[:1000]}  # Limit to first 1000 chars
```

Return a JSON array of improvements:
[{{"type": "efficiency|style|bug|best-practice", "line": line_number, "suggestion": "description", "priority": "high|medium|low"}}]

Return only the JSON array."""

                response = self.gemini_model.generate_content(prompt)
                result = response.text.strip()
                
                if result.startswith('```'):
                    result = re.sub(r'```json?\n?', '', result)
                    result = re.sub(r'\n?```', '', result)
                
                improvements = json.loads(result)
        
        except Exception as e:
            logger.debug(f"Code improvements analysis failed: {e}")
        
        return improvements
    
    def explain_code(self, code_snippet: str, language: str = 'python') -> str:
        """Explain what a code snippet does"""
        if not self.gemini_model:
            return "AI explanation not available. Install google-generativeai and set GEMINI_API_KEY."
        
        try:
            prompt = f"""Explain this {language} code in simple terms:

```{language}
{code_snippet}
```

Provide a clear, concise explanation suitable for developers."""

            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Code explanation failed: {e}")
            return f"Error generating explanation: {str(e)}"


# Global instance
ai_copilot = None


def get_ai_copilot():
    """Get or create AI Copilot instance"""
    global ai_copilot
    if ai_copilot is None:
        ai_copilot = AICopilot()
    return ai_copilot
