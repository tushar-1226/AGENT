"""
Groq API Integration
Ultra-fast inference with Groq's LPU architecture
"""

import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class GroqAPI:
    """
    Groq API client for ultra-fast LLM inference
    Groq's Language Processing Units (LPUs) provide significantly faster inference than GPUs
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not found in environment variables")
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to env variable)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response dict with completion
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if stream:
            payload["stream"] = True
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Log performance metrics (Groq returns these)
            if "x-groq" in response.headers:
                logger.info(f"Groq inference time: {response.headers.get('x-groq-time', 'N/A')}")
            
            return result
        except requests.exceptions.HTTPError as e:
            logger.error(f"Groq API HTTP error: {e.response.status_code}")
            return {
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "success": False
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request error: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate text from a simple prompt
        
        Args:
            prompt: The text prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text string
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, model, temperature, max_tokens)
        
        if "error" in response:
            return f"Error: {response['error']}"
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "Error: Invalid response format"
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available Groq models
        
        Returns:
            List of model identifiers
        """
        # As of 2026, popular Groq models include:
        return [
            "llama-3.3-70b-versatile",  # Best for general tasks
            "llama-3.1-70b-versatile",  # Previous generation
            "mixtral-8x7b-32768",       # Large context window
            "gemma2-9b-it",             # Google's efficient model
            "llama3-70b-8192",          # Balanced performance
            "llama3-8b-8192",           # Fastest, good for simple tasks
        ]
    
    async def analyze_code_async(
        self,
        code: str,
        language: str = "python",
        task: str = "review"
    ) -> Dict[str, Any]:
        """
        Analyze code using Groq's ultra-fast inference
        Perfect for real-time code analysis
        
        Args:
            code: The code to analyze
            language: Programming language
            task: Analysis task (review, explain, optimize, debug)
            
        Returns:
            Analysis results
        """
        prompts = {
            "review": f"Review this {language} code for best practices, potential bugs, and improvements:\n\n{code}",
            "explain": f"Explain what this {language} code does in detail:\n\n{code}",
            "optimize": f"Suggest optimizations for this {language} code:\n\n{code}",
            "debug": f"Identify potential bugs in this {language} code:\n\n{code}"
        }
        
        prompt = prompts.get(task, prompts["review"])
        result = self.generate_text(prompt, max_tokens=2048, temperature=0.3)
        
        return {
            "success": True,
            "analysis": result,
            "task": task,
            "language": language
        }


# Singleton instance
_groq_instance = None

def get_groq_instance() -> Optional[GroqAPI]:
    """Get or create Groq API instance"""
    global _groq_instance
    if _groq_instance is None:
        try:
            _groq_instance = GroqAPI()
        except ValueError as e:
            logger.warning(f"Groq API not initialized: {e}")
            return None
    return _groq_instance
