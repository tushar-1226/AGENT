"""
OpenRouter Extensions for Existing Modules
Add these methods to gemini_processor.py, ai_copilot.py, and command_processor.py
"""

# ============================================================================
# ADD THESE METHODS TO gemini_processor.py (GeminiProcessor class)
# ============================================================================

def _analyze_with_gemini(self, prompt: str) -> dict:
    """Analyze command using Gemini"""
    try:
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result = json.loads(result_text.strip())
        
        return {
            'success': True,
            'intent': result.get('intent', 'unknown'),
            'app_name': result.get('app_name'),
            'ai_response': result.get('response', ''),
            'raw_response': response.text,
            'provider': 'gemini'
        }
    except Exception as e:
        logger.error(f"Gemini analysis error: {e}")
        # Fallback to OpenRouter if available
        if self.openrouter:
            logger.info("Falling back to OpenRouter")
            return self._analyze_with_openrouter(prompt)
        return {'success': False, 'intent': 'unknown', 'error': str(e)}


def _analyze_with_openrouter(self, prompt: str) -> dict:
    """Analyze command using OpenRouter"""
    try:
        response = self.openrouter.simple_query(prompt)
        
        # Parse JSON response
        result_text = response.strip()
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result = json.loads(result_text.strip())
        
        return {
            'success': True,
            'intent': result.get('intent', 'unknown'),
            'app_name': result.get('app_name'),
            'ai_response': result.get('response', ''),
            'raw_response': response,
            'provider': 'openrouter'
        }
    except Exception as e:
        logger.error(f"OpenRouter analysis error: {e}")
        return {'success': False, 'intent': 'unknown', 'error': str(e)}


def _get_multi_model_response(self, prompt: str) -> dict:
    """Get responses from both Gemini and OpenRouter for comparison"""
    try:
        gemini_result = self._analyze_with_gemini(prompt) if self.model else None
        openrouter_result = self._analyze_with_openrouter(prompt) if self.openrouter else None
        
        return {
            'gemini': gemini_result,
            'openrouter': openrouter_result,
            'comparison': {
                'gemini_intent': gemini_result.get('intent') if gemini_result else None,
                'openrouter_intent': openrouter_result.get('intent') if openrouter_result else None,
                'match': gemini_result.get('intent') == openrouter_result.get('intent') if (gemini_result and openrouter_result) else None
            }
        }
    except Exception as e:
        logger.error(f"Multi-model comparison error: {e}")
        return {'error': str(e)}


# ============================================================================
# ADD THESE METHODS TO ai_copilot.py (AICopilot class)
# ============================================================================

def _get_openrouter_suggestions(self, code: str, cursor_position: int, language: str,
                               context: str = "", max_suggestions: int = 5) -> List[Dict]:
    """Get suggestions from OpenRouter"""
    try:
        # Extract relevant code around cursor
        lines = code.split('\\n')
        current_line_idx = code[:cursor_position].count('\\n')
        current_line = lines[current_line_idx] if current_line_idx < len(lines) else ""
        
        # Get context (previous 5 lines)
        start_idx = max(0, current_line_idx - 5)
        context_lines = lines[start_idx:current_line_idx + 1]
        code_context = '\\n'.join(context_lines)
        
        prompt = f\"\"\"You are an AI code completion assistant. Given this {language} code context:

```{language}
{code_context}
```

Current incomplete line: `{current_line}`

Provide {max_suggestions} intelligent code completions. Consider:
- Language syntax and idioms
- Common patterns
- Variable names and types
- Function signatures

Respond with ONLY a JSON array of completions:
[
  {{"completion": "suggestion 1", "description": "brief description", "priority": 90}},
  {{"completion": "suggestion 2", "description": "brief description", "priority": 80}}
]\"\"\"

        response_text = self.openrouter.simple_query(prompt, model="meta-llama/llama-3.2-3b-instruct:free")
        
        # Parse JSON
        response_text = response_text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        suggestions_data = json.loads(response_text.strip())
        
        # Format suggestions
        suggestions = []
        for item in suggestions_data[:max_suggestions]:
            suggestions.append({
                'text': item.get('completion', ''),
                'type': 'ai_suggestion',
                'description': f"🤖 {item.get('description', 'AI suggestion')}",
                'priority': item.get('priority', 50),
                'provider': 'openrouter'
            })
        
        return suggestions
    except Exception as e:
        logger.error(f"OpenRouter suggestions error: {e}")
        return []


# ============================================================================
# ADD THESE METHODS TO command_processor.py (CommandProcessor class)
# ============================================================================

def process_with_multi_model(self, command: str) -> dict:
    """Process command with both Gemini and OpenRouter for comparison"""
    if not self.openrouter or not self.gemini:
        return self.process_command(command)
    
    try:
        # Get Gemini analysis
        gemini_result = self.gemini.analyze_command(command)
        
        # Get OpenRouter analysis
        openrouter_prompt = f\"\"\"Analyze this voice command and respond with JSON:
Command: "{command}"

Provide:
- intent: (launch_app, close_app, list_apps, greeting, status, help, unknown)
- app_name: application name or null
- response: brief friendly response

JSON only, no extra text.\"\"\"
        
        openrouter_text = self.openrouter.simple_query(openrouter_prompt)
        openrouter_result = json.loads(openrouter_text.strip().replace('```json', '').replace('```', ''))
        
        # Compare results
        return {
            'success': True,
            'gemini': gemini_result,
            'openrouter': openrouter_result,
            'consensus': {
                'intent': gemini_result.get('intent') if gemini_result.get('intent') == openrouter_result.get('intent') else 'uncertain',
                'match': gemini_result.get('intent') == openrouter_result.get('intent')
            }
        }
    except Exception as e:
        logger.error(f"Multi-model processing error: {e}")
        return self.process_command(command)


def _process_with_openrouter_fallback(self, command: str) -> dict:
    """Process command using OpenRouter when Gemini fails"""
    if not self.openrouter:
        return {'success': False, 'response': 'No AI provider available'}
    
    try:
        prompt = f\"\"\"You are F.R.I.D.A.Y., an AI assistant. Analyze this command:
"{command}"

Determine what action to take and respond naturally.
For app commands, include the app name.
Keep response brief and friendly.\"\"\"
        
        response = self.openrouter.simple_query(prompt)
        
        return {
            'success': True,
            'response': response,
            'provider': 'openrouter',
            'fallback': True
        }
    except Exception as e:
        logger.error(f"OpenRouter fallback error: {e}")
        return {'success': False, 'response': f"Error: {e}"}
