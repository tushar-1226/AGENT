#!/bin/bash

# F.R.I.D.A.Y. Security & Configuration Checker
# This script verifies that credentials are properly protected

echo "🔒 F.R.I.D.A.Y. Security & Configuration Check"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .gitignore exists
echo "📋 Checking .gitignore..."
if [ -f .gitignore ]; then
    echo -e "${GREEN}✓${NC} .gitignore file exists"
else
    echo -e "${RED}✗${NC} .gitignore file missing!"
    exit 1
fi

# Check if .env is ignored
echo ""
echo "🔐 Checking credential protection..."
if git check-ignore -q backend/.env; then
    echo -e "${GREEN}✓${NC} backend/.env is ignored by git"
else
    echo -e "${RED}✗${NC} WARNING: backend/.env is NOT ignored!"
fi

if git check-ignore -q credentials.json; then
    echo -e "${GREEN}✓${NC} credentials.json is ignored by git"
else
    echo -e "${YELLOW}⚠${NC} credentials.json not found (OK if not using Google integration)"
fi

# Check if log files are ignored
if git check-ignore -q backend.log; then
    echo -e "${GREEN}✓${NC} Log files are ignored"
else
    echo -e "${YELLOW}⚠${NC} Log files may not be ignored"
fi

# Check if .env file exists
echo ""
echo "⚙️  Checking configuration files..."
if [ -f backend/.env ]; then
    echo -e "${GREEN}✓${NC} backend/.env exists"

    # Check for required variables
    if grep -q "LOCAL_MODEL=" backend/.env; then
        MODEL=$(grep "LOCAL_MODEL=" backend/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} LOCAL_MODEL is set to: $MODEL"
    else
        echo -e "${RED}✗${NC} LOCAL_MODEL not configured"
    fi

    if grep -q "OLLAMA_BASE_URL=" backend/.env; then
        OLLAMA_URL=$(grep "OLLAMA_BASE_URL=" backend/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} OLLAMA_BASE_URL is set to: $OLLAMA_URL"
    else
        echo -e "${RED}✗${NC} OLLAMA_BASE_URL not configured"
    fi

    if grep -q "LLM_MODE=" backend/.env; then
        MODE=$(grep "LLM_MODE=" backend/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} LLM_MODE is set to: $MODE"
    else
        echo -e "${YELLOW}⚠${NC} LLM_MODE not set (will use default)"
    fi
else
    echo -e "${RED}✗${NC} backend/.env file missing!"
    echo "   Copy backend/.env.example to backend/.env and configure it"
fi

if [ -f backend/.env.example ]; then
    echo -e "${GREEN}✓${NC} backend/.env.example exists (template)"
else
    echo -e "${YELLOW}⚠${NC} backend/.env.example missing"
fi

# Check for accidentally committed secrets
echo ""
echo "🔍 Checking for committed secrets..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git ls-files | grep -q "\.env$\|credentials\.json$\|\.pem$\|\.key$"; then
        echo -e "${RED}✗${NC} WARNING: Credential files found in git!"
        echo "   These files are tracked and may be committed:"
        git ls-files | grep "\.env$\|credentials\.json$\|\.pem$\|\.key$"
    else
        echo -e "${GREEN}✓${NC} No credential files are tracked by git"
    fi
else
    echo -e "${YELLOW}⚠${NC} Not a git repository (skipping)"
fi

# Check Ollama connection (if configured)
echo ""
echo "🤖 Checking Ollama connection..."
if [ -f backend/.env ]; then
    source backend/.env
    if curl -s "$OLLAMA_BASE_URL/api/tags" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama is running at $OLLAMA_BASE_URL"

        # List installed models
        MODELS=$(curl -s "$OLLAMA_BASE_URL/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
        if [ ! -z "$MODELS" ]; then
            echo -e "${GREEN}✓${NC} Installed models:"
            echo "$MODELS" | while read model; do
                echo "   - $model"
            done

            # Check if configured model is installed
            if echo "$MODELS" | grep -q "^$LOCAL_MODEL$"; then
                echo -e "${GREEN}✓${NC} Configured model ($LOCAL_MODEL) is installed"
            else
                echo -e "${YELLOW}⚠${NC} Configured model ($LOCAL_MODEL) is NOT installed"
                echo "   Run: ollama pull $LOCAL_MODEL"
            fi
        else
            echo -e "${YELLOW}⚠${NC} No models installed"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Ollama is not running (OK if using cloud mode)"
        echo "   Start with: ollama serve"
    fi
fi

# Summary
echo ""
echo "=============================================="
echo "✨ Configuration check complete!"
echo ""
echo "📚 For more information, see:"
echo "   - LOCAL_MODELS.md (local model setup)"
echo "   - README.md (general documentation)"
echo ""
