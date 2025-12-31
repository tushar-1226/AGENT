#!/bin/bash
# Ollama Startup Script for F.R.I.D.A.Y. Agent

echo "🚀 Starting Ollama Service..."

# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama is already running"
else
    echo "📦 Starting Ollama server..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    
    if pgrep -x "ollama" > /dev/null; then
        echo "✅ Ollama started successfully"
    else
        echo "❌ Failed to start Ollama"
        echo "Check logs: cat /tmp/ollama.log"
        exit 1
    fi
fi

# Check for installed models
echo ""
echo "📊 Checking installed models..."
MODELS=$(ollama list | tail -n +2)

if [ -z "$MODELS" ]; then
    echo "⚠️  No models installed!"
    echo ""
    echo "Recommended models for coding:"
    echo "  • qwen2.5-coder:7b (Best for coding - 4.7GB)"
    echo "  • llama3.2:3b (Fast general-purpose - 2.0GB)"
    echo "  • codellama:7b (Code specialized - 3.8GB)"
    echo ""
    echo "To install a model, run:"
    echo "  ollama pull qwen2.5-coder:7b"
    echo ""
    read -p "Would you like to pull qwen2.5-coder:7b now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⬇️  Downloading qwen2.5-coder:7b (this may take several minutes)..."
        ollama pull qwen2.5-coder:7b
        echo "✅ Model installed!"
    fi
else
    echo "✅ Installed models:"
    ollama list
fi

echo ""
echo "🎯 Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama API is responding"
else
    echo "❌ Ollama API is not responding"
    exit 1
fi

echo ""
echo "✅ Ollama is ready for F.R.I.D.A.Y. Agent!"
echo "   - API: http://localhost:11434"
echo "   - Mode: Set LLM_MODE=local or hybrid in .env"
