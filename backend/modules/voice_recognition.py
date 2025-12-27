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
        """Main listening loop"""
        with self.microphone as source:
            while self.listening:
                try:
                    logger.info("Listening for commands...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    try:
                        # Use Google Speech Recognition
                        text = self.recognizer.recognize_google(audio)
                        logger.info(f"Recognized: {text}")
                        
                        if self.callback:
                            self.callback(text)
                        
                        self.command_queue.put(text)
                        
                    except sr.UnknownValueError:
                        logger.warning("Could not understand audio")
                    except sr.RequestError as e:
                        logger.error(f"Could not request results; {e}")
                        
                except sr.WaitTimeoutError:
                    # Timeout is normal, just continue
                    continue
                except Exception as e:
                    logger.error(f"Error in listen loop: {e}")
    
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
