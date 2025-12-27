"""
Text-to-Speech Module for Friday Agent
Handles voice synthesis for responses (optional - gracefully degrades if dependencies missing)
"""
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import pyttsx3, but make it optional
try:
    import pyttsx3
    TTS_AVAILABLE = True
    logger.info("✅ Text-to-speech engine available")
except (ImportError, RuntimeError) as e:
    TTS_AVAILABLE = False
    logger.warning(f"⚠️  Text-to-speech not available: {e}")
    logger.info("💡 To enable TTS, install: sudo apt-get install espeak espeak-ng")


class TextToSpeech:
    def __init__(self):
        self.enabled = TTS_AVAILABLE
        self.engine = None
        self.speech_queue = queue.Queue()
        self.speaking = False

        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                # Configure voice properties
                self._configure_voice()
                # Start speech thread
                threading.Thread(target=self._speech_loop, daemon=True).start()
                logger.info("✅ Text-to-speech initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize TTS engine: {e}")
                self.enabled = False
        else:
            logger.info("ℹ️  Text-to-speech module running in silent mode")

    def _configure_voice(self):
        """Configure voice properties for a more JARVIS-like sound"""
        if not self.enabled or not self.engine:
            return

        try:
            voices = self.engine.getProperty('voices')

            # Try to select a male voice (usually index 0)
            if voices:
                self.engine.setProperty('voice', voices[0].id)

            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 175)  # Slightly faster than default

            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.9)

            logger.info("Voice configured successfully")
        except Exception as e:
            logger.warning(f"⚠️  Voice configuration failed: {e}")

    def speak(self, text: str, priority: bool = False):
        """Add text to speech queue"""
        if not self.enabled:
            logger.debug(f"📢 [Silent mode] Would speak: {text}")
            return

        if priority:
            # Insert at front of queue
            temp_queue = queue.Queue()
            temp_queue.put(text)
            while not self.speech_queue.empty():
                temp_queue.put(self.speech_queue.get())
            self.speech_queue = temp_queue
        else:
            self.speech_queue.put(text)

        logger.info(f"Queued speech: {text}")

    def speak_now(self, text: str):
        """Speak immediately (blocking)"""
        if not self.enabled or not self.engine:
            logger.debug(f"📢 [Silent mode] Would speak now: {text}")
            return

        try:
            logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.warning(f"⚠️  Speech failed: {e}")

    def _speech_loop(self):
        """Background thread for processing speech queue"""
        if not self.enabled or not self.engine:
            return

        while True:
            try:
                text = self.speech_queue.get()
                self.speaking = True
                self.speak_now(text)
                self.speaking = False
                self.speech_queue.task_done()
            except Exception as e:
                logger.error(f"Speech error: {e}")
                self.speaking = False

    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.speaking

    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        logger.info("Speech queue cleared")

    def stop(self):
        """Stop current speech"""
        if self.enabled and self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                logger.warning(f"⚠️  Failed to stop speech: {e}")
