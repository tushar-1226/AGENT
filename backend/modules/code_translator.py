"""
Code Translator - Multi-Language Code Translation
Translates code between programming languages while preserving logic
"""

import logging
import re
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class CodeTranslator:
    """Multi-language code translation engine"""
    
    # Supported language mappings
    SUPPORTED_LANGUAGES = {
        "python": ["javascript", "typescript", "go"],
        "javascript": ["python", "typescript"],
        "typescript": ["python", "javascript"],
        "go": ["python"],
    }
    
    def __init__(self, gemini_processor=None):
        """
        Initialize code translator
        
        Args:
            gemini_processor: Gemini AI processor for translation
        """
        self.gemini = gemini_processor
        self.translation_cache = {}
        logger.info("Code Translator initialized")
    
    async def translate_code(
        self,
        source_code: str,
        source_language: str,
        target_language: str,
        preserve_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Translate code from one language to another
        
        Args:
            source_code: Source code to translate
            source_language: Source programming language
            target_language: Target programming language
            preserve_comments: Whether to preserve comments
            
        Returns:
            Translation result with code, confidence, and notes
        """
        try:
            # Validate languages
            if not self._validate_translation(source_language, target_language):
                return {
                    "success": False,
                    "error": f"Translation from {source_language} to {target_language} not supported"
                }
            
            # Check cache
            cache_key = self._get_cache_key(source_code, source_language, target_language)
            if cache_key in self.translation_cache:
                logger.info("Returning cached translation")
                return self.translation_cache[cache_key]
            
            # Perform translation
            result = await self._perform_translation(
                source_code, source_language, target_language, preserve_comments
            )
            
            # Cache result
            self.translation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error translating code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_translation(self, source: str, target: str) -> bool:
        """Validate if translation is supported"""
        source = source.lower()
        target = target.lower()
        
        if source == target:
            return False
        
        return (source in self.SUPPORTED_LANGUAGES and 
                target in self.SUPPORTED_LANGUAGES.get(source, []))
    
    def _get_cache_key(self, code: str, source: str, target: str) -> str:
        """Generate cache key for translation"""
        import hashlib
        code_hash = hashlib.md5(code.encode()).hexdigest()
        return f"{source}_{target}_{code_hash}"
    
    async def _perform_translation(
        self,
        source_code: str,
        source_language: str,
        target_language: str,
        preserve_comments: bool
    ) -> Dict[str, Any]:
        """Perform the actual translation"""
        
        if not self.gemini:
            return {
                "success": False,
                "error": "Gemini AI not available for translation"
            }
        
        try:
            # Build translation prompt
            prompt = self._build_translation_prompt(
                source_code, source_language, target_language, preserve_comments
            )
            
            # Get translation from Gemini
            response = await self.gemini.generate_content(prompt)
            
            # Parse response
            translated_code = self._extract_code_from_response(response, target_language)
            
            # Generate translation notes
            notes = self._generate_translation_notes(
                source_code, translated_code, source_language, target_language
            )
            
            return {
                "success": True,
                "source_language": source_language,
                "target_language": target_language,
                "source_code": source_code,
                "translated_code": translated_code,
                "confidence": 0.9,  # Could be calculated based on complexity
                "notes": notes,
                "warnings": self._check_translation_warnings(
                    source_language, target_language
                )
            }
            
        except Exception as e:
            logger.error(f"Error in translation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_translation_prompt(
        self,
        source_code: str,
        source_language: str,
        target_language: str,
        preserve_comments: bool
    ) -> str:
        """Build prompt for Gemini translation"""
        
        prompt = f"""You are an expert programmer in both {source_language} and {target_language}.

Translate the following {source_language} code to {target_language}.

IMPORTANT RULES:
1. Preserve the exact same logic and functionality
2. Use idiomatic {target_language} patterns and conventions
3. Maintain code structure where possible
4. {"Preserve all comments" if preserve_comments else "Remove comments"}
5. Add type hints/annotations if the target language supports them
6. Handle language-specific features appropriately

Source Code ({source_language}):
```{source_language}
{source_code}
```

Provide ONLY the translated {target_language} code in a code block, no explanations:
```{target_language}
"""
        
        return prompt
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from Gemini response"""
        
        # Try to find code block
        pattern = f"```{language}\\s*\\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Try generic code block
        pattern = r"```\s*\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Return full response if no code block found
        return response.strip()
    
    def _generate_translation_notes(
        self,
        source_code: str,
        translated_code: str,
        source_language: str,
        target_language: str
    ) -> List[str]:
        """Generate notes about the translation"""
        
        notes = []
        
        # Language-specific notes
        if source_language == "python" and target_language in ["javascript", "typescript"]:
            if "async def" in source_code:
                notes.append("Python async/await translated to JavaScript async/await")
            if "with " in source_code:
                notes.append("Python context managers may need manual resource cleanup in JavaScript")
            if "list comprehension" in source_code or "[" in source_code and "for" in source_code:
                notes.append("List comprehensions translated to array methods (map, filter, etc.)")
        
        elif source_language in ["javascript", "typescript"] and target_language == "python":
            if "const " in source_code or "let " in source_code:
                notes.append("JavaScript const/let translated to Python variables")
            if "=>" in source_code:
                notes.append("Arrow functions translated to Python lambda or def")
        
        return notes
    
    def _check_translation_warnings(
        self, source_language: str, target_language: str
    ) -> List[str]:
        """Check for potential translation warnings"""
        
        warnings = []
        
        # Language-specific warnings
        if source_language == "python" and target_language == "go":
            warnings.append("Python's dynamic typing translated to Go's static typing - review type declarations")
            warnings.append("Python exceptions translated to Go error handling - verify error checks")
        
        if source_language == "javascript" and target_language == "python":
            warnings.append("JavaScript's prototype-based OOP translated to Python's class-based OOP")
        
        return warnings
    
    def detect_language(self, code: str) -> Optional[str]:
        """
        Detect programming language from code
        
        Args:
            code: Code snippet
            
        Returns:
            Detected language or None
        """
        # Simple heuristic-based detection
        
        # Python indicators
        if re.search(r'\bdef\s+\w+\s*\(', code) and re.search(r':\s*$', code, re.MULTILINE):
            return "python"
        
        # JavaScript/TypeScript indicators
        if re.search(r'\b(const|let|var)\s+\w+', code):
            if re.search(r':\s*\w+\s*=', code):  # Type annotations
                return "typescript"
            return "javascript"
        
        # Go indicators
        if re.search(r'\bfunc\s+\w+\s*\(', code) and re.search(r'\bpackage\s+\w+', code):
            return "go"
        
        return None
    
    def get_supported_languages(self) -> Dict[str, List[str]]:
        """Get all supported language translations"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get translator statistics"""
        return {
            "cache_size": len(self.translation_cache),
            "supported_languages": list(self.SUPPORTED_LANGUAGES.keys()),
            "has_gemini": self.gemini is not None
        }
