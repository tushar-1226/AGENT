"""
Command Processor Module for Friday Agent
Processes natural language commands and executes appropriate actions
Enhanced with Gemini AI for intelligent command understanding
"""
import os
import re
import logging
from typing import Dict, Optional, Callable
from dotenv import load_dotenv
from modules.app_launcher import AppLauncher
from modules.text_to_speech import TextToSpeech
from modules.gemini_processor import GeminiProcessor
from modules.query_analyzer import QueryAnalyzer

# OpenRouter integration
try:
    from modules.openrouter_integration import OpenRouterAPI
    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False
    logger.warning("OpenRouter not available")

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandProcessor:
    def __init__(self, app_launcher: AppLauncher, tts: TextToSpeech, gemini=None, browser_automation=None):
        self.app_launcher = app_launcher
        self.tts = tts
        self.browser_automation = browser_automation

        # Initialize Gemini for AI processing
        try:
            # Use provided instance or create new one
            if gemini is None:
                self.gemini = GeminiProcessor()
            else:
                self.gemini = gemini

            self.query_analyzer = QueryAnalyzer()
            
            # Initialize OpenRouter for fallback and multi-model responses
            self.openrouter = None
            if OPENROUTER_AVAILABLE:
                try:
                    self.openrouter = OpenRouterAPI()
                    logger.info("✅ OpenRouter available for fallback and multi-model responses")
                except Exception as e:
                    logger.warning(f"OpenRouter initialization failed: {e}")

            self.use_ai = True
            self.enable_multi_model = os.getenv('ENABLE_MULTI_MODEL', 'false').lower() == 'true'

            # Usage tracking
            self.usage_stats = {
                'cloud_queries': 0,
                'fallback_count': 0
            }

            logger.info("Gemini AI system initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}. Falling back to regex patterns.")
            self.gemini = None
            self.query_analyzer = None
            self.use_ai = False

        # Command patterns and their handlers (fallback)
        self.command_patterns = [
            # Chained commands (Open X and Search Y)
            (r'(?:open|launch|start)\s+(.+?)\s+and\s+(?:search|find|lookup)\s+(?:for\s+)?(.+)', self._handle_launch_and_search),

            # App launching
            (r'(?:open|launch|start|run)\s+(.+)', self._handle_launch_app),
            (r'(?:close|quit|exit|stop)\s+(.+)', self._handle_close_app),

            # Queries
            (r'(?:what|which)\s+apps?\s+(?:are\s+)?(?:running|open)', self._handle_list_apps),
            (r'(?:what|which)\s+apps?\s+(?:can\s+you|do\s+you)\s+(?:open|launch)', self._handle_available_apps),

            # Greetings
            (r'(?:hello|hi|hey)\s*(?:friday)?', self._handle_greeting),
            (r'how\s+are\s+you', self._handle_how_are_you),

            # Help
            (r'(?:help|what\s+can\s+you\s+do)', self._handle_help),

            # Status
            (r'(?:status|are\s+you\s+(?:there|online|active))', self._handle_status),
        ]

    def get_usage_stats(self) -> dict:
        """Get usage statistics"""
        stats = self.usage_stats.copy()
        if self.query_analyzer:
            stats['query_complexity'] = self.query_analyzer.get_stats()
        return stats

    async def process_command(self, command: str) -> Dict[str, any]:
        """Process a natural language command using Gemini AI"""
        original_command = command
        command_lower = command.lower().strip()
        logger.info(f"Processing command: {command}")

        # Try AI-powered processing first
        if self.use_ai and self.gemini:
            try:
                # Process with cloud (Gemini)
                ai_result = await self._process_with_cloud(original_command)

                if ai_result and ai_result.get('success'):
                    intent = ai_result.get('intent', 'unknown')
                    app_name = ai_result.get('app_name')
                    ai_response = ai_result.get('ai_response', '')

                    logger.info(f"AI detected intent: {intent}, app: {app_name}")

                    # Route to appropriate handler based on AI intent
                    if intent == 'launch_app' and app_name:
                        return self._handle_launch_app_by_name(app_name, ai_response)
                    elif intent == 'close_app' and app_name:
                        return self._handle_close_app_by_name(app_name, ai_response)
                    elif intent == 'list_apps':
                        return self._handle_list_apps_ai(ai_response)
                    elif intent == 'greeting':
                        return self._handle_greeting_ai(ai_response)
                    elif intent == 'status':
                        return self._handle_status_ai(ai_response)
                    elif intent == 'help':
                        return self._handle_help_ai(ai_response)
                    elif intent == 'general_query':
                        # Direct knowledge query - return AI response
                        self.tts.speak(ai_response)
                        return {
                            'success': True,
                            'message': 'General query answered',
                            'response': ai_response
                        }

                    # General query - return AI response
                    return {
                        'success': True,
                        'message': 'AI response',
                        'response': ai_response
                    }

            except Exception as e:
                logger.error(f"AI processing error: {e}. Falling back to regex.")

        # Fallback to regex pattern matching
        for pattern, handler in self.command_patterns:
            match = re.search(pattern, command_lower)
            if match:
                return handler(match)

        # No pattern matched
        return {
            'success': False,
            'message': "I didn't understand that command",
            'response': "I'm sorry, I didn't understand that. Try saying 'help' for a list of commands."
        }

    async def _process_with_cloud(self, command: str) -> Optional[Dict]:
        """Process command with cloud model (Gemini)"""
        try:
            import asyncio
            # Run blocking Gemini call in threadpool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.gemini.analyze_command, command)

            if result.get('success'):
                self.usage_stats['cloud_queries'] += 1
            return result
        except Exception as e:
            logger.error(f"Cloud model error: {e}")
            return None


    def _handle_launch_app_by_name(self, app_name: str, ai_response: str = None) -> Dict[str, any]:
        """Handle app launching with AI-detected app name"""
        result = self.app_launcher.launch_app(app_name)

        if result['success']:
            response = ai_response or f"Opening {app_name} now"
        else:
            response = f"I couldn't open {app_name}. {result['message']}"

        self.tts.speak(response)
        result['response'] = response
        return result

    def _handle_close_app_by_name(self, app_name: str, ai_response: str = None) -> Dict[str, any]:
        """Handle app closing with AI-detected app name"""
        result = self.app_launcher.close_app(app_name)

        response = ai_response or result['message']
        self.tts.speak(response)
        result['response'] = response
        return result

    def _handle_list_apps_ai(self, ai_response: str = None) -> Dict[str, any]:
        """Handle listing running apps with AI response"""
        running = self.app_launcher.list_running_apps()

        if ai_response:
            response = ai_response
        elif running:
            apps_list = ", ".join(running)
            response = f"Currently running: {apps_list}"
        else:
            response = "No apps are currently running that I launched"

        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Listed running apps',
            'response': response,
            'apps': running
        }

    def _handle_greeting_ai(self, ai_response: str = None) -> Dict[str, any]:
        """Handle greetings with AI response"""
        response = ai_response or "Hello! I'm Friday. How can I assist you today?"
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Greeting',
            'response': response
        }

    def _handle_status_ai(self, ai_response: str = None) -> Dict[str, any]:
        """Handle status checks with AI response"""
        response = ai_response or "Friday is online and ready"
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Status check',
            'response': response
        }

    def _handle_help_ai(self, ai_response: str = None) -> Dict[str, any]:
        """Handle help requests with AI response"""
        response = ai_response or ("I can help you open and close applications, check system status, "
                   "and respond to various commands. Try saying 'open chrome' or "
                   "'what apps are running'")
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Help',
            'response': response
        }


    def _handle_launch_app(self, match) -> Dict[str, any]:
        """Handle app launching commands"""
        app_name = match.group(1).strip()
        result = self.app_launcher.launch_app(app_name)

        if result['success']:
            response = f"Opening {app_name} now"
        else:
            response = f"I couldn't open {app_name}. {result['message']}"

        self.tts.speak(response)
        result['response'] = response
        return result

    def _handle_close_app(self, match) -> Dict[str, any]:
        """Handle app closing commands"""
        app_name = match.group(1).strip()
        result = self.app_launcher.close_app(app_name)

        response = result['message']
        self.tts.speak(response)
        result['response'] = response
        return result

    def _handle_list_apps(self, match) -> Dict[str, any]:
        """Handle listing running apps"""
        running = self.app_launcher.list_running_apps()

        if running:
            apps_list = ", ".join(running)
            response = f"Currently running: {apps_list}"
        else:
            response = "No apps are currently running that I launched"

        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Listed running apps',
            'response': response,
            'apps': running
        }

    def _handle_available_apps(self, match) -> Dict[str, any]:
        """Handle listing available apps"""
        available = self.app_launcher.get_available_apps()

        if available:
            response = f"I can open: {', '.join(available[:5])} and more"
        else:
            response = "No preset apps available for your platform"

        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Listed available apps',
            'response': response,
            'apps': available
        }

    def _handle_greeting(self, match) -> Dict[str, any]:
        """Handle greetings"""
        response = "Hello! I'm Friday. How can I assist you today?"
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Greeting',
            'response': response
        }

    def _handle_how_are_you(self, match) -> Dict[str, any]:
        """Handle how are you"""
        response = "All systems operational. Ready to assist you."
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Status query',
            'response': response
        }

    def _handle_help(self, match) -> Dict[str, any]:
        """Handle help requests"""
        response = ("I can help you open and close applications, check system status, "
                   "and respond to various commands. Try saying 'open chrome' or "
                   "'what apps are running'")
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Help',
            'response': response
        }

    def _handle_status(self, match) -> Dict[str, any]:
        """Handle status checks"""
        response = "Friday is online and ready"
        self.tts.speak(response)
        return {
            'success': True,
            'message': 'Status check',
            'response': response
        }

    def _handle_launch_and_search(self, match) -> Dict[str, any]:
        """Handle 'open [app] and search [query]' commands"""
        app_name = match.group(1).strip().lower()
        query = match.group(2).strip()
        
        # Check if app is a browser
        browsers = ['chrome', 'google chrome', 'browser', 'firefox', 'internet', 'edge', 'safari']
        
        if any(b in app_name for b in browsers):
            if self.browser_automation:
                response = f"Opening {app_name} and searching for {query}"
                self.tts.speak(response)
                
                # Use browser automation to launch and search
                import asyncio
                
                # We need to run this async, but we are in a sync method called by regex
                # This is a bit tricky. For now, we'll try to schedule it or run it
                # Best approach for this prototype: Use AppLauncher for the app (visual) 
                # and append the search URL if possible?
                # Actually, simple `google-chrome <url>` is best for "Opening Chrome" visible to user.
                # Playwright is great for headless/automation, but might be overkill just to open a tab.
                # Let's try AppLauncher with URL argument first if possible.
                
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                
                # Try to launch via command line with URL
                # We can construct a "command" that includes the URL
                # Update AppLauncher? Or just hack it here?
                # Let's try to use system command via AppLauncher hack or just subprocess here?
                # Better: Use BrowserAutomation if we want "Agentic" control (reading results later).
                # But user just said "open and search".
                # Let's use BrowserAutomation with headless=False to show the user.
                
                async def run_search():
                    await self.browser_automation.start_browser(headless=False)
                    await self.browser_automation.navigate(search_url)
                
                # Fire and forget / run in background?
                # Since CommandProcessor is often called from async context (WebSocket), 
                # but these regex handlers are sync functions...
                # Actually process_command is async!
                # But the regex handlers are called directly?
                # process_command calls regex handlers synchronously: `return handler(match)`
                # We should probably make regex handlers async? 
                # Refactoring all regex handlers to async would be big.
                # Alternative: Run in background thread/loop.
                
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(run_search())
                except RuntimeError:
                    # New loop if none exists
                    asyncio.run(run_search())
                    
                return {
                    'success': True,
                    'message': f"Launched {app_name} and searched for {query}",
                    'response': response
                }
            else:
                return {
                    'success': False,
                    'message': "Browser automation module not available",
                    'response': "I cannot control the browser right now."
                }
        else:
            # Not a browser - just launch the app and apologize about search
            self.app_launcher.launch_app(app_name)
            response = f"Opening {app_name}. I can only search within web browsers currently."
            self.tts.speak(response)
            return {
                'success': True,  # Partial success
                'message': f"Launched {app_name}, but skipped search",
                'response': response
            }
