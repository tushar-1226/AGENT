"""
Friday Agent - Main Application Entry Point
FastAPI backend with WebSocket support for real-time communication
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from typing import List
import json
from datetime import datetime

from modules.voice_recognition import VoiceRecognizer
from modules.text_to_speech import TextToSpeech
from modules.app_launcher import AppLauncher
from modules.command_processor import CommandProcessor
from modules.session_manager import SessionManager
from modules.file_processor import FileProcessor
from modules.external_apis import ExternalAPIs
from modules.task_manager import TaskManager
from modules.google_integration import GoogleIntegration
from modules.local_llm import LocalLLM, HybridLLM
from modules.gemini_processor import GeminiProcessor
from modules.rag_engine import RAGEngine
from modules.terminal_manager import TerminalManager
from modules.git_manager import GitManager
from modules.database_manager import DatabaseManager
from modules.screenshot_to_code import ScreenshotToCode
from modules.browser_automation import BrowserAutomation
from modules.learning_engine import LearningEngine
from modules.auth_manager import AuthManager
from modules.project_manager import ProjectManager
from modules.system_monitor import SystemMonitor
from modules.analytics_manager import AnalyticsManager

# Advanced AI modules
from modules.multi_agent_system import MultiAgentSystem
from modules.ai_testing_suite import AITestingSuite
from modules.knowledge_graph import TeamKnowledgeGraph
from modules.predictive_analytics import PredictiveAnalyticsDashboard
from modules.security_copilot import SecurityCopilot
from modules.performance_profiler import PerformanceProfiler
from modules.workflow_automation import WorkflowAutomationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Friday Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize only essential modules at startup for faster boot time
# Other modules will be lazy-loaded when needed
logger.info("Initializing Friday Agent API...")

# Core modules (always needed)
tts = TextToSpeech()
app_launcher = AppLauncher()
# Note: CommandProcessor will be initialized after LLM modules to ensure proper dependency injection
command_processor = None
voice_recognizer = None
session_manager = SessionManager()
auth_manager = AuthManager()  # Initialize auth manager
project_manager = ProjectManager()  # Initialize project manager
system_monitor = SystemMonitor()  # Initialize system monitor
analytics_manager = AnalyticsManager()  # Initialize analytics manager

# Lazy-loaded modules (initialized on first use)
file_processor = None
external_apis = None
task_manager = None
google_integration = None
gemini_processor = None
local_llm = None
hybrid_llm = None
rag_engine = None
terminal_manager = None
git_manager = None
database_manager = None
screenshot_to_code = None
browser_automation = None
learning_engine = None

# Advanced AI modules (lazy-loaded)
multi_agent_system = None
ai_testing_suite = None
knowledge_graph = None
predictive_analytics = None
security_copilot = None
performance_profiler = None
workflow_automation = None

# New feature modules (lazy-loaded)
ai_copilot = None
integrated_debugger = None
code_snippets = None

# New advanced feature modules (lazy-loaded)
collaborative_features = None
ai_pair_programmer = None
visual_programming = None
code_search_navigation = None
smart_testing_suite = None


def get_file_processor():
    global file_processor
    if file_processor is None:
        from modules.file_processor import FileProcessor

        file_processor = FileProcessor()
        logger.info("Initialized FileProcessor")
    return file_processor


def get_external_apis():
    global external_apis
    if external_apis is None:
        from modules.external_apis import ExternalAPIs

        external_apis = ExternalAPIs()
        logger.info("Initialized ExternalAPIs")
    return external_apis


def get_task_manager():
    global task_manager
    if task_manager is None:
        from modules.task_manager import TaskManager

        task_manager = TaskManager()
        logger.info("Initialized TaskManager")
    return task_manager


def get_google_integration():
    global google_integration
    if google_integration is None:
        from modules.google_integration import GoogleIntegration

        google_integration = GoogleIntegration()
        logger.info("Initialized GoogleIntegration")
    return google_integration


def get_gemini_processor():
    global gemini_processor
    if gemini_processor is None:
        from modules.gemini_processor import GeminiProcessor

        gemini_processor = GeminiProcessor()
        logger.info("Initialized GeminiProcessor")
    return gemini_processor


def get_local_llm():
    global local_llm
    if local_llm is None:
        from modules.local_llm import LocalLLM

        local_llm = LocalLLM()
        logger.info("Initialized LocalLLM")
    return local_llm


def get_hybrid_llm():
    global hybrid_llm
    if hybrid_llm is None:
        from modules.local_llm import HybridLLM

        hybrid_llm = HybridLLM(get_gemini_processor(), get_local_llm())
        logger.info("Initialized HybridLLM")
    return hybrid_llm


def get_rag_engine():
    global rag_engine
    if rag_engine is None:
        from modules.rag_engine import RAGEngine

        rag_engine = RAGEngine()
        logger.info("Initialized RAGEngine")
    return rag_engine


def get_terminal_manager():
    global terminal_manager
    if terminal_manager is None:
        from modules.terminal_manager import TerminalManager

        terminal_manager = TerminalManager()
        logger.info("Initialized TerminalManager")
    return terminal_manager


def get_git_manager():
    global git_manager
    if git_manager is None:
        from modules.git_manager import GitManager

        git_manager = GitManager()
        logger.info("Initialized GitManager")
    return git_manager


def get_database_manager():
    global database_manager
    if database_manager is None:
        from modules.database_manager import DatabaseManager

        database_manager = DatabaseManager()
        logger.info("Initialized DatabaseManager")
    return database_manager


def get_screenshot_to_code():
    global screenshot_to_code
    if screenshot_to_code is None:
        from modules.screenshot_to_code import ScreenshotToCode

        screenshot_to_code = ScreenshotToCode()
        logger.info("Initialized ScreenshotToCode")
    return screenshot_to_code


def get_browser_automation():
    global browser_automation
    if browser_automation is None:
        from modules.browser_automation import BrowserAutomation

        browser_automation = BrowserAutomation()
        logger.info("Initialized BrowserAutomation")
    return browser_automation


def get_learning_engine():
    global learning_engine
    if learning_engine is None:
        from modules.learning_engine import LearningEngine

        learning_engine = LearningEngine()
        logger.info("Initialized LearningEngine")
    return learning_engine


def get_multi_agent_system():
    global multi_agent_system
    if multi_agent_system is None:
        from modules.multi_agent_system import MultiAgentSystem

        multi_agent_system = MultiAgentSystem()
        logger.info("Initialized MultiAgentSystem")
    return multi_agent_system


def get_ai_testing_suite():
    global ai_testing_suite
    if ai_testing_suite is None:
        from modules.ai_testing_suite import AITestingSuite

        ai_testing_suite = AITestingSuite()
        logger.info("Initialized AITestingSuite")
    return ai_testing_suite


def get_knowledge_graph():
    global knowledge_graph
    if knowledge_graph is None:
        from modules.knowledge_graph import TeamKnowledgeGraph

        knowledge_graph = TeamKnowledgeGraph()
        logger.info("Initialized TeamKnowledgeGraph")
    return knowledge_graph


def get_predictive_analytics():
    global predictive_analytics
    if predictive_analytics is None:
        from modules.predictive_analytics import PredictiveAnalyticsDashboard

        predictive_analytics = PredictiveAnalyticsDashboard()
        logger.info("Initialized PredictiveAnalyticsDashboard")
    return predictive_analytics


def get_security_copilot():
    global security_copilot
    if security_copilot is None:
        from modules.security_copilot import SecurityCopilot

        security_copilot = SecurityCopilot()
        logger.info("Initialized SecurityCopilot")
    return security_copilot


def get_collaborative_features():
    global collaborative_features
    if collaborative_features is None:
        from modules.collaborative_features import CollaborativeFeatures
        
        collaborative_features = CollaborativeFeatures()
        logger.info("Initialized CollaborativeFeatures")
    return collaborative_features


def get_ai_pair_programmer():
    global ai_pair_programmer
    if ai_pair_programmer is None:
        from modules.ai_pair_programmer import AIPairProgrammer
        
        ai_pair_programmer = AIPairProgrammer(get_gemini_processor())
        logger.info("Initialized AIPairProgrammer")
    return ai_pair_programmer


def get_visual_programming():
    global visual_programming
    if visual_programming is None:
        from modules.visual_programming import VisualProgramming
        
        visual_programming = VisualProgramming(get_gemini_processor())
        logger.info("Initialized VisualProgramming")
    return visual_programming


def get_code_search_navigation():
    global code_search_navigation
    if code_search_navigation is None:
        from modules.code_search_navigation import CodeSearchNavigation
        
        code_search_navigation = CodeSearchNavigation(get_gemini_processor())
        logger.info("Initialized CodeSearchNavigation")
    return code_search_navigation


def get_smart_testing_suite():
    global smart_testing_suite
    if smart_testing_suite is None:
        from modules.smart_testing_suite import SmartTestingSuite
        
        smart_testing_suite = SmartTestingSuite(get_gemini_processor())
        logger.info("Initialized SmartTestingSuite")
    return smart_testing_suite


def get_performance_profiler():
    global performance_profiler
    if performance_profiler is None:
        from modules.performance_profiler import PerformanceProfiler

        performance_profiler = PerformanceProfiler()
        logger.info("Initialized PerformanceProfiler")
    return performance_profiler


def get_workflow_automation():
    global workflow_automation
    if workflow_automation is None:
        from modules.workflow_automation import WorkflowAutomationEngine

        workflow_automation = WorkflowAutomationEngine()
        logger.info("Initialized WorkflowAutomationEngine")
    return workflow_automation


def get_command_processor():
    """Get or initialize the CommandProcessor with proper LLM instances"""
    global command_processor
    if command_processor is None:
        from modules.command_processor import CommandProcessor

        # Initialize with lazy-loaded instances to ensure proper sharing
        command_processor = CommandProcessor(
            app_launcher,
            tts,
            local_llm=get_local_llm(),
            gemini=get_gemini_processor(),
            browser_automation=get_browser_automation()
        )
        logger.info("Initialized CommandProcessor with LLM instances")
    return command_processor


logger.info("Friday Agent API initialized successfully")

# Store active WebSocket connections
active_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "Friday Agent API is running", "status": "online"}


# ============= Authentication Endpoints =============


@app.post("/api/auth/register")
async def register(data: dict):
    """Register a new user"""
    try:
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not all([email, password, name]):
            return JSONResponse(
                status_code=400,
                content={"error": "Email, password, and name are required"},
            )

        result = auth_manager.register_user(email, password, name)

        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content={"error": result.get("error", "Registration failed")},
            )

        return {"user": result["user"], "token": result["token"]}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/auth/login")
async def login(data: dict):
    """Login user"""
    try:
        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return JSONResponse(
                status_code=400, content={"error": "Email and password are required"}
            )

        result = auth_manager.login_user(email, password)

        if not result.get("success"):
            return JSONResponse(
                status_code=401, content={"error": result.get("error", "Login failed")}
            )

        return {"user": result["user"], "token": result["token"]}
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/auth/logout")
async def logout(data: dict):
    """Logout user"""
    try:
        token = data.get("token")
        if not token:
            return JSONResponse(status_code=400, content={"error": "Token is required"})

        auth_manager.logout_user(token)
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/auth/verify")
async def verify_token(token: str):
    """Verify authentication token"""
    try:
        user = auth_manager.verify_token(token)
        if not user:
            return JSONResponse(
                status_code=401, content={"error": "Invalid or expired token"}
            )
        return {"user": user}
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= Project Management Endpoints =============


@app.post("/api/projects")
async def create_project(data: dict):
    """Create a new project"""
    try:
        name = data.get("name")
        description = data.get("description", "")
        user_id = data.get("user_id")
        metadata = data.get("metadata", {})

        if not name:
            return JSONResponse(
                status_code=400, content={"error": "Project name is required"}
            )

        result = project_manager.create_project(name, description, user_id, metadata)

        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content={"error": result.get("error", "Failed to create project")},
            )

        return result["project"]
    except Exception as e:
        logger.error(f"Create project error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/projects")
async def get_projects(user_id: int = None):
    """Get all projects"""
    try:
        projects = project_manager.get_projects(user_id)
        return {"projects": projects}
    except Exception as e:
        logger.error(f"Get projects error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Get a specific project"""
    try:
        project = project_manager.get_project(project_id)
        if not project:
            return JSONResponse(status_code=404, content={"error": "Project not found"})
        return project
    except Exception as e:
        logger.error(f"Get project error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, data: dict):
    """Update a project"""
    try:
        name = data.get("name")
        description = data.get("description")
        metadata = data.get("metadata")

        success = project_manager.update_project(
            project_id, name, description, metadata
        )

        if not success:
            return JSONResponse(
                status_code=400, content={"error": "Failed to update project"}
            )

        return {"message": "Project updated successfully"}
    except Exception as e:
        logger.error(f"Update project error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """Delete a project"""
    try:
        success = project_manager.delete_project(project_id)

        if not success:
            return JSONResponse(
                status_code=400, content={"error": "Failed to delete project"}
            )

        return {"message": "Project deleted successfully"}
    except Exception as e:
        logger.error(f"Delete project error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= Chat History Endpoints =============


@app.post("/api/chat/history")
async def add_chat_message(data: dict):
    """Add a chat message to history"""
    try:
        message = data.get("message")
        response = data.get("response")
        project_id = data.get("project_id")
        user_id = data.get("user_id")

        if not message:
            return JSONResponse(
                status_code=400, content={"error": "Message is required"}
            )

        success = project_manager.add_chat_message(
            message, response, project_id, user_id
        )

        if not success:
            return JSONResponse(
                status_code=400, content={"error": "Failed to save chat message"}
            )

        return {"message": "Chat message saved successfully"}
    except Exception as e:
        logger.error(f"Add chat message error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/chat/history")
async def get_chat_history(
    project_id: int = None, user_id: int = None, limit: int = 100
):
    """Get chat history"""
    try:
        history = project_manager.get_chat_history(project_id, user_id, limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/chat/search")
async def search_chat_history(q: str, user_id: int = None, limit: int = 50):
    """Search chat history"""
    try:
        if not q:
            return JSONResponse(
                status_code=400, content={"error": "Search query is required"}
            )

        results = project_manager.search_chat_history(q, user_id, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Search chat history error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= Analytics Endpoints =============

@app.get("/api/analytics/complete")
async def get_complete_analytics(hours: int = 24):
    """Get complete analytics overview"""
    try:
        analytics = analytics_manager.get_complete_analytics(hours)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/api-calls")
async def get_api_call_analytics(hours: int = 24):
    """Get API call statistics"""
    try:
        stats = analytics_manager.get_api_call_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Error getting API call analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/user-activity")
async def get_user_activity_analytics(hours: int = 24):
    """Get user activity statistics"""
    try:
        stats = analytics_manager.get_user_activity_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Error getting user activity analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/errors")
async def get_error_analytics(hours: int = 24):
    """Get error statistics"""
    try:
        stats = analytics_manager.get_error_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Error getting error analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/quality")
async def get_quality_metrics():
    """Get quality metrics"""
    try:
        metrics = analytics_manager.get_quality_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting quality metrics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/analytics/log-api-call")
async def log_api_call(data: dict):
    """Log an API call for analytics"""
    try:
        success = analytics_manager.log_api_call(
            endpoint=data.get("endpoint", ""),
            method=data.get("method", ""),
            status_code=data.get("status_code", 0),
            response_time=data.get("response_time", 0.0),
            user_id=data.get("user_id"),
            error_message=data.get("error_message"),
            request_size=data.get("request_size", 0),
            response_size=data.get("response_size", 0)
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Error logging API call: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/analytics/log-activity")
async def log_user_activity(data: dict):
    """Log user activity for analytics"""
    try:
        success = analytics_manager.log_user_activity(
            user_id=data.get("user_id"),
            action=data.get("action", ""),
            details=data.get("details")
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= Analytics Endpoints =============

@app.get("/api/analytics/complete")
async def get_complete_analytics(hours: int = 24):
    """Get complete analytics overview"""
    try:
        analytics = analytics_manager.get_complete_analytics(hours)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/api-calls")
async def get_api_call_analytics(hours: int = 24):
    """Get API call statistics"""
    try:
        stats = analytics_manager.get_api_call_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Error getting API call analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/user-activity")
async def get_user_activity_analytics(hours: int = 24):
    """Get user activity statistics"""
    try:
        stats = analytics_manager.get_user_activity_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Error getting user activity analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/errors")
async def get_error_analytics(hours: int = 24):
    """Get error statistics"""
    try:
        stats = analytics_manager.get_error_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Error getting error analytics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/analytics/quality")
async def get_quality_metrics():
    """Get quality metrics"""
    try:
        metrics = analytics_manager.get_quality_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting quality metrics: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/analytics/log-api-call")
async def log_api_call(data: dict):
    """Log an API call for analytics"""
    try:
        success = analytics_manager.log_api_call(
            endpoint=data.get("endpoint", ""),
            method=data.get("method", ""),
            status_code=data.get("status_code", 0),
            response_time=data.get("response_time", 0.0),
            user_id=data.get("user_id"),
            error_message=data.get("error_message"),
            request_size=data.get("request_size", 0),
            response_size=data.get("response_size", 0)
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Error logging API call: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/analytics/log-activity")
async def log_user_activity(data: dict):
    """Log user activity for analytics"""
    try:
        success = analytics_manager.log_user_activity(
            user_id=data.get("user_id"),
            action=data.get("action", ""),
            details=data.get("details")
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "voice_active": voice_recognizer is not None and voice_recognizer.listening,
        "running_apps": app_launcher.list_running_apps(),
    }


@app.get("/api/system/complete")
async def get_complete_system_stats():
    """Get complete comprehensive system statistics"""
    try:
        return system_monitor.get_complete_system_stats()
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/system/stats")
async def get_system_stats():
    """Get real-time system statistics"""
    import psutil

    # CPU stats
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_freq = psutil.cpu_freq()

    # Memory stats
    memory = psutil.virtual_memory()

    # Disk stats
    disk = psutil.disk_usage("/")

    # Network stats
    net_io = psutil.net_io_counters()

    return {
        "cpu": {
            "percent": cpu_percent,
            "per_core": cpu_per_core,
            "cores": psutil.cpu_count(),
            "frequency": {
                "current": cpu_freq.current if cpu_freq else 0,
                "min": cpu_freq.min if cpu_freq else 0,
                "max": cpu_freq.max if cpu_freq else 0,
            },
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
        },
        "network": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/docs/model")
async def get_model_docs():
    """Get comprehensive model documentation"""
    return {
        "model": {
            "name": "Gemini 2.5 Flash",
            "provider": "Google AI",
            "version": "2.5",
            "type": "Large Language Model",
            "description": "Advanced AI model for natural language understanding and command processing",
        },
        "capabilities": [
            {
                "name": "Natural Language Understanding",
                "description": "Processes user commands in natural language and extracts intent",
                "examples": ["open chrome", "what apps are running", "close firefox"],
            },
            {
                "name": "Intent Recognition",
                "description": "Identifies user intent from various command patterns",
                "intents": [
                    "launch_app",
                    "close_app",
                    "list_apps",
                    "greeting",
                    "status",
                    "help",
                ],
            },
            {
                "name": "Application Control",
                "description": "Controls desktop applications through voice and text commands",
                "actions": ["launch", "close", "list running", "list available"],
            },
            {
                "name": "Conversational AI",
                "description": "Engages in natural conversations with context awareness",
                "features": ["Greetings", "Status checks", "Help requests"],
            },
        ],
        "api_endpoints": [
            {
                "method": "POST",
                "path": "/api/command",
                "description": "Execute a text command",
                "parameters": {"text": "string - The command to execute"},
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "response": "string",
                },
            },
            {
                "method": "GET",
                "path": "/api/status",
                "description": "Get system status",
                "response": {
                    "status": "string",
                    "timestamp": "string",
                    "voice_active": "boolean",
                    "running_apps": "array",
                },
            },
            {
                "method": "POST",
                "path": "/api/apps/launch/{app_name}",
                "description": "Launch a specific application",
                "parameters": {
                    "app_name": "string - Name of the application to launch"
                },
            },
            {
                "method": "POST",
                "path": "/api/apps/close/{app_name}",
                "description": "Close a specific application",
                "parameters": {"app_name": "string - Name of the application to close"},
            },
        ],
        "usage_examples": [
            {
                "title": "Execute a Command",
                "code": 'POST /api/command\n{\n  "text": "open chrome"\n}',
                "language": "http",
            },
            {
                "title": "Get System Status",
                "code": "GET /api/status",
                "language": "http",
            },
            {
                "title": "Launch Application",
                "code": "POST /api/apps/launch/firefox",
                "language": "http",
            },
        ],
        "features": {
            "context_awareness": True,
            "multi_language": False,
            "voice_support": True,
            "websocket_support": True,
            "real_time_processing": True,
        },
    }


@app.get("/api/dashboard/info")
async def get_dashboard_info():
    """Get dashboard information and metadata"""
    return {
        "system": {
            "name": "F.R.I.D.A.Y. Agent",
            "version": "1.0.0",
            "description": "AI-powered desktop assistant inspired by Tony Stark's F.R.I.D.A.Y.",
            "status": "operational",
        },
        "ai_model": {
            "name": "Gemini 2.5 Flash",
            "provider": "Google AI",
            "enabled": get_command_processor().use_ai if command_processor else False,
        },
        "modules": {
            "voice_recognition": voice_recognizer is not None,
            "text_to_speech": tts is not None,
            "app_launcher": app_launcher is not None,
            "command_processor": command_processor is not None,
        },
        "statistics": {
            "active_connections": len(manager.active_connections),
            "running_apps": (
                len(app_launcher.list_running_apps()) if app_launcher else 0
            ),
            "available_apps": (
                len(app_launcher.get_available_apps()) if app_launcher else 0
            ),
        },
    }


@app.post("/api/command")
async def execute_command(command: dict):
    """Execute a text command"""
    text = command.get("text", "")

    if not text:
        return JSONResponse(
            status_code=400, content={"error": "No command text provided"}
        )

    result = await get_command_processor().process_command(text)

    # Broadcast to all connected clients
    await manager.broadcast(
        {
            "type": "command_result",
            "command": text,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return result


@app.post("/api/apps/launch/{app_name}")
async def launch_app(app_name: str):
    """Launch an application"""
    result = app_launcher.launch_app(app_name)

    await manager.broadcast(
        {
            "type": "app_launched",
            "app": app_name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return result


@app.post("/api/apps/close/{app_name}")
async def close_app(app_name: str):
    """Close an application"""
    result = app_launcher.close_app(app_name)

    await manager.broadcast(
        {
            "type": "app_closed",
            "app": app_name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return result


@app.get("/api/apps/running")
async def get_running_apps():
    """Get list of running apps"""
    return {"apps": app_launcher.list_running_apps()}


@app.get("/api/apps/available")
async def get_available_apps():
    """Get list of available apps"""
    return {"apps": app_launcher.get_available_apps()}


@app.post("/api/voice/start")
async def start_voice():
    """Start voice recognition"""
    global voice_recognizer

    if voice_recognizer is None:

        def on_voice_command(text):
            # Process command
            result = asyncio.run(get_command_processor().process_command(text))

            # Broadcast to clients
            asyncio.create_task(
                manager.broadcast(
                    {
                        "type": "voice_command",
                        "command": text,
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

        voice_recognizer = VoiceRecognizer(callback=on_voice_command)

    voice_recognizer.start_listening()

    return {"success": True, "message": "Voice recognition started"}


@app.post("/api/voice/stop")
async def stop_voice():
    """Stop voice recognition"""
    global voice_recognizer

    if voice_recognizer:
        voice_recognizer.stop_listening()

    return {"success": True, "message": "Voice recognition stopped"}


# ============= SESSION MANAGEMENT ENDPOINTS =============


@app.get("/api/sessions")
async def get_sessions():
    """Get all chat sessions"""
    try:
        sessions = session_manager.get_all_sessions()
        return {"success": True, "sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.post("/api/sessions")
async def create_session(data: dict):
    """Create a new chat session"""
    try:
        name = data.get("name")
        session = session_manager.create_session(name)
        return {"success": True, "session": session}
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with messages"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Session not found"},
            )

        messages = session_manager.get_messages(session_id)
        session["messages"] = messages

        return {"success": True, "session": session}
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, data: dict):
    """Update session name"""
    try:
        name = data.get("name")
        if not name:
            return JSONResponse(
                status_code=400, content={"success": False, "error": "Name is required"}
            )

        success = session_manager.update_session_name(session_id, name)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        success = session_manager.delete_session(session_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.post("/api/sessions/{session_id}/messages")
async def add_message_to_session(session_id: str, data: dict):
    """Add a message to a session"""
    try:
        message_type = data.get("type", "user")
        content = data.get("content", "")
        metadata = data.get("metadata")

        message = session_manager.add_message(
            session_id, message_type, content, metadata
        )
        return {"success": True, "message": message}
    except Exception as e:
        logger.error(f"Error adding message to session {session_id}: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


# ============= FILE UPLOAD & ANALYSIS ENDPOINTS =============


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for analysis"""
    try:
        # Read file content
        content = await file.read()

        # Get file processor (lazy loaded)
        fp = get_file_processor()

        # Validate file
        validation = fp.validate_file(file.filename, len(content))
        if not validation["valid"]:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": validation["error"]},
            )

        # Save file
        file_path = await fp.save_file(file.filename, content)
        file_info = fp.get_file_info(file_path)

        return {
            "success": True,
            "file": {"path": file_path, "type": validation["type"], "info": file_info},
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.post("/api/analyze")
async def analyze_file(data: dict):
    """Analyze an uploaded file"""
    try:
        file_path = data.get("file_path")
        file_type = data.get("file_type")
        user_prompt = data.get("prompt")

        if not file_path or not file_type:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "file_path and file_type are required",
                },
            )

        # Get file processor (lazy loaded)
        fp = get_file_processor()

        # Process file
        result = await fp.process_file(file_path, file_type, user_prompt)

        return result
    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


