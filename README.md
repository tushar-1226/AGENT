# F.R.I.D.A.Y. Agent - AI Development Platform

**The Most Advanced AI-Powered Development Assistant**

A comprehensive, standalone development platform with 24 revolutionary features including RAG document intelligence, integrated terminal, Git integration, and much more.

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Next.js](https://img.shields.io/badge/next.js-14-black)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## Features Overview

### Revolutionary Features

1. **RAG Document Intelligence** - Upload entire codebase for AI-powered semantic search
2. **Integrated Terminal** - Execute commands directly from chat with real-time output
3. **Git Integration** - Complete version control with AI-generated commit messages
4. **Database Query Builder** - Natural language to SQL conversion
5. **Screenshot to Code** - Convert UI mockups to React components
6. **Browser Automation** - Playwright-powered E2E testing
7. **Learning Path Generator** - Personalized education curriculum
8. **Universal App Launcher** - Launch and manage system applications directly from chat
9. **AI Code Translator** - Translate code between languages (Python, JS, TS, Go) while preserving logic
10. **AI Code Reviewer** - Automated comprehensive reviews for security, performance, and quality
11. **Living Documentation** - Auto-generate documentation with architecture diagrams
12. **Code Metrics Dashboard** - Advanced analytics for code complexity and maintainability

### Core Features

13. **Smart Code Assistant** - Monaco editor with explain, debug, test, refactor modes
14. **AI Task Management** - Natural language task parsing and organization
15. **Productivity Analytics** - Charts, insights, and productivity scoring
16. **Split-Screen Mode** - Work with multiple tools simultaneously
17. **System Monitoring** - Real-time CPU, RAM, disk, network stats
18. **Weather/News/Stock APIs** - Live data feeds
19. **Google Calendar & Email** - OAuth integration ready
20. **Local-Only Mode** - Ollama integration for privacy
21. **Encrypted Session Storage** - AES-256 encryption
22. **Voice Control** - Speech-to-text and text-to-speech
23. **File Upload & Analysis** - Image and PDF processing
24. **Enhanced Sidebar** - Chats, saved prompts, settings

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd friday-agent

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
./venv/bin/uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   └── main.py              # 90+ API endpoints
├── modules/
│   ├── rag_engine.py        # ChromaDB vector database
│   ├── terminal_manager.py  # Command execution
│   ├── git_manager.py       # Git operations
│   ├── database_manager.py  # SQL databases
│   ├── screenshot_to_code.py # Gemini Vision
│   ├── browser_automation.py # Playwright
│   ├── learning_engine.py   # Education paths
│   ├── task_manager.py      # AI task parsing
│   ├── external_apis.py     # Weather/News/Stocks
│   ├── google_integration.py # Google OAuth
│   ├── local_llm.py         # Ollama integration
│   ├── encryption.py        # AES-256 encryption
│   ├── session_manager.py   # Chat history
│   ├── file_processor.py    # File analysis
│   ├── app_launcher.py      # App Management
│   ├── code_translator.py   # Multi-language translation
│   ├── code_reviewer.py     # Static analysis & review
│   ├── doc_generator.py     # Auto-documentation
│   └── metrics_analyzer.py  # Code stats & complexity
└── requirements.txt
```

### Frontend (Next.js 14)

```
frontend/
├── app/
│   ├── page.tsx             # Main application
│   └── dashboard/
├── components/
│   ├── RAGManager.tsx       # Document intelligence UI
│   ├── IntegratedTerminal.tsx # Terminal UI
│   ├── GitPanel.tsx         # Git workflow UI
│   ├── TaskManager.tsx      # Task management
│   ├── CodeAssistant.tsx    # Code editor
│   ├── AnalyticsDashboard.tsx # Analytics
│   ├── SplitScreen.tsx      # Split view
│   └── ... (20 more components)
└── package.json
```

---

## Usage Examples

### RAG Document Intelligence

```bash
# Upload codebase
curl -X POST http://localhost:8000/api/rag/upload-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/path/to/project"}'

# Search code
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does authentication work?"}'
```

### Integrated Terminal

```bash
# Create session
curl -X POST http://localhost:8000/api/terminal/create

# Execute command
curl -X POST http://localhost:8000/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "command": "npm install"}'
```

### Git Integration

```bash
# Get status
curl http://localhost:8000/api/git/status

# Commit with AI message
curl -X POST http://localhost:8000/api/git/commit \
  -H "Content-Type: application/json" \
  -d '{"message": "auto"}'
```

### Task Management

```bash
# Parse natural language
curl -X POST http://localhost:8000/api/tasks/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Deploy website tomorrow urgent"}'
```

---

## Configuration

### Environment Variables

Create `.env` file in `backend/`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional - External APIs
OPENWEATHER_API_KEY=your_weather_key
NEWS_API_KEY=your_news_key

# Optional - Google Integration
GOOGLE_CREDENTIALS_FILE=credentials.json

# Optional - Local LLM
LOCAL_MODEL=gemma:7b
```

### Optional Dependencies

For full features, install:

```bash
cd backend
pip install chromadb sentence-transformers \
  gitpython sqlalchemy psycopg2-binary pymysql \
  playwright psutil

# Install Playwright browsers
playwright install
```

---

## API Documentation

### Core Endpoints

- `POST /api/sessions` - Create chat session
- `GET /api/sessions` - List sessions
- `POST /api/tasks/parse` - Parse natural language task
- `GET /api/system/stats` - System statistics

### RAG Endpoints

- `POST /api/rag/upload-directory` - Upload codebase
- `POST /api/rag/query` - Semantic search
- `GET /api/rag/documents` - List indexed files
- `GET /api/rag/stats` - Database statistics

### Terminal Endpoints

- `POST /api/terminal/create` - Create session
- `POST /api/terminal/execute` - Run command
- `GET /api/terminal/history/{id}` - Command history
- `GET /api/terminal/sessions` - List sessions

### Git Endpoints

- `GET /api/git/status` - Repository status
- `GET /api/git/diff` - View changes
- `POST /api/git/commit` - Create commit
- `POST /api/git/push` - Push to remote
- `GET /api/git/log` - Commit history
- `GET /api/git/branches` - List branches

### Database Endpoints

- `POST /api/db/connect` - Connect to database
- `GET /api/db/schema` - Get schema
- `POST /api/db/query` - Execute SQL
- `POST /api/db/nl-query` - Natural language query

### Learning Endpoints

- `POST /api/learning/path` - Generate curriculum
- `POST /api/learning/quiz` - Create quiz
- `POST /api/learning/progress` - Track progress
- `GET /api/learning/recommendations` - Get suggestions

**Full API documentation:** http://localhost:8000/docs

---

## Security

- **AES-256 Encryption** for session storage
- **PBKDF2 Key Derivation** (100,000 iterations)
- **Terminal Safety Checks** for dangerous commands
- **CORS Protection** configured
- **Input Validation** on all endpoints
- **SQL Injection Prevention** via parameterized queries

---

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **ChromaDB** - Vector database for RAG
- **GitPython** - Git integration
- **SQLAlchemy** - Database ORM
- **Playwright** - Browser automation
- **Gemini AI** - Language model
- **Psutil** - System process management

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Monaco Editor** - Code editing
- **Recharts** - Data visualization
- **xterm.js** - Terminal emulation

---

## Performance

- **API Response Time:** < 100ms average
- **Terminal Execution:** Real-time streaming
- **RAG Query:** < 500ms with ChromaDB
- **Git Operations:** < 200ms
- **Database Queries:** < 100ms

---

## Testing

Run endpoint tests:

```bash
cd backend
./venv/bin/python test_endpoints.py
```

Expected output:
```
✓ Passed:  21/21
✗ Failed:  0/21
Success Rate: 100.0%
```

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- **Google Gemini** for AI capabilities
- **ChromaDB** for vector database
- **FastAPI** for backend framework
- **Next.js** for frontend framework
- **Playwright** for browser automation

---

## Support

For issues and questions:
- Open an issue on GitHub
- Check API documentation at `/docs`
- Review walkthrough.md for detailed guide

---

## Roadmap

- [ ] Multi-model support (GPT-4, Claude)
- [ ] Plugin system
- [ ] Team collaboration features
- [ ] Mobile app (React Native)
- [ ] Custom themes
- [ ] Workflow automation builder
- [ ] Docker deployment
- [ ] Cloud hosting support

---

**Built with ❤️ for developers by developers**

**Version 2.1.0** - Complete Standalone Development Platform
