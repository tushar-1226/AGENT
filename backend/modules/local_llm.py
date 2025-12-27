"""
Local-only LLM mode using Ollama
Provides privacy-focused AI without sending data to cloud
"""
import os
import aiohttp
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LocalLLM:
    # Predefined models available in F.R.I.D.A.Y.
    AVAILABLE_MODELS = {
        "qwen2.5-coder:7b": {
            "name": "Qwen 2.5 Coder 7B",
            "description": "Best for coding tasks - code generation, debugging, review",
            "size": "4.7GB",
            "type": "coding",
            "icon": "🚀"
        },
        "llama3.2:3b": {
            "name": "Llama 3.2 3B",
            "description": "Fast general-purpose model for quick responses",
            "size": "2.0GB",
            "type": "general",
            "icon": "⚡"
        },
        "gemma2:9b": {
            "name": "Gemma 2 9B",
            "description": "Balanced performance for general tasks",
            "size": "5.4GB",
            "type": "general",
            "icon": "💎"
        },
        "codellama:7b": {
            "name": "CodeLlama 7B",
            "description": "Specialized for code completion and explanation",
            "size": "3.8GB",
            "type": "coding",
            "icon": "💻"
        },
        "phi3:mini": {
            "name": "Phi-3 Mini",
            "description": "Efficient reasoning with low resource usage",
            "size": "2.3GB",
            "type": "general",
            "icon": "🧠"
        }
    }

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = os.getenv('LOCAL_MODEL', 'qwen2.5-coder:7b')
        self.available = False
        self.installed_models = []

    async def check_availability(self) -> bool:
        """Check if Ollama is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.installed_models = [m['name'] for m in data.get('models', [])]
                        self.available = len(self.installed_models) > 0
                        return self.available
        except Exception as e:
            print(f"Ollama not available: {e}")
            self.available = False
            return False

    async def list_models(self) -> List[str]:
        """List available local models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of predefined models with their info"""
        models = []
        for model_id, info in self.AVAILABLE_MODELS.items():
            models.append({
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "size": info["size"],
                "type": info["type"],
                "icon": info["icon"],
                "installed": model_id in self.installed_models,
                "active": model_id == self.model
            })
        return models

    def set_model(self, model_name: str) -> bool:
        """Set the active model"""
        if model_name in self.AVAILABLE_MODELS:
            self.model = model_name
            return True
        return False

    def get_current_model(self) -> Dict[str, Any]:
        """Get current active model info"""
        if self.model in self.AVAILABLE_MODELS:
            info = self.AVAILABLE_MODELS[self.model]
            return {
                "id": self.model,
                "name": info["name"],
                "description": info["description"],
                "icon": info["icon"],
                "type": info["type"]
            }
        return None

    async def generate(self, prompt: str, system: str = None, stream: bool = False) -> Optional[str]:
        """Generate response using local model"""
        try:
            import json
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False  # Always disable streaming for simpler handling
            }

            if system:
                payload["system"] = system

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)  # Increased timeout
                ) as response:
                    if response.status == 200:
                        # Ollama always returns NDJSON (newline delimited JSON)
                        full_response = ""
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode('utf-8'))
                                    if 'response' in chunk:
                                        full_response += chunk['response']
                                    # Check if generation is done
                                    if chunk.get('done', False):
                                        break
                                except json.JSONDecodeError:
                                    continue
                        return full_response if full_response else None
                    else:
                        error_text = await response.text()
                        print(f"Ollama API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"Error generating with local model: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Chat with local model using conversation history"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('message', {}).get('content', '')
        except Exception as e:
            print(f"Error in chat: {e}")
            return None

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for download
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False

    def get_setup_instructions(self) -> Dict[str, Any]:
        """Get setup instructions for Ollama"""
        return {
            "status": "not_installed" if not self.available else "ready",
            "instructions": {
                "linux": "curl -fsSL https://ollama.ai/install.sh | sh",
                "mac": "brew install ollama",
                "windows": "Download from https://ollama.ai/download"
            },
            "after_install": [
                "Start Ollama: ollama serve",
                "Models will be auto-downloaded when selected"
            ],
            "recommended_models": list(self.AVAILABLE_MODELS.keys())
        }


class HybridLLM:
    """
    Hybrid LLM manager that can switch between cloud (Gemini) and local (Ollama)
    """
    def __init__(self, gemini_processor, local_llm: LocalLLM):
        self.gemini = gemini_processor
        self.local = local_llm
        self.mode = 'cloud'  # 'cloud' or 'local'

    async def set_mode(self, mode: str) -> bool:
        """Switch between cloud and local mode"""
        if mode == 'local':
            available = await self.local.check_availability()
            if not available:
                return False

        self.mode = mode
        return True

    async def process_command(self, command: str, context: str = None) -> str:
        """Process command using current mode"""
        if self.mode == 'local':
            system = context or "You are F.R.I.D.A.Y., a helpful AI assistant."
            response = await self.local.generate(command, system=system)
            return response or "Local model not available"
        else:
            # Use Gemini (cloud)
            return await self.gemini.process_command(command)

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "mode": self.mode,
            "local_available": self.local.available,
            "local_model": self.local.model if self.local.available else None
        }
