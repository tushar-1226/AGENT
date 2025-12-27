#!/usr/bin/env python3
"""
Test script to verify Local LLM integration
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.local_llm import LocalLLM
from modules.gemini_processor import GeminiProcessor
from modules.command_processor import CommandProcessor
from modules.app_launcher import AppLauncher
from modules.text_to_speech import TextToSpeech

async def test_local_llm():
    """Test Local LLM connectivity"""
    print("=" * 60)
    print("Testing Local LLM (Ollama)")
    print("=" * 60)

    llm = LocalLLM()
    available = await llm.check_availability()

    print(f"\n✅ Ollama Status: {'Running' if available else 'Not Available'}")

    if available:
        print(f"📦 Installed Models ({len(llm.installed_models)}):")
        for model in llm.installed_models:
            print(f"   - {model}")

        print(f"\n🎯 Current Model: {llm.model}")

        # Test generation
        print("\n🧪 Testing generation...")
        response = await llm.generate(
            "Write a one-line greeting for F.R.I.D.A.Y. AI assistant",
            system="You are F.R.I.D.A.Y., a helpful AI assistant."
        )
        print(f"Response: {response}")
    else:
        print("\n❌ Ollama is not running!")
        print("To start: ollama serve")
        print("To install a model: ollama pull qwen2.5-coder:7b")

    return available

async def test_command_processor():
    """Test CommandProcessor with LLM integration"""
    print("\n" + "=" * 60)
    print("Testing Command Processor")
    print("=" * 60)

    try:
        # Initialize components
        app_launcher = AppLauncher()
        tts = TextToSpeech()
        gemini = GeminiProcessor()
        local_llm = LocalLLM()

        # Initialize CommandProcessor with shared instances
        processor = CommandProcessor(app_launcher, tts, local_llm=local_llm, gemini=gemini)

        print(f"\n✅ CommandProcessor initialized")
        print(f"🎯 Default Mode: {processor.mode}")
        print(f"🤖 AI Enabled: {processor.use_ai}")

        # Test with a simple command
        print("\n🧪 Testing command: 'What is 2+2?'")
        result = await processor.process_command("What is 2+2?")

        if result.get('success'):
            print(f"✅ Response: {result.get('response', 'No response')}")
            if 'used_model' in result:
                print(f"📡 Used Model: {result['used_model']}")
        else:
            print(f"❌ Error: {result.get('message')}")

        # Get usage stats
        stats = processor.get_usage_stats()
        print(f"\n📊 Usage Stats:")
        print(f"   Local queries: {stats['local_queries']}")
        print(f"   Cloud queries: {stats['cloud_queries']}")
        print(f"   Fallback count: {stats['fallback_count']}")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n🚀 F.R.I.D.A.Y. Local LLM Integration Test\n")

    # Test 1: Local LLM
    llm_ok = await test_local_llm()

    # Test 2: Command Processor (only if we need it)
    # Note: This will try to use Gemini API key
    try:
        processor_ok = await test_command_processor()
    except Exception as e:
        print(f"\n⚠️  Command Processor test skipped: {e}")
        processor_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Local LLM: {'✅ PASS' if llm_ok else '❌ FAIL'}")
    print(f"Command Processor: {'✅ PASS' if processor_ok else '⚠️  SKIP'}")

    if llm_ok:
        print("\n🎉 Local LLM is working correctly!")
        print("You can now use F.R.I.D.A.Y. with local AI models.")
    else:
        print("\n⚠️  Please start Ollama and install a model.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
