#!/usr/bin/env python3
"""
F.R.I.D.A.Y. Agent - Model Health Check Script
Checks all AI models and their availability
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    print(f"{CYAN}ℹ{RESET} {text}")

async def check_gemini():
    """Check Gemini AI model availability"""
    print_header("1. Checking Gemini AI (Cloud Model)")
    
    try:
        from modules.gemini_processor import GeminiProcessor
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print_error("GEMINI_API_KEY not found in environment variables")
            print_info("Please set GEMINI_API_KEY in backend/.env")
            return False
        
        print_info(f"API Key found: {api_key[:10]}...{api_key[-4:]}")
        
        # Initialize processor
        processor = GeminiProcessor()
        print_success("GeminiProcessor initialized successfully")
        
        # Test API availability
        print_info("Testing API connection...")
        is_available = processor.is_available()
        
        if is_available:
            print_success("Gemini API is available and responding")
            print_info("Model: gemini-2.5-flash")
            
            # Test a simple command
            print_info("Testing command analysis...")
            result = processor.analyze_command("Hello Friday")
            if result.get('success'):
                print_success(f"Command analysis working - Intent: {result.get('intent')}")
                print_info(f"AI Response: {result.get('ai_response')}")
            else:
                print_warning("Command analysis returned error")
            
            return True
        else:
            print_error("Gemini API is not responding")
            return False
            
    except Exception as e:
        print_error(f"Gemini check failed: {e}")
        return False

async def check_local_llm():
    """Check Local LLM (Ollama) availability"""
    print_header("2. Checking Local LLM (Ollama)")
    
    try:
        from modules.local_llm import LocalLLM
        
        llm = LocalLLM()
        print_info("LocalLLM instance created")
        
        # Check if Ollama is running
        print_info("Checking Ollama service...")
        is_available = await llm.check_availability()
        
        if is_available:
            print_success("Ollama is running and available")
            print_info(f"Base URL: {llm.base_url}")
            
            # List installed models
            installed = await llm.list_models()
            print_success(f"Found {len(installed)} installed models:")
            for model in installed:
                print(f"  • {model}")
            
            # Show available models
            print_info("\nAvailable models for installation:")
            available_models = llm.get_available_models()
            for model in available_models:
                status = "✓ Installed" if model['installed'] else "○ Not installed"
                active = " [ACTIVE]" if model['active'] else ""
                print(f"  {model['icon']} {model['name']} - {status}{active}")
                print(f"     {model['description']} ({model['size']})")
            
            # Get current model
            current = llm.get_current_model()
            if current:
                print_success(f"\nCurrent active model: {current['name']}")
            
            return True
        else:
            print_error("Ollama is not running")
            print_info("\nTo install and run Ollama:")
            setup = llm.get_setup_instructions()
            print(f"  Linux:   {setup['instructions']['linux']}")
            print(f"  Mac:     {setup['instructions']['mac']}")
            print(f"  Windows: {setup['instructions']['windows']}")
            print_info("\nAfter installation:")
            for step in setup['after_install']:
                print(f"  • {step}")
            
            return False
            
    except Exception as e:
        print_error(f"Local LLM check failed: {e}")
        return False

def check_voice_recognition():
    """Check Voice Recognition availability"""
    print_header("3. Checking Voice Recognition")
    
    try:
        import speech_recognition as sr
        print_success("SpeechRecognition library installed")
        
        # Check microphone
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            print_success("Microphone detected")
            
            # List available microphones
            mic_list = sr.Microphone.list_microphone_names()
            print_info(f"Found {len(mic_list)} audio input devices:")
            for i, name in enumerate(mic_list[:5]):  # Show first 5
                print(f"  {i}: {name}")
            
            print_info("Using Google Speech Recognition API")
            print_warning("Note: Requires internet connection for recognition")
            
            return True
            
        except Exception as e:
            print_warning(f"Microphone check failed: {e}")
            print_info("Voice recognition may not work without a microphone")
            return False
            
    except ImportError:
        print_error("SpeechRecognition library not installed")
        print_info("Install with: pip install SpeechRecognition")
        return False

def check_text_to_speech():
    """Check Text-to-Speech availability"""
    print_header("4. Checking Text-to-Speech")
    
    try:
        import pyttsx3
        print_success("pyttsx3 library installed")
        
        try:
            engine = pyttsx3.init()
            print_success("TTS engine initialized successfully")
            
            # Get voices
            voices = engine.getProperty('voices')
            print_info(f"Found {len(voices)} voices:")
            for i, voice in enumerate(voices[:3]):  # Show first 3
                print(f"  {i}: {voice.name}")
            
            # Get properties
            rate = engine.getProperty('rate')
            volume = engine.getProperty('volume')
            print_info(f"Speech rate: {rate} WPM")
            print_info(f"Volume: {volume}")
            
            return True
            
        except Exception as e:
            print_error(f"TTS engine initialization failed: {e}")
            print_info("On Linux, install espeak:")
            print_info("  sudo apt-get install espeak espeak-ng")
            return False
            
    except ImportError:
        print_error("pyttsx3 library not installed")
        print_info("Install with: pip install pyttsx3")
        return False

def check_dependencies():
    """Check critical dependencies"""
    print_header("5. Checking Critical Dependencies")
    
    dependencies = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'google.generativeai': 'Google Gemini AI',
        'aiohttp': 'Async HTTP client',
        'PIL': 'Image processing (Pillow)',
        'pypdf': 'PDF processing',
        'psutil': 'System monitoring',
        'cryptography': 'Encryption',
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print_success(f"{module:25s} - {description}")
        except ImportError:
            print_error(f"{module:25s} - {description} [MISSING]")
            all_ok = False
    
    return all_ok

def check_optional_dependencies():
    """Check optional dependencies"""
    print_header("6. Checking Optional Dependencies")
    
    optional = {
        'chromadb': 'RAG Document Intelligence',
        'sentence_transformers': 'Semantic embeddings',
        'git': 'Git integration (GitPython)',
        'sqlalchemy': 'Database ORM',
        'playwright': 'Browser automation',
    }
    
    installed = []
    missing = []
    
    for module, description in optional.items():
        try:
            __import__(module)
            print_success(f"{module:25s} - {description}")
            installed.append(module)
        except ImportError:
            print_warning(f"{module:25s} - {description} [NOT INSTALLED]")
            missing.append(module)
    
    if missing:
        print_info("\nTo install optional features:")
        print_info("  pip install chromadb sentence-transformers gitpython sqlalchemy playwright")
    
    return len(installed), len(missing)

async def main():
    """Main check routine"""
    print(f"\n{BOLD}{CYAN}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║     F.R.I.D.A.Y. Agent - Model Health Check Report        ║{RESET}")
    print(f"{BOLD}{CYAN}╚════════════════════════════════════════════════════════════╝{RESET}")
    
    results = {}
    
    # Run all checks
    results['gemini'] = await check_gemini()
    results['local_llm'] = await check_local_llm()
    results['voice_recognition'] = check_voice_recognition()
    results['text_to_speech'] = check_text_to_speech()
    results['dependencies'] = check_dependencies()
    installed, missing = check_optional_dependencies()
    
    # Summary
    print_header("Summary Report")
    
    total_checks = 5
    passed = sum([
        results['gemini'],
        results['local_llm'],
        results['voice_recognition'],
        results['text_to_speech'],
        results['dependencies']
    ])
    
    print(f"\n{BOLD}Core Features:{RESET}")
    print(f"  Gemini AI (Cloud):     {'✓ Working' if results['gemini'] else '✗ Not Available'}")
    print(f"  Local LLM (Ollama):    {'✓ Working' if results['local_llm'] else '✗ Not Available'}")
    print(f"  Voice Recognition:     {'✓ Working' if results['voice_recognition'] else '✗ Not Available'}")
    print(f"  Text-to-Speech:        {'✓ Working' if results['text_to_speech'] else '✗ Not Available'}")
    print(f"  Core Dependencies:     {'✓ All Installed' if results['dependencies'] else '✗ Missing Some'}")
    
    print(f"\n{BOLD}Optional Features:{RESET}")
    print(f"  Installed: {installed}/{installed + missing}")
    
    print(f"\n{BOLD}Overall Status:{RESET}")
    percentage = (passed / total_checks) * 100
    
    if percentage == 100:
        print_success(f"All systems operational! ({passed}/{total_checks} checks passed)")
    elif percentage >= 60:
        print_warning(f"Partially operational ({passed}/{total_checks} checks passed)")
    else:
        print_error(f"Multiple issues detected ({passed}/{total_checks} checks passed)")
    
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}\n")
    
    return passed == total_checks

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Check interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        sys.exit(1)
