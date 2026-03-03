#!/bin/bash

# F.R.I.D.A.Y. Desktop Agent v2.1.0 - Enhanced Startup Script
# Starts backend, frontend, and optional services with health checks

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "═══════════════════════════════════════════════════════"
echo "   F.R.I.D.A.Y. Desktop Agent v2.1.0 - Starting..."
echo "═══════════════════════════════════════════════════════"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Trap Ctrl+C to gracefully shutdown
trap cleanup SIGINT SIGTERM

cleanup() {
    echo ""
    echo -e "${YELLOW}⚠  Shutting down F.R.I.D.A.Y...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✓  Shutdown complete${NC}"
    exit 0
}

# 1. Check Python environment
echo -e "${BLUE}📦 Checking Python environment...${NC}"
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
    echo -e "${YELLOW}   Creating virtual environment...${NC}"
    cd "$SCRIPT_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}   Installing backend dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}✓  Virtual environment created${NC}"
else
    echo -e "${GREEN}✓  Virtual environment found${NC}"
fi

# 2. Check backend environment variables
echo -e "${BLUE}🔧 Checking backend configuration...${NC}"
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo -e "${YELLOW}⚠  .env file not found, creating from template...${NC}"
    cat > "$SCRIPT_DIR/backend/.env" << EOF
# API Keys
GOOGLE_API_KEY=your_google_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Security (v2.1.0)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
RATE_LIMIT_PER_MINUTE=100
SECRET_KEY=$(openssl rand -hex 32)

# Features (v2.1.0)
ENABLE_CACHING=true
ENABLE_METRICS=true
ENABLE_CODE_INTELLIGENCE=true

# Database
DATABASE_URL=sqlite:///./users.db

# Server
HOST=0.0.0.0
PORT=8000
EOF
    echo -e "${YELLOW}⚠  Please update backend/.env with your API keys${NC}"
else
    echo -e "${GREEN}✓  Configuration found${NC}"
fi

# 3. Run database migrations
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
if [ -d "alembic" ]; then
    alembic upgrade head 2>/dev/null && echo -e "${GREEN}✓  Database migrations complete${NC}" || echo -e "${YELLOW}⚠  Migrations skipped (already up to date)${NC}"
else
    echo -e "${YELLOW}⚠  Alembic not configured, skipping migrations${NC}"
fi
cd "$SCRIPT_DIR"

# 4. Check frontend dependencies
echo -e "${BLUE}📦 Checking frontend dependencies...${NC}"
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo -e "${YELLOW}   Installing frontend dependencies...${NC}"
    cd "$SCRIPT_DIR/frontend"
    npm install
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}✓  Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓  Frontend dependencies found${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "   Starting Services..."
echo "═══════════════════════════════════════════════════════"
echo ""

# Clear old log files
rm -f "$SCRIPT_DIR/backend.log" "$SCRIPT_DIR/frontend.log"

# 5. Clean up existing processes on required ports
echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"

# Function to kill process on port with retry
kill_port() {
    local port=$1
    local retries=3
    
    for ((i=1; i<=retries; i++)); do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            if [ $i -eq 1 ]; then
                echo -e "${YELLOW}   Stopping existing process on port $port...${NC}"
            fi
            # Try graceful kill first, then force kill
            if [ $i -lt $retries ]; then
                kill $(lsof -t -i:$port) 2>/dev/null || true
            else
                kill -9 $(lsof -t -i:$port) 2>/dev/null || true
            fi
            sleep 2
        else
            break
        fi
    done
}

# Clean up ports
kill_port 8000
kill_port 3000
kill_port 3001
kill_port 3002

echo -e "${GREEN}✓  Ports cleaned up${NC}"

# 6. Start backend
echo -e "${BLUE}▶  Starting backend server...${NC}"
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH" python3 app/main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait and verify backend started
echo -n "   Waiting for backend to start"
for i in {1..10}; do
    sleep 1
    echo -n "."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓  Backend is running (PID: $BACKEND_PID)${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo ""
        echo -e "${RED}✗  Backend failed to start (check backend.log)${NC}"
        cleanup
        exit 1
    fi
done

# 7. Start frontend
echo -e "${BLUE}▶  Starting frontend server...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Wait and verify frontend started
echo -n "   Waiting for frontend to start"
FRONTEND_PORT=""
for i in {1..30}; do
    sleep 2
    echo -n "."
    # Check ports 3000, 3001, 3002 by checking if they're listening
    for port in 3000 3001 3002; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            FRONTEND_PORT=$port
            echo ""
            echo -e "${GREEN}✓  Frontend is running on port $FRONTEND_PORT (PID: $FRONTEND_PID)${NC}"
            break 2
        fi
    done
    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${YELLOW}⚠  Frontend may still be starting (check frontend.log)${NC}"
        # Show last few lines of frontend log for debugging
        echo -e "${YELLOW}   Last lines of frontend.log:${NC}"
        tail -5 frontend.log | sed 's/^/   /'
    fi
done

# Set default port if not detected
if [ -z "$FRONTEND_PORT" ]; then
    FRONTEND_PORT=3000
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "   🎉 F.R.I.D.A.Y. is now running!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}🌐 Access URLs:${NC}"
echo -e "   Frontend:  ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "   Backend:   ${BLUE}http://localhost:8000${NC}"
echo -e "   API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
echo -e "   Health:    ${BLUE}http://localhost:8000/health/detailed${NC}"
echo -e "   Metrics:   ${BLUE}http://localhost:8000/metrics${NC}"
echo ""
echo -e "${GREEN}📊 Process IDs:${NC}"
echo -e "   Backend PID:  $BACKEND_PID"
echo -e "   Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${GREEN}📝 Log Files:${NC}"
echo -e "   Backend:  ${BLUE}$SCRIPT_DIR/backend.log${NC}"
echo -e "   Frontend: ${BLUE}$SCRIPT_DIR/frontend.log${NC}"
echo ""
echo -e "${YELLOW}⚠  To stop all services:${NC}"
echo -e "   kill $BACKEND_PID $FRONTEND_PID"
echo -e "   or press ${YELLOW}Ctrl+C${NC}"
echo ""
echo "═══════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📊 Watching logs... (Press Ctrl+C to stop)${NC}"
echo ""

# Follow logs
tail -f backend.log frontend.log
