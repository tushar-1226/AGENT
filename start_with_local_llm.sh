#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "========================================================================"
echo -e "${BLUE} 🤖 F.R.I.D.A.Y. - Starting with Local LLM${NC}"
echo "========================================================================"
echo ""

# 1. Start Ollama
echo -e "${BLUE}Starting Ollama service...${NC}"
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✅ Ollama already running${NC}"
else
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✅ Ollama started${NC}"
fi

# Check model
echo -e "${BLUE}Checking installed models...${NC}"
if ollama list | grep -q "llama3.2:3b"; then
    echo -e "${GREEN}✅ llama3.2:3b is installed${NC}"
else
    echo -e "${YELLOW}⚠️  llama3.2:3b not found. Installing...${NC}"
    ollama pull llama3.2:3b
    echo -e "${GREEN}✅ Model installed${NC}"
fi

echo ""

# 2. Start Backend
echo -e "${BLUE}Starting backend server...${NC}"
cd /home/tushar/Developer/python/Agent/friday-agent

# Kill old backend if running
pkill -f "uvicorn app.main:app" 2>/dev/null

# Activate venv and start
source .venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Backend failed to start. Check backend.log${NC}"
fi

echo ""
echo "========================================================================"
echo -e "${GREEN} ✅ F.R.I.D.A.Y. is ready!${NC}"
echo "========================================================================"
echo ""
echo "  Services:"
echo "    • Ollama:   http://localhost:11434"
echo "    • Backend:  http://localhost:8000"
echo "    • Frontend: http://localhost:3001"
echo ""
echo "  Model:"
echo "    • llama3.2:3b (Local, Private, Fast)"
echo ""
echo "  Mode:"
echo "    • Hybrid (Local + Cloud fallback)"
echo ""
echo "  Quick Commands:"
echo "    • Test:   ./test_local_llm_integration.sh"
echo "    • Logs:   tail -f backend.log"
echo "    • Status: curl http://localhost:8000/api/local-llm/status"
echo ""
echo -e "${BLUE}  Press Ctrl+C to stop viewing logs${NC}"
echo ""

# Follow logs
tail -f ../backend.log
