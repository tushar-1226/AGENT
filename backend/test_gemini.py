"""
Test script for Gemini integration
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/tushar/Developer/python/Agent/friday-agent/backend')

from modules.gemini_processor import GeminiProcessor

def test_gemini():
    """Test Gemini AI processor"""
    print("=" * 50)
    print("Testing Gemini AI Integration")
    print("=" * 50)
    
    try:
        # Initialize processor
        print("\n1. Initializing Gemini processor...")
        gemini = GeminiProcessor()
        print("✓ Gemini processor initialized successfully")
        
        # Test commands
        test_commands = [
            "Hello Friday",
            "Open Chrome",
            "Can you launch my web browser?",
            "What apps are running?",
            "How are you?"
        ]
        
        print("\n2. Testing AI command analysis...\n")
        for cmd in test_commands:
            print(f"Command: '{cmd}'")
            result = gemini.analyze_command(cmd)
            
            if result['success']:
                print(f"  Intent: {result.get('intent')}")
                print(f"  App: {result.get('app_name')}")
                print(f"  Response: {result.get('ai_response')}")
            else:
                print(f"  Error: {result.get('error')}")
            print()
        
        print("=" * 50)
        print("✓ All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini()
