"""
Code Predictor - Predictive Code Completion with RAG Context
Provides intelligent code suggestions based on codebase patterns and context
"""

import logging
from typing import List, Dict, Optional, Any
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class CodePredictor:
    """Predictive code completion engine with RAG integration"""
    
    def __init__(self, gemini_processor=None, rag_engine=None):
        """
        Initialize code predictor
        
        Args:
            gemini_processor: Gemini AI processor for predictions
            rag_engine: RAG engine for context search
        """
        self.gemini = gemini_processor
        self.rag = rag_engine
        self.prediction_cache = {}
        logger.info("Code Predictor initialized")
    
    async def predict_code(
        self,
        current_code: str,
        cursor_position: int,
        file_path: Optional[str] = None,
        language: str = "python",
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Predict code completions based on context
        
        Args:
            current_code: Current code in editor
            cursor_position: Cursor position in code
            file_path: Path to current file
            language: Programming language
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of prediction objects with code, confidence, and explanation
        """
        try:
            # Extract context around cursor
            context = self._extract_context(current_code, cursor_position)
            
            # Search RAG for similar patterns
            similar_patterns = await self._find_similar_patterns(
                context, language
            )
            
            # Generate predictions using Gemini
            predictions = await self._generate_predictions(
                context, similar_patterns, language, max_suggestions
            )
            
            # Rank predictions by confidence
            ranked_predictions = self._rank_predictions(predictions)
            
            return ranked_predictions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error predicting code: {e}")
            return []
    
    def _extract_context(
        self, code: str, cursor_position: int, context_lines: int = 10
    ) -> Dict[str, Any]:
        """
        Extract relevant context around cursor position
        
        Args:
            code: Full code content
            cursor_position: Cursor position
            context_lines: Number of lines before/after cursor
            
        Returns:
            Context dictionary with code snippets and metadata
        """
        lines = code.split('\n')
        
        # Find cursor line
        char_count = 0
        cursor_line = 0
        for i, line in enumerate(lines):
            if char_count + len(line) + 1 >= cursor_position:
                cursor_line = i
                break
            char_count += len(line) + 1
        
        # Extract context lines
        start_line = max(0, cursor_line - context_lines)
        end_line = min(len(lines), cursor_line + context_lines)
        
        before_cursor = '\n'.join(lines[start_line:cursor_line])
        current_line = lines[cursor_line] if cursor_line < len(lines) else ""
        after_cursor = '\n'.join(lines[cursor_line + 1:end_line])
        
        # Detect current scope (function, class, etc.)
        scope = self._detect_scope(lines, cursor_line)
        
        # Extract imports
        imports = self._extract_imports(lines)
        
        return {
            "before_cursor": before_cursor,
            "current_line": current_line,
            "after_cursor": after_cursor,
            "cursor_line": cursor_line,
            "scope": scope,
            "imports": imports,
            "indentation": self._get_indentation(current_line)
        }
    
    def _detect_scope(self, lines: List[str], cursor_line: int) -> Dict[str, str]:
        """Detect current scope (function, class, module)"""
        scope = {
            "type": "module",
            "name": "",
            "parent": ""
        }
        
        # Look backwards for function/class definitions
        for i in range(cursor_line, -1, -1):
            line = lines[i].strip()
            
            # Check for function
            if line.startswith("def "):
                match = re.match(r'def\s+(\w+)', line)
                if match:
                    scope["type"] = "function"
                    scope["name"] = match.group(1)
                    break
            
            # Check for class
            elif line.startswith("class "):
                match = re.match(r'class\s+(\w+)', line)
                if match:
                    if scope["type"] == "function":
                        scope["parent"] = match.group(1)
                    else:
                        scope["type"] = "class"
                        scope["name"] = match.group(1)
                    break
        
        return scope
    
    def _extract_imports(self, lines: List[str]) -> List[str]:
        """Extract import statements from code"""
        imports = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return imports
    
    def _get_indentation(self, line: str) -> str:
        """Get indentation of current line"""
        match = re.match(r'^(\s*)', line)
        return match.group(1) if match else ""
    
    async def _find_similar_patterns(
        self, context: Dict[str, Any], language: str
    ) -> List[Dict[str, Any]]:
        """
        Find similar code patterns in RAG database
        
        Args:
            context: Code context
            language: Programming language
            
        Returns:
            List of similar code patterns
        """
        if not self.rag:
            return []
        
        try:
            # Create search query from context
            query = f"{context['before_cursor']}\n{context['current_line']}"
            
            # Search RAG database
            results = await self.rag.query(
                query=query,
                n_results=5,
                filter_metadata={"language": language}
            )
            
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error finding similar patterns: {e}")
            return []
    
    async def _generate_predictions(
        self,
        context: Dict[str, Any],
        similar_patterns: List[Dict[str, Any]],
        language: str,
        max_suggestions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate code predictions using Gemini
        
        Args:
            context: Code context
            similar_patterns: Similar code from RAG
            language: Programming language
            max_suggestions: Maximum suggestions to generate
            
        Returns:
            List of predictions
        """
        if not self.gemini:
            return self._generate_basic_predictions(context, language)
        
        try:
            # Build prompt for Gemini
            prompt = self._build_prediction_prompt(
                context, similar_patterns, language, max_suggestions
            )
            
            # Get predictions from Gemini
            response = await self.gemini.generate_content(prompt)
            
            # Parse predictions from response
            predictions = self._parse_predictions(response, context)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return self._generate_basic_predictions(context, language)
    
    def _build_prediction_prompt(
        self,
        context: Dict[str, Any],
        similar_patterns: List[Dict[str, Any]],
        language: str,
        max_suggestions: int
    ) -> str:
        """Build prompt for Gemini prediction"""
        
        similar_code = "\n\n".join([
            f"Example {i+1}:\n{pattern.get('code', '')}"
            for i, pattern in enumerate(similar_patterns[:3])
        ])
        
        prompt = f"""You are an expert {language} programmer. Predict the next lines of code based on the context.

Current Code Context:
```{language}
{context['before_cursor']}
{context['current_line']}  <-- CURSOR HERE
{context['after_cursor']}
```

Current Scope: {context['scope']['type']} {context['scope']['name']}
Imports: {', '.join(context['imports'][:5])}

Similar Code Patterns from Codebase:
{similar_code if similar_code else "No similar patterns found"}

Generate {max_suggestions} intelligent code completion suggestions.
For each suggestion, provide:
1. The code to insert (maintain proper indentation: "{context['indentation']}")
2. Confidence score (0.0-1.0)
3. Brief explanation

Format as JSON array:
[
  {{
    "code": "suggested code here",
    "confidence": 0.95,
    "explanation": "Brief explanation"
  }}
]

Only return valid JSON, no additional text."""
        
        return prompt
    
    def _parse_predictions(
        self, response: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse predictions from Gemini response"""
        import json
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                predictions = json.loads(json_match.group(0))
                
                # Add metadata to each prediction
                for pred in predictions:
                    pred["type"] = "ai_generated"
                    pred["indentation"] = context["indentation"]
                
                return predictions
            
        except Exception as e:
            logger.error(f"Error parsing predictions: {e}")
        
        return []
    
    def _generate_basic_predictions(
        self, context: Dict[str, Any], language: str
    ) -> List[Dict[str, Any]]:
        """Generate basic predictions without AI (fallback)"""
        predictions = []
        
        current_line = context["current_line"].strip()
        indent = context["indentation"]
        
        # Basic Python predictions
        if language == "python":
            if current_line.startswith("def "):
                predictions.append({
                    "code": f'{indent}    """TODO: Add docstring"""',
                    "confidence": 0.7,
                    "explanation": "Add docstring to function",
                    "type": "template"
                })
            
            elif current_line.startswith("class "):
                predictions.append({
                    "code": f'{indent}    def __init__(self):',
                    "confidence": 0.8,
                    "explanation": "Add constructor",
                    "type": "template"
                })
            
            elif "if " in current_line and current_line.endswith(":"):
                predictions.append({
                    "code": f'{indent}    pass',
                    "confidence": 0.6,
                    "explanation": "Add pass statement",
                    "type": "template"
                })
        
        return predictions
    
    def _rank_predictions(
        self, predictions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank predictions by confidence score"""
        return sorted(
            predictions,
            key=lambda x: x.get("confidence", 0.0),
            reverse=True
        )
    
    async def learn_from_acceptance(
        self, prediction: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """
        Learn from accepted predictions to improve future suggestions
        
        Args:
            prediction: Accepted prediction
            context: Context where prediction was accepted
            
        Returns:
            Success status
        """
        try:
            # Store accepted pattern in RAG if available
            if self.rag:
                code_snippet = f"{context['before_cursor']}\n{prediction['code']}"
                
                await self.rag.add_document(
                    content=code_snippet,
                    metadata={
                        "type": "accepted_prediction",
                        "confidence": prediction.get("confidence", 0.0),
                        "scope": context.get("scope", {}).get("type", "unknown")
                    }
                )
            
            logger.info("Learned from accepted prediction")
            return True
            
        except Exception as e:
            logger.error(f"Error learning from acceptance: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get predictor statistics"""
        return {
            "cache_size": len(self.prediction_cache),
            "has_gemini": self.gemini is not None,
            "has_rag": self.rag is not None
        }
