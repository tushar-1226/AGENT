"""
OpenRouter API Integration
Provides access to multiple AI models through OpenRouter
"""

import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class OpenRouterAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-90b-vision-instruct:free")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter
        
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
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("FRONTEND_URL", "http://localhost:3000"),
            "X-Title": "FRIDAY Agent"
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
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "success": False
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            return []
    
    def get_free_models(self) -> List[Dict[str, Any]]:
        """Get list of free models"""
        all_models = self.get_available_models()
        # Filter for free models
        free_models = [
            model for model in all_models 
            if "free" in model.get("id", "").lower() or 
               model.get("pricing", {}).get("prompt", "0") == "0"
        ]
        return free_models
    
    def simple_query(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Simple text query - just send a prompt and get a response
        
        Args:
            prompt: The question/prompt to send
            model: Optional model override
            
        Returns:
            The AI's response text
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, model=model)
        
        if response.get("error"):
            return f"Error: {response['error']}"
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "Error: Unexpected response format"


# Convenience functions
def query_openrouter(prompt: str, model: Optional[str] = None) -> str:
    """Quick function to query OpenRouter"""
    try:
        api = OpenRouterAPI()
        return api.simple_query(prompt, model)
    except Exception as e:
        return f"Error: {str(e)}"


def get_openrouter_models() -> List[str]:
    """Get list of available OpenRouter model names"""
    try:
        api = OpenRouterAPI()
        models = api.get_available_models()
        return [model.get("id", "") for model in models]
    except Exception as e:
        print(f"Error getting models: {e}")
        return []


# Recommended free models
FREE_MODELS = {
    "fast": "meta-llama/llama-3.2-3b-instruct:free",
    "powerful": "meta-llama/llama-3.2-90b-vision-instruct:free",
    "vision": "meta-llama/llama-3.2-90b-vision-instruct:free",
    "gemma": "google/gemma-2-9b-it:free",
    "phi": "microsoft/phi-3-mini-128k-instruct:free",
    "qwen": "qwen/qwen-2-7b-instruct:free"
}