# ============= EXTERNAL APIS ENDPOINTS =============


@app.get("/api/weather")
async def get_weather(city: str = "London"):
    """Get current weather for a city"""
    try:
        apis = get_external_apis()
        weather_data = await apis.get_weather(city)
        return {"success": True, "data": weather_data}
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/news")
async def get_news(category: str = "technology", country: str = "us"):
    """Get top news headlines"""
    try:
        apis = get_external_apis()
        news_data = await apis.get_news(category, country)
        return {"success": True, "data": news_data}
    except Exception as e:
        logger.error(f"News API error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/stocks/{symbol}")
async def get_stock(symbol: str):
    """Get stock data"""
    try:
        apis = get_external_apis()
        stock_data = await apis.get_stock_data(symbol)
        return {"success": True, "data": stock_data}
    except Exception as e:
        logger.error(f"Stock API error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/crypto/{symbol}")
async def get_crypto(symbol: str):
    """Get cryptocurrency data"""
    try:
        apis = get_external_apis()
        crypto_data = await apis.get_crypto_data(symbol)
        return {"success": True, "data": crypto_data}
    except Exception as e:
        logger.error(f"Crypto API error: {e}")
        return {"success": False, "error": str(e)}


# ============= TASK MANAGEMENT ENDPOINTS =============


