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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiProcessor:
    def __init__(self):
        """Initialize Gemini AI processor"""
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash model (latest stable model)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
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
        Analyze user command and extract intent
        
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

            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            import json
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            
            logger.info(f"Gemini analysis: {result}")
            return {
                'success': True,
                'intent': result.get('intent', 'unknown'),
                'app_name': result.get('app_name'),
                'ai_response': result.get('response', ''),
                'raw_response': response.text
            }
            
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

            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Command processed."
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        try:
            # Simple test to verify API connection
            test_response = self.model.generate_content("Hello")
            return True
        except Exception as e:
            logger.error(f"Gemini API not available: {e}")
            return False
