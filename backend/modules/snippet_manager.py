"""
Snippet Manager - Code Snippet Library with AI Search
Save, organize, and search code snippets with AI-powered semantic search
"""

import logging
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SnippetManager:
    """Manage code snippets with AI-powered search"""
    
    def __init__(self, db_path: str = "snippets.db", gemini_processor=None):
        """
        Initialize snippet manager
        
        Args:
            db_path: Path to SQLite database
            gemini_processor: Gemini AI for semantic search
        """
        self.db_path = db_path
        self.gemini = gemini_processor
        self._init_database()
        logger.info("Snippet Manager initialized")
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                tags TEXT,
                category TEXT,
                user_id INTEGER,
                is_public BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snippets_language 
            ON snippets(language)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snippets_tags 
            ON snippets(tags)
        """)
        
        conn.commit()
        conn.close()
    
    def create_snippet(
        self,
        title: str,
        code: str,
        language: str,
        description: str = "",
        tags: List[str] = None,
        category: str = "",
        user_id: Optional[int] = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new code snippet
        
        Args:
            title: Snippet title
            code: Code content
            language: Programming language
            description: Optional description
            tags: List of tags
            category: Category name
            user_id: User ID
            is_public: Whether snippet is public
            
        Returns:
            Created snippet object
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tags_str = ",".join(tags) if tags else ""
            
            cursor.execute("""
                INSERT INTO snippets 
                (title, description, code, language, tags, category, user_id, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, code, language, tags_str, category, user_id, is_public))
            
            snippet_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return self.get_snippet(snippet_id)
            
        except Exception as e:
            logger.error(f"Error creating snippet: {e}")
            return {"error": str(e)}
    
    def get_snippet(self, snippet_id: int) -> Optional[Dict[str, Any]]:
        """Get snippet by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                snippet = dict(row)
                snippet["tags"] = snippet["tags"].split(",") if snippet["tags"] else []
                return snippet
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting snippet: {e}")
            return None
    
    def list_snippets(
        self,
        user_id: Optional[int] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List snippets with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM snippets WHERE 1=1"
            params = []
            
            if user_id is not None:
                query += " AND (user_id = ? OR is_public = 1)"
                params.append(user_id)
            
            if language:
                query += " AND language = ?"
                params.append(language)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            snippets = []
            for row in rows:
                snippet = dict(row)
                snippet["tags"] = snippet["tags"].split(",") if snippet["tags"] else []
                snippets.append(snippet)
            
            return snippets
            
        except Exception as e:
            logger.error(f"Error listing snippets: {e}")
            return []
    
    def update_snippet(
        self,
        snippet_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        code: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> bool:
        """Update snippet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if code is not None:
                updates.append("code = ?")
                params.append(code)
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(",".join(tags))
            
            if category is not None:
                updates.append("category = ?")
                params.append(category)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(snippet_id)
                
                query = f"UPDATE snippets SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating snippet: {e}")
            return False
    
    def delete_snippet(self, snippet_id: int) -> bool:
        """Delete snippet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting snippet: {e}")
            return False
    
    async def search_snippets(
        self,
        query: str,
        language: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        AI-powered semantic search for snippets
        
        Args:
            query: Search query
            language: Filter by language
            user_id: Filter by user
            limit: Maximum results
            
        Returns:
            List of matching snippets
        """
        try:
            # Get all snippets (with filters)
            snippets = self.list_snippets(user_id, language, limit=1000)
            
            if not snippets:
                return []
            
            # Simple keyword search first
            keyword_matches = []
            for snippet in snippets:
                score = 0
                query_lower = query.lower()
                
                if query_lower in snippet["title"].lower():
                    score += 10
                if query_lower in snippet["description"].lower():
                    score += 5
                if query_lower in snippet["code"].lower():
                    score += 3
                if snippet["tags"]:
                    for tag in snippet["tags"]:
                        if query_lower in tag.lower():
                            score += 7
                
                if score > 0:
                    snippet["search_score"] = score
                    keyword_matches.append(snippet)
            
            # Sort by score
            keyword_matches.sort(key=lambda x: x["search_score"], reverse=True)
            
            # AI semantic search if Gemini available
            if self.gemini and len(keyword_matches) < 5:
                semantic_matches = await self._semantic_search(query, snippets)
                
                # Merge results
                seen_ids = {s["id"] for s in keyword_matches}
                for match in semantic_matches:
                    if match["id"] not in seen_ids:
                        keyword_matches.append(match)
            
            return keyword_matches[:limit]
            
        except Exception as e:
            logger.error(f"Error searching snippets: {e}")
            return []
    
    async def _semantic_search(
        self, query: str, snippets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use AI for semantic search"""
        try:
            # Build context for AI
            snippet_summaries = []
            for i, snippet in enumerate(snippets[:50]):  # Limit for performance
                snippet_summaries.append(
                    f"{i}. {snippet['title']} - {snippet['description'][:100]}"
                )
            
            prompt = f"""Given this search query: "{query}"

Find the most relevant code snippets from this list:

{chr(10).join(snippet_summaries)}

Return only the numbers (0-indexed) of the top 5 most relevant snippets, comma-separated.
Example: 2,5,8,12,15"""
            
            response = await self.gemini.generate_content(prompt)
            
            # Parse response
            import re
            numbers = re.findall(r'\d+', response)
            indices = [int(n) for n in numbers if int(n) < len(snippets)]
            
            matches = []
            for idx in indices[:5]:
                snippet = snippets[idx].copy()
                snippet["search_score"] = 10 - indices.index(idx)
                matches.append(snippet)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def increment_usage(self, snippet_id: int):
        """Increment usage count for snippet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE snippets SET usage_count = usage_count + 1 WHERE id = ?",
                (snippet_id,)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
    
    def get_popular_snippets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most used snippets"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM snippets 
                WHERE is_public = 1 
                ORDER BY usage_count DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            snippets = []
            for row in rows:
                snippet = dict(row)
                snippet["tags"] = snippet["tags"].split(",") if snippet["tags"] else []
                snippets.append(snippet)
            
            return snippets
            
        except Exception as e:
            logger.error(f"Error getting popular snippets: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get snippet statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM snippets")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT language) FROM snippets")
            languages = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT category) FROM snippets")
            categories = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_snippets": total,
                "languages": languages,
                "categories": categories
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
