#!/usr/bin/env python3
"""
F.R.I.D.A.Y. Agent - Test All Local Models
Tests each installed Ollama model with sample prompts
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.local_llm import LocalLLM

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_info(text):
    print(f"{CYAN}ℹ{RESET} {text}")

async def test_model(llm: LocalLLM, model_name: str, test_prompt: str, system_prompt: str = None):
    """Test a specific model with a prompt"""
    print(f"\n{BOLD}Testing: {model_name}{RESET}")
    print(f"Prompt: {test_prompt}")

    # Set the model
    llm.set_model(model_name)

    try:
        start_time = datetime.now()
        response = await llm.generate(test_prompt, system=system_prompt)
        end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()

        if response:
            print_success(f"Response received in {duration:.2f}s")
            print(f"\n{YELLOW}Response:{RESET}")
            print(f"{response[:500]}{'...' if len(response) > 500 else ''}")
            return True, duration, len(response)
        else:
            print_error("No response received")
            return False, 0, 0

    except Exception as e:
        print_error(f"Error: {e}")
        return False, 0, 0

async def main():
    """Main test routine"""
    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║     F.R.I.D.A.Y. Agent - Test All Local Models               ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")

    # Initialize LocalLLM
    llm = LocalLLM()

    # Check availability
    print_header("1. Checking Ollama Availability")
    available = await llm.check_availability()

    if not available:
        print_error("Ollama is not running!")
        print_info("Start Ollama with: ollama serve")
        return False

    print_success("Ollama is running")
    print_info(f"Base URL: {llm.base_url}")

    # List installed models
    print_header("2. Installed Models")
    installed = await llm.list_models()

    if not installed:
        print_error("No models installed!")
        print_info("Install models with: ollama pull <model-name>")
        return False

    print_success(f"Found {len(installed)} installed models:")
    for model in installed:
        print(f"  • {model}")

    # Check predefined models
    print_header("3. Checking Predefined Models")
    available_models = llm.get_available_models()

    models_to_install = []
    models_to_test = []

    for model in available_models:
        if model['installed']:
            print_success(f"{model['icon']} {model['name']} - Installed")
            models_to_test.append(model)
        else:
            print_info(f"{model['icon']} {model['name']} - Not installed ({model['size']})")
            models_to_install.append(model)

    if models_to_install:
        print(f"\n{YELLOW}Missing models:{RESET}")
        for model in models_to_install:
            print(f"  To install: ollama pull {model['id']}")

    # Test prompts for different model types
    test_cases = {
        'coding': {
            'prompt': 'Write a Python function to calculate fibonacci numbers',
            'system': 'You are a coding assistant. Provide concise, working code.'
        },
        'general': {
            'prompt': 'Explain what artificial intelligence is in one sentence',
            'system': 'You are a helpful AI assistant. Be concise and clear.'
        }
    }

    # Test each installed model
    print_header("4. Testing Models")

    results = {}

    for model in models_to_test:
        model_id = model['id']
        model_type = model['type']

        # Select appropriate test case
        test_case = test_cases.get(model_type, test_cases['general'])

        print(f"\n{BOLD}{BLUE}{'─'*70}{RESET}")
        print(f"{BOLD}{model['icon']} {model['name']}{RESET}")
        print(f"Type: {model_type} | ID: {model_id}")
        print(f"{BOLD}{BLUE}{'─'*70}{RESET}")

        success, duration, response_len = await test_model(
            llm,
            model_id,
            test_case['prompt'],
            test_case['system']
        )

        results[model_id] = {
            'name': model['name'],
            'success': success,
            'duration': duration,
            'response_length': response_len
        }

        # Small delay between tests
        await asyncio.sleep(1)

    # Summary
    print_header("5. Test Summary")

    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)

    print(f"\n{BOLD}Results:{RESET}")
    for model_id, result in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if result['success'] else f"{RED}✗ FAIL{RESET}"
        if result['success']:
            print(f"  {status} - {result['name']}")
            print(f"         Duration: {result['duration']:.2f}s | Response: {result['response_length']} chars")
        else:
            print(f"  {status} - {result['name']}")

    print(f"\n{BOLD}Overall:{RESET}")
    percentage = (successful / total * 100) if total > 0 else 0

    if percentage == 100:
        print_success(f"All models working! ({successful}/{total} passed)")
    elif percentage >= 50:
        print(f"{YELLOW}⚠{RESET} Some models failed ({successful}/{total} passed)")
    else:
        print_error(f"Most models failed ({successful}/{total} passed)")

    # Recommendations
    if models_to_install:
        print(f"\n{BOLD}Recommendations:{RESET}")
        print_info(f"Install {len(models_to_install)} missing models for full functionality:")
        for model in models_to_install:
            print(f"  ollama pull {model['id']}")

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}\n")

    return successful == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
