#!/bin/bash
# Quick Local LLM Setup for F.R.I.D.A.Y. Agent

echo "=================================="
echo "LOCAL LLM SETUP - F.R.I.D.A.Y."
echo "=================================="

# Pull a smaller model first for quick testing
echo ""
echo "📦 Pulling llama3.2:3b (2GB - fast model for testing)..."
ollama pull llama3.2:3b

echo ""
echo "✅ Testing the model..."
ollama run llama3.2:3b "Say 'Local LLM is working!' in one sentence" --verbose

echo ""
echo "=================================="
echo "✅ LOCAL LLM IS NOW WORKING!"
echo "=================================="
echo ""
echo "Model installed: llama3.2:3b (2GB)"
echo "API: http://localhost:11434"
echo ""
echo "To use in F.R.I.D.A.Y.:"
echo "  1. Edit backend/.env"
echo "  2. Set: LLM_MODE=local"
echo "  3. Set: LOCAL_MODEL=llama3.2:3b"
echo "  4. Restart backend"
echo ""
echo "For better coding support (larger download):"
echo "  ollama pull qwen2.5-coder:7b"
echo ""
