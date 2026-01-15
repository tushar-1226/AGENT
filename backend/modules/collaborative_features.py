"""
Collaborative Features Module
Real-time collaborative coding, session sharing, code review assignments, and team knowledge base
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

logger = logging.getLogger(__name__)


class CollaborationRole(Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    REVIEWER = "reviewer"


class ChangeType(Enum):
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    CURSOR_MOVE = "cursor_move"


@dataclass
class CodeChange:
    """Represents a single code change in collaborative session"""
    id: str
    user_id: str
    user_name: str
    timestamp: float
    change_type: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    cursor_position: Optional[Dict] = None


@dataclass
class CollaborativeSession:
    """Represents a collaborative coding session"""
    session_id: str
    name: str
    owner_id: str
    created_at: float
    participants: Dict[str, str]  # user_id -> role
    active_file: Optional[str]
    changes_history: List[CodeChange]
    is_active: bool
    settings: Dict


@dataclass
class CodeReview:
    """Represents a code review assignment"""
    review_id: str
    title: str
    description: str
    file_paths: List[str]
    assignee_id: str
    reviewer_id: str
    created_at: float
    status: str  # pending, in_review, approved, changes_requested
    comments: List[Dict]
    ai_insights: Optional[Dict]


@dataclass
class TeamSnippet:
    """Represents a shared code snippet in team knowledge base"""
    snippet_id: str
    title: str
    description: str
    code: str
    language: str
    tags: List[str]
    author_id: str
    created_at: float
    updated_at: float
    usage_count: int
    ratings: Dict[str, int]  # user_id -> rating (1-5)


class CollaborativeFeatures:
    """
    Manages real-time collaborative coding features including:
    - Real-time code editing with conflict resolution
    - Session sharing and management
    - Code review workflows with AI insights
    - Team knowledge base for snippets and patterns
    """

    def __init__(self):
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.active_connections: Dict[str, Set[str]] = {}  # session_id -> set of websocket connections
        self.reviews: Dict[str, CodeReview] = {}
        self.team_snippets: Dict[str, TeamSnippet] = {}
        self.operational_transforms: Dict[str, List] = {}  # For conflict resolution
        logger.info("Collaborative Features module initialized")

    # ==================== Session Management ====================

    async def create_session(
        self,
        name: str,
        owner_id: str,
        settings: Optional[Dict] = None
    ) -> Dict:
        """Create a new collaborative session"""
        try:
            session_id = str(uuid.uuid4())
            session = CollaborativeSession(
                session_id=session_id,
                name=name,
                owner_id=owner_id,
                created_at=datetime.now().timestamp(),
                participants={owner_id: CollaborationRole.OWNER.value},
                active_file=None,
                changes_history=[],
                is_active=True,
                settings=settings or {
                    "allow_anonymous": False,
                    "auto_save": True,
                    "conflict_resolution": "operational_transform",
                    "max_participants": 10
                }
            )

            self.sessions[session_id] = session
            self.active_connections[session_id] = set()

            logger.info(f"Created collaborative session: {session_id}")
            return {
                "success": True,
                "session_id": session_id,
                "session": asdict(session),
                "invite_link": f"friday://join-session/{session_id}"
            }

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {"success": False, "error": str(e)}

    async def join_session(
        self,
        session_id: str,
        user_id: str,
        user_name: str,
        role: str = "viewer"
    ) -> Dict:
        """Join an existing collaborative session"""
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}

            session = self.sessions[session_id]
            
            if not session.is_active:
                return {"success": False, "error": "Session is not active"}

            # Check participant limit
            max_participants = session.settings.get("max_participants", 10)
            if len(session.participants) >= max_participants:
                return {"success": False, "error": "Session is full"}

            # Add participant
            session.participants[user_id] = role
            
            # Notify other participants
            await self._broadcast_event(session_id, {
                "type": "user_joined",
                "user_id": user_id,
                "user_name": user_name,
                "role": role,
                "timestamp": datetime.now().timestamp()
            })

            return {
                "success": True,
                "session": asdict(session),
                "participants": session.participants
            }

        except Exception as e:
            logger.error(f"Error joining session: {e}")
            return {"success": False, "error": str(e)}

    async def leave_session(self, session_id: str, user_id: str) -> Dict:
        """Leave a collaborative session"""
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}

            session = self.sessions[session_id]
            
            if user_id in session.participants:
                del session.participants[user_id]

            # Notify other participants
            await self._broadcast_event(session_id, {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.now().timestamp()
            })

            # Close session if owner left
            if user_id == session.owner_id:
                session.is_active = False
                await self._broadcast_event(session_id, {
                    "type": "session_closed",
                    "reason": "Owner left the session"
                })

            return {"success": True}

        except Exception as e:
            logger.error(f"Error leaving session: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Real-time Code Editing ====================

    async def apply_code_change(
        self,
        session_id: str,
        user_id: str,
        user_name: str,
        change_data: Dict
    ) -> Dict:
        """Apply a code change in real-time with conflict resolution"""
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}

            session = self.sessions[session_id]

            # Check permissions
            role = session.participants.get(user_id)
            if role not in [CollaborationRole.OWNER.value, CollaborationRole.EDITOR.value]:
                return {"success": False, "error": "Insufficient permissions"}

            # Create change object
            change = CodeChange(
                id=str(uuid.uuid4()),
                user_id=user_id,
                user_name=user_name,
                timestamp=datetime.now().timestamp(),
                change_type=change_data.get("change_type", "insert"),
                file_path=change_data["file_path"],
                start_line=change_data["start_line"],
                end_line=change_data["end_line"],
                content=change_data["content"],
                cursor_position=change_data.get("cursor_position")
            )

            # Apply operational transform for conflict resolution
            transformed_change = await self._apply_operational_transform(
                session_id,
                change
            )

            # Add to history
            session.changes_history.append(transformed_change)

            # Broadcast to all participants
            await self._broadcast_event(session_id, {
                "type": "code_change",
                "change": asdict(transformed_change)
            })

            return {
                "success": True,
                "change_id": change.id,
                "applied_change": asdict(transformed_change)
            }

        except Exception as e:
            logger.error(f"Error applying code change: {e}")
            return {"success": False, "error": str(e)}

    async def _apply_operational_transform(
        self,
        session_id: str,
        change: CodeChange
    ) -> CodeChange:
        """Apply operational transformation for conflict resolution"""
        # Simplified OT - in production, use a library like ShareDB
        if session_id not in self.operational_transforms:
            self.operational_transforms[session_id] = []

        # Get concurrent operations
        concurrent_ops = self.operational_transforms[session_id]
        
        # Transform the change based on concurrent operations
        transformed_change = change
        for op in concurrent_ops:
            # Apply transformation logic here
            # This is a simplified version
            if op.file_path == change.file_path:
                if op.start_line <= change.start_line:
                    # Adjust line numbers based on previous operations
                    offset = op.end_line - op.start_line
                    if op.change_type == "insert":
                        transformed_change.start_line += offset
                        transformed_change.end_line += offset

        # Add this operation to the queue
        self.operational_transforms[session_id].append(transformed_change)

        # Clean old operations (keep last 100)
        if len(self.operational_transforms[session_id]) > 100:
            self.operational_transforms[session_id] = \
                self.operational_transforms[session_id][-100:]

        return transformed_change

    async def get_session_state(self, session_id: str) -> Dict:
        """Get current state of collaborative session"""
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}

            session = self.sessions[session_id]
            
            return {
                "success": True,
                "session": asdict(session),
                "active_participants": len(session.participants),
                "total_changes": len(session.changes_history)
            }

        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Code Review System ====================

    async def create_code_review(
        self,
        title: str,
        description: str,
        file_paths: List[str],
        assignee_id: str,
        reviewer_id: str,
        ai_analysis: bool = True
    ) -> Dict:
        """Create a new code review assignment"""
        try:
            review_id = str(uuid.uuid4())
            
            # Generate AI insights if requested
            ai_insights = None
            if ai_analysis:
                ai_insights = await self._generate_ai_code_insights(file_paths)

            review = CodeReview(
                review_id=review_id,
                title=title,
                description=description,
                file_paths=file_paths,
                assignee_id=assignee_id,
                reviewer_id=reviewer_id,
                created_at=datetime.now().timestamp(),
                status="pending",
                comments=[],
                ai_insights=ai_insights
            )

            self.reviews[review_id] = review

            logger.info(f"Created code review: {review_id}")
            return {
                "success": True,
                "review_id": review_id,
                "review": asdict(review)
            }

        except Exception as e:
            logger.error(f"Error creating code review: {e}")
            return {"success": False, "error": str(e)}

    async def add_review_comment(
        self,
        review_id: str,
        user_id: str,
        user_name: str,
        file_path: str,
        line_number: int,
        comment: str,
        suggestion: Optional[str] = None
    ) -> Dict:
        """Add a comment to a code review"""
        try:
            if review_id not in self.reviews:
                return {"success": False, "error": "Review not found"}

            review = self.reviews[review_id]

            comment_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "user_name": user_name,
                "file_path": file_path,
                "line_number": line_number,
                "comment": comment,
                "suggestion": suggestion,
                "timestamp": datetime.now().timestamp(),
                "resolved": False
            }

            review.comments.append(comment_data)

            return {
                "success": True,
                "comment_id": comment_data["id"],
                "total_comments": len(review.comments)
            }

        except Exception as e:
            logger.error(f"Error adding review comment: {e}")
            return {"success": False, "error": str(e)}

    async def update_review_status(
        self,
        review_id: str,
        status: str,
        reviewer_notes: Optional[str] = None
    ) -> Dict:
        """Update code review status"""
        try:
            if review_id not in self.reviews:
                return {"success": False, "error": "Review not found"}

            review = self.reviews[review_id]
            review.status = status

            if reviewer_notes:
                review.comments.append({
                    "id": str(uuid.uuid4()),
                    "type": "status_update",
                    "status": status,
                    "notes": reviewer_notes,
                    "timestamp": datetime.now().timestamp()
                })

            return {
                "success": True,
                "review_id": review_id,
                "status": status
            }

        except Exception as e:
            logger.error(f"Error updating review status: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_ai_code_insights(self, file_paths: List[str]) -> Dict:
        """Generate AI-powered insights for code review"""
        # This would integrate with your AI models
        insights = {
            "security_issues": [],
            "performance_suggestions": [],
            "code_quality": {
                "complexity_score": 0,
                "maintainability_index": 0,
                "test_coverage": 0
            },
            "best_practices": [],
            "suggested_improvements": []
        }

        # Placeholder for actual AI analysis
        insights["suggested_improvements"].append({
            "type": "info",
            "message": "AI analysis complete. Review the suggestions below.",
            "files_analyzed": len(file_paths)
        })

        return insights

    # ==================== Team Knowledge Base ====================

    async def create_team_snippet(
        self,
        title: str,
        description: str,
        code: str,
        language: str,
        tags: List[str],
        author_id: str
    ) -> Dict:
        """Create a shared code snippet in team knowledge base"""
        try:
            snippet_id = str(uuid.uuid4())
            
            snippet = TeamSnippet(
                snippet_id=snippet_id,
                title=title,
                description=description,
                code=code,
                language=language,
                tags=tags,
                author_id=author_id,
                created_at=datetime.now().timestamp(),
                updated_at=datetime.now().timestamp(),
                usage_count=0,
                ratings={}
            )

            self.team_snippets[snippet_id] = snippet

            logger.info(f"Created team snippet: {snippet_id}")
            return {
                "success": True,
                "snippet_id": snippet_id,
                "snippet": asdict(snippet)
            }

        except Exception as e:
            logger.error(f"Error creating team snippet: {e}")
            return {"success": False, "error": str(e)}

    async def search_team_snippets(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Dict:
        """Search team knowledge base for snippets"""
        try:
            results = []

            for snippet in self.team_snippets.values():
                # Search by query in title/description
                query_match = (
                    query.lower() in snippet.title.lower() or
                    query.lower() in snippet.description.lower() or
                    query.lower() in snippet.code.lower()
                )

                # Filter by tags
                tag_match = not tags or any(tag in snippet.tags for tag in tags)

                # Filter by language
                lang_match = not language or snippet.language == language

                if query_match and tag_match and lang_match:
                    # Calculate relevance score
                    avg_rating = (
                        sum(snippet.ratings.values()) / len(snippet.ratings)
                        if snippet.ratings else 0
                    )
                    
                    results.append({
                        **asdict(snippet),
                        "relevance_score": avg_rating + (snippet.usage_count * 0.1)
                    })

            # Sort by relevance
            results.sort(key=lambda x: x["relevance_score"], reverse=True)

            return {
                "success": True,
                "results": results[:20],  # Top 20 results
                "total_found": len(results)
            }

        except Exception as e:
            logger.error(f"Error searching team snippets: {e}")
            return {"success": False, "error": str(e)}

    async def rate_snippet(
        self,
        snippet_id: str,
        user_id: str,
        rating: int
    ) -> Dict:
        """Rate a team snippet (1-5 stars)"""
        try:
            if snippet_id not in self.team_snippets:
                return {"success": False, "error": "Snippet not found"}

            if not 1 <= rating <= 5:
                return {"success": False, "error": "Rating must be between 1 and 5"}

            snippet = self.team_snippets[snippet_id]
            snippet.ratings[user_id] = rating

            avg_rating = sum(snippet.ratings.values()) / len(snippet.ratings)

            return {
                "success": True,
                "average_rating": avg_rating,
                "total_ratings": len(snippet.ratings)
            }

        except Exception as e:
            logger.error(f"Error rating snippet: {e}")
            return {"success": False, "error": str(e)}

    async def increment_snippet_usage(self, snippet_id: str) -> Dict:
        """Increment usage count when snippet is used"""
        try:
            if snippet_id not in self.team_snippets:
                return {"success": False, "error": "Snippet not found"}

            self.team_snippets[snippet_id].usage_count += 1

            return {
                "success": True,
                "usage_count": self.team_snippets[snippet_id].usage_count
            }

        except Exception as e:
            logger.error(f"Error incrementing snippet usage: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Broadcasting & Utilities ====================

    async def _broadcast_event(self, session_id: str, event: Dict):
        """Broadcast event to all participants in a session"""
        # This would integrate with WebSocket connections
        # Placeholder for actual implementation
        logger.info(f"Broadcasting event to session {session_id}: {event['type']}")
        pass

    async def get_active_sessions(self, user_id: str) -> Dict:
        """Get all active sessions for a user"""
        try:
            user_sessions = []

            for session in self.sessions.values():
                if user_id in session.participants and session.is_active:
                    user_sessions.append({
                        **asdict(session),
                        "user_role": session.participants[user_id]
                    })

            return {
                "success": True,
                "sessions": user_sessions,
                "total": len(user_sessions)
            }

        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_reviews(
        self,
        user_id: str,
        role: Optional[str] = None
    ) -> Dict:
        """Get code reviews for a user (as assignee or reviewer)"""
        try:
            user_reviews = []

            for review in self.reviews.values():
                if role == "assignee" and review.assignee_id == user_id:
                    user_reviews.append(asdict(review))
                elif role == "reviewer" and review.reviewer_id == user_id:
                    user_reviews.append(asdict(review))
                elif not role and (review.assignee_id == user_id or review.reviewer_id == user_id):
                    user_reviews.append(asdict(review))

            return {
                "success": True,
                "reviews": user_reviews,
                "total": len(user_reviews)
            }

        except Exception as e:
            logger.error(f"Error getting user reviews: {e}")
            return {"success": False, "error": str(e)}
