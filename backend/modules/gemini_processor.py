"""
Gemini AI Processor Module for Friday Agent
Handles natural language understanding using Google's Gemini AI
"""
import google.generativeai as genai
import logging
import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter fallback
try:
    from modules.openrouter_integration import OpenRouterAPI
    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiProcessor:
    def __init__(self, use_openrouter_fallback=True):
        """Initialize Gemini AI processor with OpenRouter fallback"""
        api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.openrouter = None
        self.active_provider = None
        
        # Try Gemini first
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.active_provider = 'gemini'
                logger.info("✅ Gemini processor initialized")
            except Exception as e:
                logger.error(f"Gemini initialization failed: {e}")
        
        # Fallback to OpenRouter
        if not self.model and use_openrouter_fallback and OPENROUTER_AVAILABLE:
            try:
                self.openrouter = OpenRouterAPI()
                self.active_provider = 'openrouter'
                logger.info("✅ Using OpenRouter as fallback for Gemini")
            except Exception as e:
                logger.error(f"OpenRouter fallback failed: {e}")
        
        if not self.active_provider:
            logger.error("No AI provider available (neither Gemini nor OpenRouter)")
            raise ValueError("At least one AI provider (Gemini or OpenRouter) is required")
        
        # System prompt for Friday assistant
        self.system_context = """You are F.R.I.D.A.Y., a voice assistant inspired by Tony Stark's AI.
You help users control their computer through voice commands. Your capabilities include:
- Opening and closing applications
- Listing running and available applications
- Responding to greetings and queries
- Providing system status

When analyzing user commands, identify the intent and extract relevant information.
Respond in a helpful, concise, and friendly manner befitting an advanced AI assistant.
Keep responses brief and natural for text-to-speech output.

For app control commands, identify:
- Action: open/launch/start OR close/quit/exit
- App name: the specific application mentioned

Always respond professionally yet warmly, like F.R.I.D.A.Y. would."""
        
        logger.info("Gemini processor initialized successfully")
    
    def analyze_command(self, user_input: str) -> Dict[str, any]:
        """
        Analyze user command and extract intent with OpenRouter fallback
        
        Args:
            user_input: The user's natural language command
            
        Returns:
            Dict containing intent, entities, and suggested response
        """
        try:
            # Create prompt for intent analysis
            prompt = f"""{self.system_context}

User command: "{user_input}"

Analyze this command and provide a JSON response with:
1. intent: The primary action (greeting, launch_app, close_app, list_apps, status, help, unknown)
2. app_name: The application name if mentioned (or null)
3. response: A brief, natural response F.R.I.D.A.Y. would give

Respond ONLY with valid JSON, no additional text."""

            # Use active provider or fallback
            if self.active_provider == 'gemini' and self.model:
                result = self._analyze_with_gemini(prompt)
            elif self.active_provider == 'openrouter' and self.openrouter:
                result = self._analyze_with_openrouter(prompt)
            else:
                return {'success': False, 'intent': 'unknown', 'error': 'No provider available'}
            
            logger.info(f"Analysis ({result.get('provider')}): {result.get('intent')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            return {
                'success': False,
                'intent': 'unknown',
                'error': 'Failed to parse AI response'
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                'success': False,
                'intent': 'unknown',
                'error': str(e)
            }
    
    def generate_response(self, context: str, user_input: str) -> str:
        """
        Generate a natural language response
        
        Args:
            context: Context about what action was taken
            user_input: The original user command
            
        Returns:
            Natural language response
        """
        try:
            prompt = f"""{self.system_context}

User said: "{user_input}"
Action taken: {context}

Generate a brief, natural response (1-2 sentences) that F.R.I.D.A.Y. would say.
Keep it conversational and suitable for text-to-speech."""

            if self.active_provider == 'gemini' and self.model:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            elif self.active_provider == 'openrouter' and self.openrouter:
                response = self.openrouter.simple_query(prompt)
                return response.strip()
            else:
                return "Command processed."
            
        except Exception as e:
            logger.error(f"Error generating response ({self.active_provider}): {e}")
            # Try fallback
            if self.active_provider == 'gemini' and self.openrouter:
                try:
                    response = self.openrouter.simple_query(prompt)
                    return response.strip()
                except:
                    pass
            return "Command processed."
    
    def is_available(self) -> bool:
        """Check if AI provider is available"""
        return self.active_provider is not None
    
    def _analyze_with_gemini(self, prompt: str) -> dict:
        """Analyze command using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
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
            if self.openrouter:
                return self._analyze_with_openrouter(prompt)
            return {'success': False, 'intent': 'unknown', 'error': str(e)}
    
    def _analyze_with_openrouter(self, prompt: str) -> dict:
        """Analyze command using OpenRouter"""
        try:
            response = self.openrouter.simple_query(prompt)
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
