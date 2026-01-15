"""
Helper functions for Project Management and Chat History features
"""

from typing import Dict, List, Optional, Any
from modules.project_manager import ProjectManager
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize project manager
project_manager = ProjectManager()


# ============= PROJECT HELPER FUNCTIONS =============

def validate_project_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate project creation/update data

    Args:
        data: Dictionary containing project data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data.get("name") or not data.get("name").strip():
        return False, "Project name is required"

    if len(data.get("name", "")) > 255:
        return False, "Project name must be less than 255 characters"

    return True, ""


def create_project_safe(name: str, description: str = "", user_id: int = None, metadata: dict = None) -> Dict:
    """
    Safely create a project with validation

    Args:
        name: Project name
        description: Project description
        user_id: User ID
        metadata: Additional metadata

    Returns:
        Dictionary with success status and project data or error
    """
    try:
        # Validate inputs
        if not name or not name.strip():
            return {
                "success": False,
                "error": "Project name is required"
            }

        # Create project
        result = project_manager.create_project(name.strip(), description, user_id, metadata)

        if result.get("success"):
            logger.info(f"Project created: {name} (ID: {result['project']['id']})")
        else:
            logger.error(f"Failed to create project: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        return {
            "success": False,
            "error": f"Internal error: {str(e)}"
        }


def get_user_projects(user_id: int) -> List[Dict]:
    """
    Get all projects for a specific user

    Args:
        user_id: User ID

    Returns:
        List of project dictionaries
    """
    try:
        projects = project_manager.get_projects(user_id)
        logger.info(f"Retrieved {len(projects)} projects for user {user_id}")
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return []


def update_project_safe(project_id: int, name: str = None, description: str = None, metadata: dict = None) -> tuple[bool, str]:
    """
    Safely update a project

    Args:
        project_id: Project ID
        name: New project name (optional)
        description: New description (optional)
        metadata: New metadata (optional)

    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if project exists
        project = project_manager.get_project(project_id)
        if not project:
            return False, "Project not found"

        # Validate name if provided
        if name is not None and (not name.strip() or len(name) > 255):
            return False, "Invalid project name"

        # Update project
        success = project_manager.update_project(project_id, name, description, metadata)

        if success:
            logger.info(f"Project updated: {project_id}")
            return True, "Project updated successfully"
        else:
            return False, "Failed to update project"

    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        return False, f"Internal error: {str(e)}"


def delete_project_safe(project_id: int) -> tuple[bool, str]:
    """
    Safely delete a project

    Args:
        project_id: Project ID

    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if project exists
        project = project_manager.get_project(project_id)
        if not project:
            return False, "Project not found"

        # Delete project
        success = project_manager.delete_project(project_id)

        if success:
            logger.info(f"Project deleted: {project_id}")
            return True, "Project deleted successfully"
        else:
            return False, "Failed to delete project"

    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        return False, f"Internal error: {str(e)}"


# ============= CHAT HISTORY HELPER FUNCTIONS =============

def validate_chat_message(message: str) -> tuple[bool, str]:
    """
    Validate chat message data

    Args:
        message: Message text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Message is required"

    if len(message) > 10000:
        return False, "Message is too long (max 10000 characters)"

    return True, ""


def save_chat_message(message: str, response: str = None, user_id: int = None, project_id: int = None) -> tuple[bool, str]:
    """
    Safely save a chat message

    Args:
        message: User message
        response: AI response
        user_id: User ID
        project_id: Project ID (optional)

    Returns:
        Tuple of (success, message)
    """
    try:
        # Validate message
        is_valid, error = validate_chat_message(message)
        if not is_valid:
            return False, error

        # Save message
        success = project_manager.add_chat_message(message, response, project_id, user_id)

        if success:
            logger.info(f"Chat message saved for user {user_id}")
            return True, "Chat message saved successfully"
        else:
            return False, "Failed to save chat message"

    except Exception as e:
        logger.error(f"Error saving chat message: {str(e)}")
        return False, f"Internal error: {str(e)}"


def get_user_chat_history(user_id: int, project_id: int = None, limit: int = 100) -> List[Dict]:
    """
    Get chat history for a user

    Args:
        user_id: User ID
        project_id: Project ID (optional)
        limit: Maximum number of messages

    Returns:
        List of chat message dictionaries
    """
    try:
        history = project_manager.get_chat_history(project_id, user_id, limit)
        logger.info(f"Retrieved {len(history)} chat messages for user {user_id}")
        return history
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return []


def search_user_chat_history(query: str, user_id: int = None, limit: int = 50) -> tuple[List[Dict], str]:
    """
    Search chat history

    Args:
        query: Search query
        user_id: User ID (optional)
        limit: Maximum number of results

    Returns:
        Tuple of (results list, error message)
    """
    try:
        if not query or not query.strip():
            return [], "Search query is required"

        results = project_manager.search_chat_history(query, user_id, limit)
        logger.info(f"Search found {len(results)} results for query: {query}")
        return results, ""

    except Exception as e:
        logger.error(f"Error searching chat history: {str(e)}")
        return [], f"Internal error: {str(e)}"


# ============= UTILITY FUNCTIONS =============

def format_error_response(status_code: int, error_message: str) -> JSONResponse:
    """
    Format a standardized error response

    Args:
        status_code: HTTP status code
        error_message: Error message

    Returns:
        JSONResponse object
    """
    return JSONResponse(
        status_code=status_code,
        content={"error": error_message}
    )


def format_success_response(data: Any, message: str = None) -> Dict:
    """
    Format a standardized success response

    Args:
        data: Response data
        message: Optional success message

    Returns:
        Dictionary with response data
    """
    response = {"success": True}

    if message:
        response["message"] = message

    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data

    return response


def get_project_stats(user_id: int) -> Dict:
    """
    Get statistics about user's projects

    Args:
        user_id: User ID

    Returns:
        Dictionary with project statistics
    """
    try:
        projects = project_manager.get_projects(user_id)
        chat_history = project_manager.get_chat_history(user_id=user_id, limit=1000)

        stats = {
            "total_projects": len(projects),
            "total_messages": len(chat_history),
            "projects_with_chats": len(set(msg.get("project_id") for msg in chat_history if msg.get("project_id"))),
        }

        if projects:
            stats["latest_project"] = projects[0].get("name")

        return stats

    except Exception as e:
        logger.error(f"Error getting project stats: {str(e)}")
        return {
            "total_projects": 0,
            "total_messages": 0,
            "projects_with_chats": 0,
        }


def cleanup_orphaned_chats(user_id: int = None) -> int:
    """
    Clean up chat messages that reference deleted projects

    Args:
        user_id: User ID (optional)

    Returns:
        Number of orphaned messages found
    """
    try:
        # Get all chat messages
        chat_history = project_manager.get_chat_history(user_id=user_id, limit=10000)

        orphaned_count = 0
        for msg in chat_history:
            if msg.get("project_id"):
                project = project_manager.get_project(msg["project_id"])
                if not project:
                    orphaned_count += 1

        logger.info(f"Found {orphaned_count} orphaned chat messages")
        return orphaned_count

    except Exception as e:
        logger.error(f"Error checking orphaned chats: {str(e)}")
        return 0
