# Local Model Configuration Guide

This document explains how to configure and use local AI models with F.R.I.D.A.Y.

## Overview

F.R.I.D.A.Y. supports running AI models locally using Ollama, providing:

- 🔒 **Privacy**: Your data never leaves your machine
- 🚀 **Speed**: Fast inference on local hardware
- 💰 **Cost-effective**: No API fees
- 🔄 **Hybrid Mode**: Smart routing between local and cloud models

## Environment Variables

All configuration is stored in `backend/.env` (never commit this file!):

```env
# LLM Mode Selection
LLM_MODE=hybrid          # Options: local, cloud, hybrid

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL=qwen2.5-coder:7b
```

## Available Local Models

### 🚀 qwen2.5-coder:7b (RECOMMENDED)

- **Best for**: Coding tasks, debugging, code review
- **Size**: 4.7GB
- **Type**: Coding specialist
- **Use case**: Default model for development tasks

### ⚡ llama3.2:3b

- **Best for**: Quick general responses
- **Size**: 2.0GB
- **Type**: General purpose
- **Use case**: Fast conversations, simple queries

### 💎 gemma2:9b

- **Best for**: Balanced performance
- **Size**: 5.4GB
- **Type**: General purpose
- **Use case**: Complex reasoning tasks

### 💻 codellama:7b

- **Best for**: Code completion and explanation
- **Size**: 3.8GB
- **Type**: Coding specialist
- **Use case**: Alternative coding model

### 🧠 phi3:mini

- **Best for**: Efficient reasoning
- **Size**: 2.3GB
- **Type**: General purpose
- **Use case**: Low resource environments

## Setup Instructions

### 1. Install Ollama

**Linux:**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**

```bash
brew install ollama
```

**Windows:**
Download from https://ollama.ai/download

### 2. Start Ollama Service

```bash
ollama serve
```

### 3. Pull a Model

```bash
# Pull the recommended coding model
ollama pull qwen2.5-coder:7b

# Or pull a smaller model for testing
ollama pull llama3.2:3b
```

### 4. Configure F.R.I.D.A.Y.

Edit `backend/.env`:

```env
LLM_MODE=local                    # Use only local models
LOCAL_MODEL=qwen2.5-coder:7b     # Set your preferred model
OLLAMA_BASE_URL=http://localhost:11434
```

### 5. Restart Backend

```bash
cd backend
source ../.venv/bin/activate
python -m app.main
```

## LLM Modes

### Local Mode

```env
LLM_MODE=local
```

- Uses only Ollama/local models
- Complete privacy
- No internet required (after model download)
- Limited by local hardware

### Cloud Mode

```env
LLM_MODE=cloud
```

- Uses only Google Gemini
- Requires API key
- Best performance for complex tasks
- Internet connection required

### Hybrid Mode (Recommended)

```env
LLM_MODE=hybrid
```

- Automatically chooses best model for each task
- Coding tasks → Local models
- Complex reasoning → Cloud models
- Best of both worlds

## Switching Models

You can switch models at runtime via the API or frontend:

```python
# Via Python
await local_llm.set_model("llama3.2:3b")

# Via API endpoint
POST /api/llm/set-model
{
  "model": "llama3.2:3b"
}
```

## Security Notes

⚠️ **NEVER commit these files:**

- `backend/.env` (contains your API keys)
- `credentials.json` (Google credentials)
- Any `.key` or `.pem` files

✅ **Safe to commit:**

- `backend/.env.example` (template without secrets)
- Configuration documentation

The `.gitignore` file is configured to protect your credentials automatically.

## Troubleshooting

### Ollama not connecting

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### Model not found

```bash
# List installed models
ollama list

# Pull the model
ollama pull qwen2.5-coder:7b
```

### Out of memory

- Use smaller models (llama3.2:3b or phi3:mini)
- Close other applications
- Reduce context length in code

## Best Practices

1. **Start with hybrid mode** to get the best of both worlds
2. **Use qwen2.5-coder:7b** for coding tasks
3. **Keep models updated**: `ollama pull <model-name>`
4. **Monitor resources**: Local models use RAM/VRAM
5. **Backup your .env**: Copy `.env.example` before making changes

## Model Selection Guide

| Task              | Recommended Model | Mode         |
| ----------------- | ----------------- | ------------ |
| Code generation   | qwen2.5-coder:7b  | Local/Hybrid |
| Code review       | qwen2.5-coder:7b  | Local/Hybrid |
| Quick chat        | llama3.2:3b       | Local/Hybrid |
| Complex reasoning | Gemini            | Cloud/Hybrid |
| Documentation     | codellama:7b      | Local/Hybrid |
| General tasks     | gemma2:9b         | Local/Hybrid |

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Model Library](https://ollama.ai/library)
- [F.R.I.D.A.Y. Documentation](../README.md)
