#!/bin/bash

# F.R.I.D.A.Y. Desktop Agent - Startup Script

echo " Starting F.R.I.D.A.Y. Desktop Agent..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if backend venv exists
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
    echo " Virtual environment not found. Creating one..."
    cd "$SCRIPT_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    echo " Installing backend dependencies..."
    pip install -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo " Virtual environment found"
fi

# Check if frontend node_modules exists
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo " Frontend dependencies not found. Installing..."
    cd "$SCRIPT_DIR/frontend"
    npm install
    cd "$SCRIPT_DIR"
else
    echo " Frontend dependencies found"
fi

echo ""
echo " Starting services..."
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    # Check if Ollama is already running
    if ! pgrep -x "ollama" > /dev/null; then
        echo "▶  Starting Ollama (Local LLM)..."
        ollama serve > "$SCRIPT_DIR/ollama.log" 2>&1 &
        OLLAMA_PID=$!
        echo "   Ollama PID: $OLLAMA_PID"

        # Wait for Ollama to start
        sleep 2

        # Check if Ollama started successfully
        if pgrep -x "ollama" > /dev/null; then
            echo "    Ollama is running"
        else
            echo "     Ollama failed to start (check ollama.log)"
        fi
    else
        echo "▶  Ollama is already running"
    fi
else
    echo "  Ollama not installed - Local LLM mode will not be available"
    echo "   Install: curl -fsSL https://ollama.ai/install.sh | sh"
fi

echo ""

# Start backend in background
echo "▶  Starting backend..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH" python app/main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
cd "$SCRIPT_DIR"

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "▶  Starting frontend..."
cd "$SCRIPT_DIR/frontend"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd "$SCRIPT_DIR"

echo ""
echo " F.R.I.D.A.Y. is now running!"
echo ""
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
if [ ! -z "$OLLAMA_PID" ]; then
    echo "   Ollama PID:   $OLLAMA_PID"
fi
echo ""
echo " Logs:"
echo "   Backend:  $SCRIPT_DIR/backend.log"
echo "   Frontend: $SCRIPT_DIR/frontend.log"
if [ ! -z "$OLLAMA_PID" ]; then
    echo "   Ollama:   $SCRIPT_DIR/ollama.log"
fi
echo ""
if [ ! -z "$OLLAMA_PID" ]; then
    echo "  To stop, run: kill $BACKEND_PID $FRONTEND_PID $OLLAMA_PID"
else
    echo "  To stop, run: kill $BACKEND_PID $FRONTEND_PID"
fi
echo ""
echo "Press Ctrl+C to view logs in real-time..."

# Follow logs
if [ ! -z "$OLLAMA_PID" ]; then
    tail -f backend.log frontend.log ollama.log
else
    tail -f backend.log frontend.log
fi
