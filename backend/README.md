# Friday Agent Backend

AI-powered voice assistant backend with Google Gemini integration.

## Features

- 🤖 **Google Gemini AI** - Intelligent natural language understanding
- 🎤 **Voice Recognition** - Speech-to-text processing
- 🗣️ **Text-to-Speech** - Natural voice responses
- 🚀 **App Control** - Launch and manage applications
- ⚡ **WebSocket** - Real-time communication

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file with your Gemini API key:
```bash
cp .env.example .env
# Add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
# Get your key at: https://ai.google.dev/
```

## Running the Backend

```bash
# Activate venv first
source venv/bin/activate

# Run the server
python app/main.py
```

Or use uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Health check
- `GET /api/status` - System status
- `POST /api/command` - Execute text command
- `POST /api/apps/launch/{app_name}` - Launch app
- `POST /api/apps/close/{app_name}` - Close app
- `GET /api/apps/running` - List running apps
- `GET /api/apps/available` - List available apps
- `POST /api/voice/start` - Start voice recognition
- `POST /api/voice/stop` - Stop voice recognition
- `WS /ws` - WebSocket connection

## Voice Commands Examples

- "Open Chrome"
- "Launch Firefox"
- "Close Chrome"
- "What apps are running?"
- "Hello Friday"
- "Help"
