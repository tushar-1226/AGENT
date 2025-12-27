"""
Command Processor Module for Friday Agent
Processes natural language commands and executes appropriate actions
Enhanced with Hybrid LLM (Local + Cloud) for intelligent command understanding
"""
import os
import re
import logging
from typing import Dict, Optional, Callable, Literal
from dotenv import load_dotenv
from modules.app_launcher import AppLauncher
from modules.text_to_speech import TextToSpeech
from modules.gemini_processor import GeminiProcessor
from modules.local_llm import LocalLLM, HybridLLM
from modules.query_analyzer import QueryAnalyzer

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LLMMode = Literal['local', 'cloud', 'hybrid']


class CommandProcessor:
    def __init__(self, app_launcher: AppLauncher, tts: TextToSpeech, local_llm=None, gemini=None):
        self.app_launcher = app_launcher
        self.tts = tts

        # Initialize Hybrid LLM system with provided instances or create new ones
        try:
            # Use provided instances or create new ones
            if gemini is None:
                self.gemini = GeminiProcessor()
            else:
                self.gemini = gemini

            if local_llm is None:
                self.local_llm = LocalLLM()
            else:
                self.local_llm = local_llm

            self.hybrid_llm = HybridLLM(self.gemini, self.local_llm)
            self.query_analyzer = QueryAnalyzer()

            # Read default mode from environment, fallback to hybrid
            default_mode = os.getenv('LLM_MODE', 'hybrid').lower()
            if default_mode not in ['local', 'cloud', 'hybrid']:
                logger.warning(f"Invalid LLM_MODE in .env: {default_mode}, using 'hybrid'")
                default_mode = 'hybrid'

            self.mode: LLMMode = default_mode
            self.use_ai = True

            # Usage tracking
            self.usage_stats = {
                'local_queries': 0,
                'cloud_queries': 0,
                'fallback_count': 0
            }

            logger.info(f"Hybrid LLM system initialized (Local + Cloud) - Default mode: {self.mode}")
        except Exception as e:
            logger.warning(f"Failed to initialize Hybrid LLM: {e}. Falling back to regex patterns.")
            self.hybrid_llm = None
            self.gemini = None
            self.local_llm = None
            self.query_analyzer = None
            self.use_ai = False
            self.mode = 'cloud'

        # Command patterns and their handlers (fallback)
        self.command_patterns = [
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

    def set_mode(self, mode: LLMMode) -> bool:
        """Set LLM mode (local/cloud/hybrid)"""
        if mode not in ['local', 'cloud', 'hybrid']:
            return False

        # Only check local availability if switching to local-only mode
        if mode == 'local':
            if not self.local_llm:
                logger.warning("Local LLM not initialized, cannot switch to local mode")
                return False

            import asyncio
            try:
                # Run async check in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                available = loop.run_until_complete(self.local_llm.check_availability())
                loop.close()

                if not available:
                    logger.warning("Local LLM not available (Ollama not running?), cannot switch to local mode")
                    return False
            except Exception as e:
                logger.error(f"Error checking local LLM availability: {e}")
                return False

        # Cloud and Hybrid modes can work without local LLM
        self.mode = mode
        logger.info(f"LLM mode set to: {mode}")
        return True

    def get_mode(self) -> LLMMode:
        """Get current LLM mode"""
        return self.mode

    def get_usage_stats(self) -> dict:
        """Get usage statistics"""
        stats = self.usage_stats.copy()
        if self.query_analyzer:
            stats['query_complexity'] = self.query_analyzer.get_stats()
        return stats

    async def process_command(self, command: str) -> Dict[str, any]:
        """Process a natural language command using Hybrid LLM with intelligent routing"""
        original_command = command
        command_lower = command.lower().strip()
        logger.info(f"Processing command: {command} (Mode: {self.mode})")

        # Try AI-powered processing first
        if self.use_ai and self.hybrid_llm:
            try:
                # Analyze query complexity
                complexity = self.query_analyzer.analyze_complexity(command) if self.query_analyzer else 'medium'
                is_code_related = self.query_analyzer.is_code_related(command) if self.query_analyzer else False

                # Determine which model to use based on mode and complexity
                use_local = self._should_use_local(complexity, is_code_related)

                logger.info(f"Query complexity: {complexity}, Code-related: {is_code_related}, Using: {'local' if use_local else 'cloud'}")

                # Route to appropriate model
                if use_local:
                    ai_result = await self._process_with_local(original_command)
                else:
                    ai_result = await self._process_with_cloud(original_command)

                if ai_result and ai_result.get('success'):
                    intent = ai_result.get('intent', 'unknown')
                    app_name = ai_result.get('app_name')
                    ai_response = ai_result.get('ai_response', '')

                    # Add routing metadata
                    ai_result['used_model'] = 'local' if use_local else 'cloud'
                    ai_result['complexity'] = complexity

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

                    # General query - return AI response
                    return {
                        'success': True,
                        'message': 'AI response',
                        'response': ai_response,
                        'used_model': 'local' if use_local else 'cloud',
                        'complexity': complexity
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

    def _should_use_local(self, complexity: str, is_code_related: bool) -> bool:
        """Determine if local model should be used based on mode and query characteristics"""
        if self.mode == 'cloud':
            return False
        elif self.mode == 'local':
            return True
        else:  # hybrid mode
            # Simple queries always go to local
            if complexity == 'simple':
                return True
            # Code-related medium queries go to local if we have a coding model
            if complexity == 'medium' and is_code_related:
                return True
            # Complex queries go to cloud
            return False

    async def _process_with_local(self, command: str) -> Optional[Dict]:
        """Process command with local model"""
        try:
            # Use local model directly with await
            response = await self.local_llm.generate(
                command,
                system="You are F.R.I.D.A.Y., a helpful AI assistant. Provide concise, helpful responses."
            )

            if response:
                self.usage_stats['local_queries'] += 1
                return {
                    'success': True,
                    'ai_response': response,
                    'intent': 'general_query'
                }
            else:
                # If strict local mode, do not fallback
                if self.mode == 'local':
                    logger.warning("Local model returned empty response. Strict local mode enabled - skipping fallback.")
                    return {
                        'success': False,
                        'message': 'Local model returned empty response',
                        'response': 'I am unable to generate a response with the local model right now.'
                    }

                # Fallback to cloud for hybrid mode
                logger.warning("Local model returned empty response, falling back to cloud")
                self.usage_stats['fallback_count'] += 1
                return await self._process_with_cloud(command)

        except Exception as e:
            # If strict local mode, do not fallback
            if self.mode == 'local':
                logger.error(f"Local model error in strict local mode: {e}")
                return {
                    'success': False,
                    'message': f'Local model error: {str(e)}',
                    'response': 'I encountered an error using the local model.'
                }

            logger.error(f"Local model error: {e}, falling back to cloud")
            self.usage_stats['fallback_count'] += 1
            return await self._process_with_cloud(command)

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