@app.post("/api/tasks")
async def create_task(task_data: dict):
    """Create a new task"""
    try:
        tm = get_task_manager()
        task = tm.create_task(task_data)
        return {"success": True, "task": task}
    except Exception as e:
        logger.error(f"Task creation error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/tasks/parse")
async def parse_task(data: dict):
    """Parse natural language into task"""
    try:
        text = data.get("text", "")
        tm = get_task_manager()
        parsed = tm.parse_natural_language(text)
        return {"success": True, "parsed": parsed}
    except Exception as e:
        logger.error(f"Task parsing error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/tasks")
async def get_tasks(status: str = None, category: str = None):
    """Get all tasks with optional filtering"""
    try:
        tm = get_task_manager()
        tasks = tm.get_all_tasks(status=status, category=category)
        stats = tm.get_statistics()
        return {"success": True, "tasks": tasks, "stats": stats}
    except Exception as e:
        logger.error(f"Task retrieval error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task"""
    try:
        tm = get_task_manager()
        task = tm.get_task(task_id)
        if task:
            return {"success": True, "task": task}
        return {"success": False, "error": "Task not found"}
    except Exception as e:
        logger.error(f"Task retrieval error: {e}")
        return {"success": False, "error": str(e)}


@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, updates: dict):
    """Update a task"""
    try:
        tm = get_task_manager()
        task = tm.update_task(task_id, updates)
        if task:
            return {"success": True, "task": task}
        return {"success": False, "error": "Task not found"}
    except Exception as e:
        logger.error(f"Task update error: {e}")
        return {"success": False, "error": str(e)}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    try:
        tm = get_task_manager()
        success = tm.delete_task(task_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Task deletion error: {e}")
        return {"success": False, "error": str(e)}


# ============= GOOGLE INTEGRATION ENDPOINTS =============


@app.get("/api/google/auth-url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    try:
        gi = get_google_integration()
        url = gi.get_authorization_url()
        return {"success": True, "url": url}
    except Exception as e:
        logger.error(f"Google auth URL error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/google/authenticate")
async def authenticate_google(data: dict):
    """Authenticate with Google using OAuth code"""
    try:
        code = data.get("code")
        gi = get_google_integration()
        success = gi.authenticate(code)
        return {"success": success}
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/google/calendar/events")
async def get_calendar_events(max_results: int = 10):
    """Get upcoming calendar events"""
    try:
        gi = get_google_integration()
        events = gi.get_calendar_events(max_results)
        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"Calendar events error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/google/calendar/events")
async def create_calendar_event(data: dict):
    """Create a calendar event"""
    try:
        gi = get_google_integration()
        event = gi.create_calendar_event(
            summary=data.get("summary", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            description=data.get("description", ""),
            location=data.get("location", ""),
        )
        return {"success": True, "event": event}
    except Exception as e:
        logger.error(f"Create event error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/google/gmail/emails")
async def get_recent_emails(max_results: int = 10):
    """Get recent emails"""
    try:
        gi = get_google_integration()
        emails = gi.get_recent_emails(max_results)
        return {"success": True, "emails": emails}
    except Exception as e:
        logger.error(f"Get emails error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/google/gmail/draft")
async def create_email_draft(data: dict):
    """Create an email draft"""
    try:
        gi = get_google_integration()
        draft = gi.create_email_draft(
            to=data.get("to", ""),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
        )
        return {"success": True, "draft": draft}
    except Exception as e:
        logger.error(f"Create draft error: {e}")
        return {"success": False, "error": str(e)}


# ============= LOCAL LLM ENDPOINTS =============


@app.get("/api/local-llm/status")
async def get_local_llm_status():
    """Check if Ollama is available"""
    try:
        llm = get_local_llm()
        available = await llm.check_availability()
        hllm = get_hybrid_llm()
        status = hllm.get_status()
        setup = llm.get_setup_instructions()
        return {
            "success": True,
            "available": available,
            "status": status,
            "setup": setup,
        }
    except Exception as e:
        logger.error(f"Local LLM status error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/local-llm/models")
async def list_local_models():
    """List available local models"""
    try:
        models = await local_llm.list_models()
        return {"success": True, "models": models}
    except Exception as e:
        logger.error(f"List models error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/local-llm/mode")
async def set_llm_mode(data: dict):
    """Switch between cloud and local mode"""
    try:
        mode = data.get("mode", "hybrid")
        hllm = get_hybrid_llm()
        success = await hllm.set_mode(mode)
        return {"success": success, "mode": mode if success else hllm.mode}
    except Exception as e:
        logger.error(f"Set mode error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/local-llm/pull")
async def pull_local_model(data: dict):
    """Pull a model from Ollama registry"""
    try:
        model_name = data.get("model")
        success = await local_llm.pull_model(model_name)
        return {"success": success}
    except Exception as e:
        logger.error(f"Pull model error: {e}")
        return {"success": False, "error": str(e)}


# ============= NEW LOCAL LLM ENDPOINTS (Frontend Compatible) =============

@app.get("/api/local-llm/available-models")
async def get_available_models_v2():
    """Get processed models list for UI"""
    try:
        local_llm = get_local_llm()
        # Ensure we have latest installed status
        await local_llm.check_availability()
        
        models = local_llm.get_available_models()
        return {"success": True, "models": models}
    except Exception as e:
        logger.error(f"Get available models error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/local-llm/select-model")
async def select_local_model(data: dict):
    """Select active local model"""
    try:
        model_id = data.get("model_id")
        if not model_id:
            return JSONResponse(status_code=400, content={"error": "Model ID required"})
            
        local_llm = get_local_llm()
        success = local_llm.set_model(model_id)
        
        if success:
            return {"success": True, "model": local_llm.get_current_model()}
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid model ID"})
    except Exception as e:
        logger.error(f"Select model error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/llm/get-mode")
async def get_llm_mode():
    """Get current LLM mode (local/cloud/hybrid)"""
    try:
        # CommandProcessor holds the mode authority
        cp = get_command_processor()
        return {
            "success": True, 
            "mode": cp.mode,
            "using_hybrid": cp.hybrid_llm is not None
        }
    except Exception as e:
        logger.error(f"Get mode error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/llm/set-mode")
async def set_llm_mode_v2(data: dict):
    """Set LLM mode"""
    try:
        mode = data.get("mode") # local, cloud, hybrid
        if mode not in ['local', 'cloud', 'hybrid']:
            return JSONResponse(status_code=400, content={"error": "Invalid mode"})
            
        cp = get_command_processor()
        cp.mode = mode
        
        # If hybrid, also update hybrid manager
        if cp.hybrid_llm:
            await cp.hybrid_llm.set_mode(mode)
            
        return {"success": True, "mode": mode}
    except Exception as e:
        logger.error(f"Set mode error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= RAG DOCUMENT INTELLIGENCE ENDPOINTS =============


@app.post("/api/rag/upload-file")
async def rag_upload_file(file_path: str):
    """Upload a single file to RAG"""
    try:
        success = rag_engine.add_document(file_path)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/rag/upload-directory")
async def rag_upload_directory(data: dict):
    """Upload entire directory to RAG"""
    try:
        directory = data.get("directory")
        extensions = data.get("extensions")
        stats = rag_engine.add_directory(directory, extensions)
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/rag/query")
async def rag_query(data: dict):
    """Query RAG database"""
    try:
        query = data.get("query", "")
        n_results = data.get("n_results", 5)
        results = rag_engine.query(query, n_results)
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/rag/documents")
async def rag_list_documents():
    """List all indexed documents"""
    try:
        documents = rag_engine.list_documents()
        return {"success": True, "documents": documents}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/rag/document")
async def rag_delete_document(file_path: str):
    """Delete a document from RAG"""
    try:
        success = rag_engine.delete_document(file_path)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/rag/stats")
async def rag_get_stats():
    """Get RAG database statistics"""
    try:
        stats = rag_engine.get_stats()
        return stats
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============= INTEGRATED TERMINAL ENDPOINTS =============


@app.post("/api/terminal/create")
async def terminal_create_session(data: dict = None):
    """Create a new terminal session"""
    try:
        cwd = data.get("cwd") if data else None
        session_id = terminal_manager.create_session(cwd)
        return {"success": True, "session_id": session_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/terminal/execute")
async def terminal_execute(data: dict):
    """Execute a terminal command"""
    try:
        session_id = data.get("session_id")
        command = data.get("command")
        force = data.get("force", False)

        result = await terminal_manager.execute_command(
            session_id, command, force=force
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/terminal/history/{session_id}")
async def terminal_get_history(session_id: str, limit: int = 50):
    """Get command history"""
    try:
        history = terminal_manager.get_history(session_id, limit)
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/terminal/sessions")
async def terminal_list_sessions():
    """List all terminal sessions"""
    try:
        sessions = terminal_manager.list_sessions()
        return {"success": True, "sessions": sessions}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/terminal/cwd/{session_id}")
async def terminal_get_cwd(session_id: str):
    """Get current working directory"""
    try:
        cwd = terminal_manager.get_current_directory(session_id)
        return {"success": True, "cwd": cwd}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============= GIT INTEGRATION ENDPOINTS =============


@app.get("/api/git/status")
async def git_get_status():
    """Get git status"""
    try:
        status = git_manager.get_status()
        return status
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/git/diff")
async def git_get_diff(staged: bool = False):
    """Get git diff"""
    try:
        diff = git_manager.get_diff(staged)
        return {"success": True, "diff": diff}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/git/stage")
async def git_stage_files(data: dict):
    """Stage files for commit"""
    try:
        files = data.get("files")
        success = git_manager.stage_files(files)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/git/commit")
async def git_commit(data: dict):
    """Create a commit"""
    try:
        message = data.get("message")

        # Generate AI message if requested
        if message == "auto":
            diff = git_manager.get_diff(staged=True)
            message = git_manager.generate_commit_message(diff)

        commit_hash = git_manager.commit(message)
        return {
            "success": commit_hash is not None,
            "commit_hash": commit_hash,
            "message": message,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/git/push")
async def git_push(data: dict = None):
    """Push commits to remote"""
    try:
        remote = data.get("remote", "origin") if data else "origin"
        branch = data.get("branch") if data else None
        success = git_manager.push(remote, branch)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/git/pull")
async def git_pull(data: dict = None):
    """Pull changes from remote"""
    try:
        remote = data.get("remote", "origin") if data else "origin"
        branch = data.get("branch") if data else None
        success = git_manager.pull(remote, branch)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/git/log")
async def git_get_log(max_count: int = 10):
    """Get commit history"""
    try:
        log = git_manager.get_log(max_count)
        return {"success": True, "log": log}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/git/branches")
async def git_list_branches():
    """List all branches"""
    try:
        branches = git_manager.list_branches()
        return {"success": True, "branches": branches}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/git/branch")
async def git_create_branch(data: dict):
    """Create a new branch"""
    try:
        branch_name = data.get("branch_name")
        success = git_manager.create_branch(branch_name)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/git/checkout")
async def git_checkout(data: dict):
    """Checkout a branch"""
    try:
        branch_name = data.get("branch_name")
        success = git_manager.checkout_branch(branch_name)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============= DATABASE QUERY BUILDER ENDPOINTS =============


@app.post("/api/db/connect")
async def db_connect(data: dict):
    """Connect to a database"""
    try:
        connection_string = data.get("connection_string")
        db_name = data.get("db_name", "default")
        success = database_manager.connect(connection_string, db_name)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/db/schema")
async def db_get_schema(db_name: str = None):
    """Get database schema"""
    try:
        schema = database_manager.get_schema(db_name)
        return schema
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/db/query")
async def db_execute_query(data: dict):
    """Execute SQL query"""
    try:
        query = data.get("query")
        db_name = data.get("db_name")
        result = database_manager.execute_query(query, db_name)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/db/nl-query")
async def db_natural_language_query(data: dict):
    """Convert natural language to SQL and execute"""
    try:
        nl_query = data.get("query")
        db_name = data.get("db_name")

        # Get schema
        schema = database_manager.get_schema(db_name)

        # Convert to SQL
        sql_query = database_manager.natural_language_to_sql(nl_query, schema)

        # Execute if it's a valid query
        if not sql_query.startswith("--"):
            result = database_manager.execute_query(sql_query, db_name)
            return {"success": True, "sql": sql_query, "result": result}
        else:
            return {
                "success": False,
                "sql": sql_query,
                "message": "Could not generate SQL",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/db/preview/{table_name}")
async def db_table_preview(table_name: str, limit: int = 10):
    """Get table preview"""
    try:
        result = database_manager.get_table_preview(table_name, limit)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============= SCREENSHOT TO CODE ENDPOINTS =============


@app.post("/api/screenshot/analyze")
async def screenshot_analyze(file: UploadFile = File(...)):
    """Analyze screenshot"""
    try:
        # Save uploaded file temporarily
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = screenshot_to_code.analyze_screenshot(tmp_path)

        # Clean up
        import os

        os.unlink(tmp_path)

        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/screenshot/generate")
async def screenshot_generate_code(
    file: UploadFile = File(...), framework: str = Form("react")
):
    """Generate code from screenshot"""
    try:
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = screenshot_to_code.generate_react_code(tmp_path, framework)

        import os

        os.unlink(tmp_path)

        return result
    except Exception as e:
        return {"error": str(e)}


# ============= BROWSER AUTOMATION ENDPOINTS =============


@app.post("/api/browser/start")
async def browser_start(data: dict = None):
    """Start browser"""
    try:
        headless = data.get("headless", True) if data else True
        success = await browser_automation.start_browser(headless)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/browser/navigate")
async def browser_navigate(data: dict):
    """Navigate to URL"""
    try:
        url = data.get("url")
        result = await browser_automation.navigate(url)
        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/browser/test")
async def browser_run_test(data: dict):
    """Run automated test"""
    try:
        steps = data.get("steps", [])
        result = await browser_automation.run_test(steps)
        return result
    except Exception as e:
        return {"error": str(e)}


# ============= LEARNING PATH ENDPOINTS =============


@app.post("/api/learning/path")
async def learning_generate_path(data: dict):
    """Generate learning path"""
    try:
        topic = data.get("topic")
        current_level = data.get("current_level", "beginner")
        goal = data.get("goal", "advanced")

        path = learning_engine.generate_learning_path(topic, current_level, goal)
        return {"success": True, "path": path}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/learning/quiz")
async def learning_generate_quiz(data: dict):
    """Generate quiz"""
    try:
        topic = data.get("topic")
        level = data.get("level", "beginner")
        count = data.get("count", 5)

        quiz = learning_engine.generate_quiz(topic, level, count)
        return {"success": True, "quiz": quiz}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/learning/progress")
async def learning_track_progress(data: dict):
    """Track learning progress"""
    try:
        user_id = data.get("user_id", "default")
        topic = data.get("topic")
        module = data.get("module")
        completed = data.get("completed", True)

        progress = learning_engine.track_progress(user_id, topic, module, completed)
        return {"success": True, "progress": progress}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/learning/recommendations")
async def learning_get_recommendations(user_id: str = "default"):
    """Get personalized recommendations"""
    try:
        recommendations = learning_engine.get_recommendations(user_id)
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/execute-code")
async def execute_code(data: dict):
    """Execute code in different languages"""
    try:
        code = data.get("code", "")
        language = data.get("language", "python")

        import subprocess
        import tempfile
        import os

        # Security check - prevent dangerous operations
        dangerous_keywords = ['rm -rf', 'format', 'del /f', 'os.system', 'subprocess', 'eval(']
        if any(keyword in code.lower() for keyword in dangerous_keywords):
            return {"success": False, "error": "Security: Dangerous operation detected"}

        output = ""
        error = ""

        if language == "python":
            # Execute Python code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                result = subprocess.run(
                    ['python3', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout
                error = result.stderr
            finally:
                os.unlink(temp_file)

        elif language == "javascript":
            # Execute JavaScript with Node.js
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout
                error = result.stderr
            finally:
                os.unlink(temp_file)

        elif language == "cpp":
            # Compile and execute C++
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Compile
                compile_result = subprocess.run(
                    ['g++', temp_file, '-o', temp_file + '.out'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if compile_result.returncode == 0:
                    # Execute
                    run_result = subprocess.run(
                        [temp_file + '.out'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    output = run_result.stdout
                    error = run_result.stderr
                    os.unlink(temp_file + '.out')
                else:
                    error = compile_result.stderr
            finally:
                os.unlink(temp_file)

        else:
            return {"success": False, "error": f"Language '{language}' not supported yet"}

        if error:
            return {"success": False, "error": error, "output": output}
        else:
            return {"success": True, "output": output or "Code executed successfully (no output)"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timeout (5 seconds)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/terminal")
async def terminal_command(data: dict):
    """Execute terminal commands"""
    try:
        command = data.get("command", "")

        # Security check - prevent dangerous operations
        dangerous_cmds = ['rm -rf /', 'format', 'del /f', 'dd if=', 'mkfs', ':(){:|:&};:']
        if any(cmd in command.lower() for cmd in dangerous_cmds):
            return {"success": False, "error": "Security: Dangerous command detected"}

        # Execute command with timeout
        import subprocess
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout if result.stdout else result.stderr
        return {"success": True, "output": output or "Command executed"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timeout (10 seconds)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# QR Code Generator Endpoints
@app.post("/api/qr/generate")
async def generate_qr_code(data: dict):
    """Generate QR code"""
    try:
        from modules.qr_generator import QRCodeGenerator
        
        qr_gen = QRCodeGenerator()
        text = data.get("text", "")
        size = data.get("size", 10)
        border = data.get("border", 4)
        fill_color = data.get("fill_color", "black")
        back_color = data.get("back_color", "white")
        error_correction = data.get("error_correction", "M")
        style = data.get("style", "square")
        
        result = qr_gen.generate_qr_code(
            data=text,
            size=size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
            error_correction=error_correction,
            style=style
        )
        
        return result
    except ImportError:
        return {
            "success": False,
            "error": "QR code library not installed. Run: pip install qrcode[pil]"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/qr/wifi")
async def generate_wifi_qr(data: dict):
    """Generate WiFi QR code"""
    try:
        from modules.qr_generator import QRCodeGenerator
        
        qr_gen = QRCodeGenerator()
        ssid = data.get("ssid", "")
        password = data.get("password", "")
        security = data.get("security", "WPA")
        
        result = qr_gen.generate_wifi_qr(ssid, password, security)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/qr/vcard")
async def generate_vcard_qr(data: dict):
    """Generate vCard QR code"""
    try:
        from modules.qr_generator import QRCodeGenerator
        
        qr_gen = QRCodeGenerator()
        name = data.get("name", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        organization = data.get("organization", "")
        url = data.get("url", "")
        
        result = qr_gen.generate_vcard_qr(name, phone, email, organization, url)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============= AI Copilot Endpoints =============

def get_ai_copilot():
    """Lazy load AI Copilot"""
    global ai_copilot
    if ai_copilot is None:
        from modules.ai_copilot import AICopilot
        ai_copilot = AICopilot()
    return ai_copilot


@app.post("/api/copilot/completions")
async def get_code_completions(data: dict):
    """Get code completion suggestions (Enhanced with AI)"""
    try:
        copilot = get_ai_copilot()
        code = data.get("code", "")
        cursor_position = data.get("cursor_position", 0)
        language = data.get("language", "python")
        file_path = data.get("file_path", "")
        project_path = data.get("project_path", "")
        
        suggestions = copilot.get_completions(
            code, cursor_position, language, file_path, project_path
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Copilot completions error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/copilot/signature")
async def get_signature_help(data: dict):
    """Get function signature help"""
    try:
        copilot = get_ai_copilot()
        code = data.get("code", "")
        cursor_position = data.get("cursor_position", 0)
        language = data.get("language", "python")
        
        signature = copilot.get_signature_help(code, cursor_position, language)
        
        return {
            "success": True,
            "signature": signature
        }
    except Exception as e:
        logger.error(f"Signature help error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/copilot/context")
async def get_context_suggestions(data: dict):
    """Get context-aware suggestions"""
    try:
        copilot = get_ai_copilot()
        code = data.get("code", "")
        file_path = data.get("file_path", "")
        language = data.get("language", "python")
        
        suggestions = copilot.get_context_suggestions(code, file_path, language)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Context suggestions error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/copilot/detect-errors")
async def detect_code_errors(data: dict):
    """Detect potential errors and code quality issues"""
    try:
        copilot = get_ai_copilot()
        code = data.get("code", "")
        language = data.get("language", "python")
        
        issues = copilot.detect_errors(code, language)
        
        return {
            "success": True,
            "issues": issues,
            "count": len(issues)
        }
    except Exception as e:
        logger.error(f"Error detection failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/copilot/improvements")
async def get_code_improvements(data: dict):
    """Get AI-powered code improvement suggestions"""
    try:
        copilot = get_ai_copilot()
        code = data.get("code", "")
        language = data.get("language", "python")
        
        improvements = copilot.get_code_improvements(code, language)
        
        return {
            "success": True,
            "improvements": improvements,
            "count": len(improvements)
        }
    except Exception as e:
        logger.error(f"Code improvements failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/copilot/explain")
async def explain_code(data: dict):
    """Explain what a code snippet does using AI"""
    try:
        copilot = get_ai_copilot()
        code = data.get("code", "")
        language = data.get("language", "python")
        
        explanation = copilot.explain_code(code, language)
        
        return {
            "success": True,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= Integrated Debugger Endpoints =============

def get_integrated_debugger():
    """Lazy load Integrated Debugger"""
    global integrated_debugger
    if integrated_debugger is None:
        from modules.integrated_debugger import IntegratedDebugger
        integrated_debugger = IntegratedDebugger()
    return integrated_debugger


@app.post("/api/debugger/session")
async def create_debug_session(data: dict):
    """Create a new debug session"""
    try:
        debugger = get_integrated_debugger()
        file_path = data.get("file_path")
        
        if not file_path:
            return JSONResponse(status_code=400, content={"error": "file_path is required"})
        
        session_id = debugger.create_session(file_path)
        session = debugger.get_session(session_id)
        
        return {
            "success": True,
            "session": session.to_dict() if session else None
        }
    except Exception as e:
        logger.error(f"Create debug session error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/debugger/sessions")
async def list_debug_sessions():
    """List all debug sessions"""
    try:
        debugger = get_integrated_debugger()
        sessions = debugger.list_sessions()
        
        return {
            "success": True,
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/debugger/{session_id}/breakpoint")
async def add_breakpoint(session_id: str, data: dict):
    """Add a breakpoint"""
    try:
        debugger = get_integrated_debugger()
        line_number = data.get("line_number")
        condition = data.get("condition")
        
        success = debugger.add_breakpoint(session_id, line_number, condition)
        
        return {
            "success": success,
            "session_id": session_id,
            "line_number": line_number
        }
    except Exception as e:
        logger.error(f"Add breakpoint error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/api/debugger/{session_id}/breakpoint/{line_number}")
async def remove_breakpoint(session_id: str, line_number: int):
    """Remove a breakpoint"""
    try:
        debugger = get_integrated_debugger()
        success = debugger.remove_breakpoint(session_id, line_number)
        
        return {"success": success}
    except Exception as e:
        logger.error(f"Remove breakpoint error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/debugger/{session_id}/start")
async def start_debugging(session_id: str):
    """Start debugging"""
    try:
        debugger = get_integrated_debugger()
        result = debugger.start_debugging(session_id)
        
        return result
    except Exception as e:
        logger.error(f"Start debugging error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/debugger/{session_id}/step-over")
async def step_over(session_id: str):
    """Step over current line"""
    try:
        debugger = get_integrated_debugger()
        result = debugger.step_over(session_id)
        
        return result
    except Exception as e:
        logger.error(f"Step over error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/debugger/{session_id}/step-into")
async def step_into(session_id: str):
    """Step into function"""
    try:
        debugger = get_integrated_debugger()
        result = debugger.step_into(session_id)
        
        return result
    except Exception as e:
        logger.error(f"Step into error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/debugger/{session_id}/continue")
async def continue_execution(session_id: str):
    """Continue execution"""
    try:
        debugger = get_integrated_debugger()
        result = debugger.continue_execution(session_id)
        
        return result
    except Exception as e:
        logger.error(f"Continue error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/debugger/{session_id}/variables")
async def get_variables(session_id: str, scope: str = "local"):
    """Get variables in current scope"""
    try:
        debugger = get_integrated_debugger()
        result = debugger.get_variables(session_id, scope)
        
        return result
    except Exception as e:
        logger.error(f"Get variables error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/debugger/{session_id}/evaluate")
async def evaluate_expression(session_id: str, data: dict):
    """Evaluate expression in debug context"""
    try:
        debugger = get_integrated_debugger()
        expression = data.get("expression", "")
        result = debugger.evaluate_expression(session_id, expression)
        
        return result
    except Exception as e:
        logger.error(f"Evaluate error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= Code Snippets Endpoints =============

def get_code_snippets():
    """Lazy load Code Snippets Library"""
    global code_snippets
    if code_snippets is None:
        from modules.code_snippets_library import CodeSnippetsLibrary
        code_snippets = CodeSnippetsLibrary()
    return code_snippets


@app.get("/api/snippets/templates")
async def get_snippet_templates(language: str = None):
    """Get snippet templates"""
    try:
        snippets = get_code_snippets()
        templates = snippets.list_templates(language)
        
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/snippets/languages")
async def get_snippet_languages():
    """Get supported languages"""
    try:
        snippets = get_code_snippets()
        languages = snippets.get_languages()
        
        return {
            "success": True,
            "languages": languages
        }
    except Exception as e:
        logger.error(f"Get languages error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/snippets/template/{language}/{template_name}")
async def get_specific_template(language: str, template_name: str):
    """Get a specific template"""
    try:
        snippets = get_code_snippets()
        template = snippets.get_template(language, template_name)
        
        if template:
            return {
                "success": True,
                "template": template
            }
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Template not found"}
            )
    except Exception as e:
        logger.error(f"Get template error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============================================================================
# OPENROUTER API ENDPOINTS
# ============================================================================

openrouter_api = None

def get_openrouter():
    """Lazy-load OpenRouter integration"""
    global openrouter_api
    if openrouter_api is None:
        from modules.openrouter_integration import OpenRouterAPI
        openrouter_api = OpenRouterAPI()
    return openrouter_api


@app.post("/api/openrouter/chat")
async def openrouter_chat(request: dict):
    """
    Send a chat request to OpenRouter
    
    Request body:
    {
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "meta-llama/llama-3.2-90b-vision-instruct:free",  # optional
        "temperature": 0.7,  # optional
        "max_tokens": 1000   # optional
    }
    """
    try:
        api = get_openrouter()
        messages = request.get("messages", [])
        model = request.get("model")
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 1000)
        
        if not messages:
            return JSONResponse(
                status_code=400,
                content={"error": "messages field is required"}
            )
        
        response = api.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if response.get("error"):
            return JSONResponse(
                status_code=500,
                content={"error": response["error"], "success": False}
            )
        
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        logger.error(f"OpenRouter chat error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/openrouter/query")
async def openrouter_simple_query(request: dict):
    """
    Simple text query to OpenRouter
    
    Request body:
    {
        "prompt": "What is Python?",
        "model": "meta-llama/llama-3.2-90b-vision-instruct:free"  # optional
    }
    """
    try:
        api = get_openrouter()
        prompt = request.get("prompt", "")
        model = request.get("model")
        
        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"error": "prompt field is required"}
            )
        
        response_text = api.simple_query(prompt, model=model)
        
        return {
            "success": True,
            "response": response_text
        }
    except Exception as e:
        logger.error(f"OpenRouter query error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.get("/api/openrouter/models")
async def get_openrouter_models():
    """Get list of available OpenRouter models"""
    try:
        api = get_openrouter()
        models = api.get_available_models()
        
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Get OpenRouter models error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.get("/api/openrouter/models/free")


# ==================== NEW ADVANCED FEATURES API ====================

# ==================== Collaborative Features ====================

@app.post("/api/collab/session/create")
async def create_collab_session(request: dict):
    """Create a new collaborative coding session"""
    try:
        collab = get_collaborative_features()
        result = await collab.create_session(
            name=request.get("name", ""),
            owner_id=request.get("owner_id", ""),
            settings=request.get("settings")
        )
        return result
    except Exception as e:
        logger.error(f"Error creating collaborative session: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/collab/session/join")
async def join_collab_session(request: dict):
    """Join an existing collaborative session"""
    try:
        collab = get_collaborative_features()
        result = await collab.join_session(
            session_id=request.get("session_id", ""),
            user_id=request.get("user_id", ""),
            user_name=request.get("user_name", ""),
            role=request.get("role", "viewer")
        )
        return result
    except Exception as e:
        logger.error(f"Error joining collaborative session: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/collab/code/change")
async def apply_code_change(request: dict):
    """Apply a code change in real-time collaboration"""
    try:
        collab = get_collaborative_features()
        result = await collab.apply_code_change(
            session_id=request.get("session_id", ""),
            user_id=request.get("user_id", ""),
            user_name=request.get("user_name", ""),
            change_data=request.get("change_data", {})
        )
        return result
    except Exception as e:
        logger.error(f"Error applying code change: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/collab/review/create")
async def create_code_review(request: dict):
    """Create a code review assignment"""
    try:
        collab = get_collaborative_features()
        result = await collab.create_code_review(
            title=request.get("title", ""),
            description=request.get("description", ""),
            file_paths=request.get("file_paths", []),
            assignee_id=request.get("assignee_id", ""),
            reviewer_id=request.get("reviewer_id", ""),
            ai_analysis=request.get("ai_analysis", True)
        )
        return result
    except Exception as e:
        logger.error(f"Error creating code review: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/collab/review/comment")
async def add_review_comment(request: dict):
    """Add a comment to code review"""
    try:
        collab = get_collaborative_features()
        result = await collab.add_review_comment(
            review_id=request.get("review_id", ""),
            user_id=request.get("user_id", ""),
            user_name=request.get("user_name", ""),
            file_path=request.get("file_path", ""),
            line_number=request.get("line_number", 0),
            comment=request.get("comment", ""),
            suggestion=request.get("suggestion")
        )
        return result
    except Exception as e:
        logger.error(f"Error adding review comment: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/collab/snippet/create")
async def create_team_snippet(request: dict):
    """Create a shared code snippet"""
    try:
        collab = get_collaborative_features()
        result = await collab.create_team_snippet(
            title=request.get("title", ""),
            description=request.get("description", ""),
            code=request.get("code", ""),
            language=request.get("language", "python"),
            tags=request.get("tags", []),
            author_id=request.get("author_id", "")
        )
        return result
    except Exception as e:
        logger.error(f"Error creating team snippet: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/collab/snippet/search")
async def search_team_snippets(request: dict):
    """Search team knowledge base"""
    try:
        collab = get_collaborative_features()
        result = await collab.search_team_snippets(
            query=request.get("query", ""),
            tags=request.get("tags"),
            language=request.get("language")
        )
        return result
    except Exception as e:
        logger.error(f"Error searching team snippets: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


# ==================== AI Pair Programmer ====================

@app.post("/api/pair-programmer/suggestions")
async def get_live_suggestions(request: dict):
    """Get live code suggestions as user types"""
    try:
        pair_prog = get_ai_pair_programmer()
        result = await pair_prog.get_live_suggestions(
            code_context=request.get("code_context", {}),
            trigger_type=request.get("trigger_type", "typing")
        )
        return result
    except Exception as e:
        logger.error(f"Error getting live suggestions: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/pair-programmer/next-steps")
async def suggest_next_steps(request: dict):
    """Suggest next logical steps in implementation"""
    try:
        pair_prog = get_ai_pair_programmer()
        result = await pair_prog.suggest_next_steps(
            context=request.get("context", {})
        )
        return result
    except Exception as e:
        logger.error(f"Error suggesting next steps: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/pair-programmer/feedback")
async def learn_from_feedback(request: dict):
    """Learn from user feedback on suggestions"""
    try:
        pair_prog = get_ai_pair_programmer()
        result = await pair_prog.learn_from_feedback(
            suggestion_id=request.get("suggestion_id", ""),
            accepted=request.get("accepted", False),
            user_id=request.get("user_id", "")
        )
        return result
    except Exception as e:
        logger.error(f"Error learning from feedback: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/pair-programmer/index-codebase")
async def index_codebase(request: dict):
    """Index codebase for context-aware suggestions"""
    try:
        pair_prog = get_ai_pair_programmer()
        result = await pair_prog.index_codebase(
            project_path=request.get("project_path", "")
        )
        return result
    except Exception as e:
        logger.error(f"Error indexing codebase: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


# ==================== Visual Programming ====================

@app.post("/api/visual/workflow/create")
async def create_visual_workflow(request: dict):
    """Create a new visual workflow"""
    try:
        visual_prog = get_visual_programming()
        result = await visual_prog.create_workflow(
            name=request.get("name", ""),
            description=request.get("description", ""),
            template=request.get("template")
        )
        return result
    except Exception as e:
        logger.error(f"Error creating visual workflow: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/visual/workflow/add-node")
async def add_workflow_node(request: dict):
    """Add a node to visual workflow"""
    try:
        visual_prog = get_visual_programming()
        result = await visual_prog.add_node(
            workflow_id=request.get("workflow_id", ""),
            node_type=request.get("node_type", ""),
            label=request.get("label", ""),
            position=request.get("position", {}),
            config=request.get("config")
        )
        return result
    except Exception as e:
        logger.error(f"Error adding workflow node: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/visual/workflow/generate-code")
async def generate_code_from_workflow(request: dict):
    """Generate code from visual workflow"""
    try:
        visual_prog = get_visual_programming()
        result = await visual_prog.generate_code(
            workflow_id=request.get("workflow_id", ""),
            language=request.get("language", "python"),
            framework=request.get("framework")
        )
        return result
    except Exception as e:
        logger.error(f"Error generating code from workflow: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.get("/api/visual/templates")
async def get_workflow_templates():
    """Get available workflow templates"""
    try:
        visual_prog = get_visual_programming()
        result = await visual_prog.get_templates()
        return result
    except Exception as e:
        logger.error(f"Error getting workflow templates: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/visual/api/design")
async def design_api_endpoint(request: dict):
    """Design a visual API endpoint"""
    try:
        visual_prog = get_visual_programming()
        result = await visual_prog.design_api_endpoint(
            endpoint_name=request.get("endpoint_name", ""),
            method=request.get("method", "GET"),
            path=request.get("path", ""),
            workflow_id=request.get("workflow_id")
        )
        return result
    except Exception as e:
        logger.error(f"Error designing API endpoint: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


# ==================== Code Search & Navigation ====================

@app.post("/api/code-search/index")
async def index_codebase_for_search(request: dict):
    """Index codebase for fast searching"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.index_codebase(
            project_path=request.get("project_path", ""),
            file_extensions=request.get("file_extensions"),
            exclude_dirs=request.get("exclude_dirs")
        )
        return result
    except Exception as e:
        logger.error(f"Error indexing codebase: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/code-search/semantic")
async def semantic_code_search(request: dict):
    """Perform semantic search across codebase"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.semantic_search(
            query=request.get("query", ""),
            project_path=request.get("project_path"),
            max_results=request.get("max_results", 20)
        )
        return result
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/code-search/similar-patterns")
async def find_similar_code_patterns(request: dict):
    """Find similar code patterns in codebase"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.find_similar_patterns(
            code_snippet=request.get("code_snippet", ""),
            language=request.get("language", "python"),
            threshold=request.get("threshold", 0.7)
        )
        return result
    except Exception as e:
        logger.error(f"Error finding similar patterns: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/code-search/dependencies")
async def analyze_symbol_dependencies(request: dict):
    """Analyze dependencies for a symbol"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.analyze_dependencies(
            symbol_name=request.get("symbol_name", ""),
            file_path=request.get("file_path")
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing dependencies: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/code-search/impact-analysis")
async def perform_impact_analysis(request: dict):
    """Analyze impact of changing a symbol"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.impact_analysis(
            symbol_name=request.get("symbol_name", ""),
            file_path=request.get("file_path")
        )
        return result
    except Exception as e:
        logger.error(f"Error in impact analysis: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/code-search/dead-code")
async def detect_dead_code(request: dict):
    """Detect unused functions and classes"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.detect_dead_code(
            project_path=request.get("project_path", "")
        )
        return result
    except Exception as e:
        logger.error(f"Error detecting dead code: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/code-search/find-definition")
async def find_symbol_definition(request: dict):
    """Find definition of a symbol"""
    try:
        code_search = get_code_search_navigation()
        result = await code_search.find_definition(
            symbol_name=request.get("symbol_name", "")
        )
        return result
    except Exception as e:
        logger.error(f"Error finding definition: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


# ==================== Smart Testing Suite ====================

@app.post("/api/testing/generate-tests")
async def generate_unit_tests(request: dict):
    """Auto-generate unit tests for code"""
    try:
        testing = get_smart_testing_suite()
        result = await testing.generate_unit_tests(
            file_path=request.get("file_path", ""),
            function_name=request.get("function_name"),
            framework=request.get("framework", "pytest")
        )
        return result
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/testing/run-tests")
async def run_generated_tests(request: dict):
    """Run generated tests"""
    try:
        testing = get_smart_testing_suite()
        result = await testing.run_tests(
            test_file_path=request.get("test_file_path", ""),
            framework=request.get("framework", "pytest")
        )
        return result
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/testing/mutation-testing")
async def perform_mutation_testing(request: dict):
    """Perform mutation testing to assess test quality"""
    try:
        testing = get_smart_testing_suite()
        result = await testing.perform_mutation_testing(
            file_path=request.get("file_path", ""),
            test_command=request.get("test_command", "pytest")
        )
        return result
    except Exception as e:
        logger.error(f"Error in mutation testing: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/testing/benchmark")
async def benchmark_function_performance(request: dict):
    """Benchmark function performance"""
    try:
        testing = get_smart_testing_suite()
        result = await testing.benchmark_function(
            file_path=request.get("file_path", ""),
            function_name=request.get("function_name", ""),
            iterations=request.get("iterations", 1000),
            compare_to_baseline=request.get("compare_to_baseline", False)
        )
        return result
    except Exception as e:
        logger.error(f"Error benchmarking function: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/testing/visual-regression")
async def perform_visual_regression_test(request: dict):
    """Perform visual regression testing"""
    try:
        testing = get_smart_testing_suite()
        result = await testing.visual_regression_test(
            url=request.get("url", ""),
            screenshot_path=request.get("screenshot_path", ""),
            baseline_path=request.get("baseline_path")
        )
        return result
    except Exception as e:
        logger.error(f"Error in visual regression test: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.post("/api/testing/api-mock")
async def generate_api_mock(request: dict):
    """Generate API mocks from OpenAPI spec"""
    try:
        testing = get_smart_testing_suite()
        result = await testing.generate_api_mock(
            openapi_spec=request.get("openapi_spec", {})
        )
        return result
    except Exception as e:
        logger.error(f"Error generating API mock: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.get("/api/openrouter/models/free")
async def get_free_openrouter_models():
    """Get list of free OpenRouter models"""
    try:
        api = get_openrouter()
        models = api.get_free_models()
        
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Get free models error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)

    try:
        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to Friday Agent",
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "command":
                # Process command
                text = message.get("text", "")
                result = await get_command_processor().process_command(text)

                # Send result back
                await websocket.send_json(
                    {
                        "type": "command_result",
                        "command": text,
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            elif message.get("type") == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """Run startup checks"""
    logger.info("Running startup checks...")

    # Check Ollama availability
    try:
        llm = get_local_llm()
        available = await llm.check_availability()
        if available:
            logger.info(f"✅ Ollama is running with {len(llm.installed_models)} models available")
            for model in llm.installed_models:
                logger.info(f"   - {model}")
        else:
            logger.warning("⚠️  Ollama is not running or no models are installed")
            logger.info("   To use local LLM mode:")
            logger.info("   1. Start Ollama: ollama serve")
            logger.info("   2. Pull a model: ollama pull qwen2.5-coder:7b")
    except Exception as e:
        logger.warning(f"⚠️  Could not check Ollama status: {e}")

    logger.info("Friday Agent API ready!")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Friday Agent API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
