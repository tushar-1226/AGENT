"""
Voice Recognition Module for Friday Agent
Handles speech-to-text conversion using multiple engines
"""
import speech_recognition as sr
import threading
import queue
from typing import Callable, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceRecognizer:
    def __init__(self, callback: Optional[Callable] = None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.callback = callback
        self.command_queue = queue.Queue()
        
        # Adjust for ambient noise
        with self.microphone as source:
            logger.info("Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Calibration complete")
    
    def start_listening(self):
        """Start continuous listening in a separate thread"""
        if not self.listening:
            self.listening = True
            threading.Thread(target=self._listen_loop, daemon=True).start()
            logger.info("Voice recognition started")
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False
        logger.info("Voice recognition stopped")
    
    def _listen_loop(self):
        """Main listening loop with Wake Word detection"""
        import time
        
        self.active_mode = False
        self.last_active_time = 0
        self.active_duration = 5  # seconds
        
        with self.microphone as source:
            while self.listening:
                try:
                    # Determine current state
                    is_active = False
                    if self.active_mode:
                        if time.time() - self.last_active_time < self.active_duration:
                            is_active = True
                        else:
                            self.active_mode = False
                            logger.info("Wake word timeout: Entering passive mode")
                            if self.callback:
                                self.callback("system_notification:exiting_active_mode")

                    logger.info(f"Listening ({'ACTIVE' if is_active else 'PASSIVE'})...")
                    
                    # Adjust timeout based on mode
                    listen_timeout = 5 if is_active else 2  # Short listen for wake word checks
                    
                    try:
                        audio = self.recognizer.listen(source, timeout=listen_timeout, phrase_time_limit=10)
                    except sr.WaitTimeoutError:
                        continue

                    try:
                        # Use Google Speech Recognition
                        text = self.recognizer.recognize_google(audio).lower()
                        logger.info(f"Recognized: {text}")
                        
                        # Check for Wake Word "Friday"
                        if "friday" in text:
                            logger.info("Wake word detected!")
                            self.active_mode = True
                            self.last_active_time = time.time()
                            
                            # Remove "friday" from text to see if there's a command attached
                            command = text.replace("friday", "").strip()
                            
                            if command:
                                logger.info(f"Command with wake word: {command}")
                                if self.callback:
                                    self.callback(command)
                                self.command_queue.put(command)
                            else:
                                logger.info("Wake word only - waiting for command")
                                if self.callback:
                                    self.callback("system_notification:wake_word_detected")
                                    
                        elif self.active_mode:
                            # Already in active mode, process as command
                            logger.info(f"Active mode command: {text}")
                            # Refresh timer? Optionally yes. Let's reset it to allow conversation flow.
                            self.last_active_time = time.time() 
                            
                            if self.callback:
                                self.callback(text)
                            self.command_queue.put(text)
                        
                    except sr.UnknownValueError:
                        # Only log warning if in active mode to avoid spamming "Could not understand" in passive
                        if self.active_mode:
                            logger.warning("Could not understand audio in active mode")
                    except sr.RequestError as e:
                        logger.error(f"Could not request results; {e}")
                        
                except Exception as e:
                    logger.error(f"Error in listen loop: {e}")
                    import time
                    time.sleep(1)  # Prevent tight loop on error
    
    def get_command(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get next command from queue"""
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def recognize_once(self) -> Optional[str]:
        """Recognize a single command"""
        with self.microphone as source:
            try:
                logger.info("Listening for single command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: {text}")
                return text
            except Exception as e:
                logger.error(f"Recognition error: {e}")
                return None
