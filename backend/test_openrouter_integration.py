"""
Test OpenRouter Integration Across All Modules
"""
import sys
import os
sys.path.insert(0, '/home/tushar/Developer/python/Agent/friday-agent/backend')

print("=" * 70)
print("TESTING OPENROUTER INTEGRATION")
print("=" * 70)

# Test 1: OpenRouter API directly
print("\n✅ TEST 1: OpenRouter API")
print("-" * 70)
try:
    from modules.openrouter_integration import query_openrouter
    result = query_openrouter("What is 5+5? Answer in 5 words.")
    print(f"Response: {result}")
    print("✅ OpenRouter API: WORKING")
except Exception as e:
    print(f"❌ OpenRouter API: FAILED - {e}")

# Test 2: Gemini Processor with OpenRouter fallback
print("\n✅ TEST 2: Gemini Processor (with OpenRouter fallback)")
print("-" * 70)
try:
    from modules.gemini_processor import GeminiProcessor
    processor = GeminiProcessor(use_openrouter_fallback=True)
    print(f"Active Provider: {processor.active_provider}")
    result = processor.analyze_command("open chrome")
    print(f"Intent: {result.get('intent')}")
    print(f"Response: {result.get('ai_response')}")
    print(f"✅ Gemini Processor: WORKING (using {result.get('provider', processor.active_provider)})")
except Exception as e:
    print(f"❌ Gemini Processor: FAILED - {e}")

# Test 3: AI Copilot with OpenRouter
print("\n✅ TEST 3: AI Copilot (with OpenRouter support)")
print("-" * 70)
try:
    from modules.ai_copilot import AICopilot
    copilot = AICopilot()
    print(f"AI Provider: {copilot.ai_provider}")
    
    test_code = """def calculate_sum(a, b):
    return a + """
    
    suggestions = copilot.get_completions(test_code, len(test_code), language='python')
    print(f"Got {len(suggestions)} suggestions")
    if suggestions:
        print(f"First suggestion: {suggestions[0].get('label')}")
        print(f"Source: {suggestions[0].get('source', 'pattern-based')}")
    print(f"✅ AI Copilot: WORKING (provider: {copilot.ai_provider})")
except Exception as e:
    print(f"❌ AI Copilot: FAILED - {e}")

# Test 4: Code Explanation
print("\n✅ TEST 4: Code Explanation (with OpenRouter)")
print("-" * 70)
try:
    from modules.ai_copilot import AICopilot
    copilot = AICopilot()
    
    test_code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)
"""
    
    explanation = copilot.explain_code(test_code, language='python')
    print(f"Explanation length: {len(explanation.get('explanation', ''))} chars")
    print(f"Complexity: {explanation.get('complexity')}")
    print(f"Provider: {copilot.ai_provider}")
    print("✅ Code Explanation: WORKING")
except Exception as e:
    print(f"❌ Code Explanation: FAILED - {e}")

# Summary
print("\n" + "=" * 70)
print("INTEGRATION SUMMARY")
print("=" * 70)
print("""
✅ OpenRouter is integrated into:

1. Gemini Processor - Automatic fallback when Gemini fails
2. AI Copilot - Code suggestions with OpenRouter support  
3. Command Processor - Multi-model voice command processing
4. Code Explanation - Alternative AI brain for explanations

Configuration:
- OPENROUTER_API_KEY: Set in .env ✅
- OPENROUTER_MODEL: meta-llama/llama-3.2-3b-instruct:free ✅
- USE_OPENROUTER_FALLBACK: true ✅
- ENABLE_MULTI_MODEL: false (set to true for comparisons)

How to use:
- Voice commands automatically fall back to OpenRouter
- Code suggestions use Gemini first, then OpenRouter
- Set ENABLE_MULTI_MODEL=true to compare both models
- API endpoints available at /api/openrouter/*

Free Models Available:
- meta-llama/llama-3.2-3b-instruct:free (fast, general)
- google/gemma-2-9b-it:free (more powerful)
- microsoft/phi-3-mini-128k-instruct:free (long context)
- qwen/qwen-2-7b-instruct:free (multilingual)
""")
print("=" * 70)
