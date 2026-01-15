"""
RAG (Retrieval-Augmented Generation) Engine
Vector database for codebase intelligence and semantic search
"""
import os
import hashlib
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not installed. Run: pip install chromadb")

class RAGEngine:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        if CHROMADB_AVAILABLE:
            self._initialize_chromadb()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="codebase",
                metadata={"description": "F.R.I.D.A.Y. codebase knowledge"}
            )
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        
        return chunks
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file and extract content"""
        try:
            file_ext = Path(file_path).suffix.lower()
            content = ""
            
            # Handle different file types
            if file_ext == '.docx':
                # Process DOCX files
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    print("python-docx not installed. Install with: pip install python-docx")
                    return None
            elif file_ext == '.md':
                # Process Markdown files
                try:
                    import markdown
                    with open(file_path, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                    # Convert markdown to plain text (strip HTML)
                    html = markdown.markdown(md_content)
                    # Simple HTML strip (for better context)
                    from html.parser import HTMLParser
                    class MLStripper(HTMLParser):
                        def __init__(self):
                            super().__init__()
                            self.reset()
                            self.strict = False
                            self.convert_charrefs = True
                            self.text = []
                        def handle_data(self, d):
                            self.text.append(d)
                        def get_data(self):
                            return ''.join(self.text)
                    stripper = MLStripper()
                    stripper.feed(html)
                    content = stripper.get_data()
                except Exception as e:
                    print(f"Error processing markdown: {e}")
                    # Fallback to reading as plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
            elif file_ext == '.pdf':
                # Process PDF files
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    content = '\n'.join([page.extract_text() for page in reader.pages])
                except Exception as e:
                    print(f"Error processing PDF: {e}")
                    return None
            else:
                # Default: read as text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Get file metadata
            file_stat = os.stat(file_path)
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            return {
                'path': file_path,
                'content': content,
                'size': file_stat.st_size,
                'hash': file_hash,
                'extension': Path(file_path).suffix
            }
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def add_document(self, file_path: str, metadata: Dict = None) -> bool:
        """Add a document to the vector database"""
        if not CHROMADB_AVAILABLE or not self.collection:
            return False
        
        try:
            file_data = self.process_file(file_path)
            if not file_data:
                return False
            
            # Chunk the content
            chunks = self.chunk_text(file_data['content'])
            
            # Prepare data for ChromaDB
            ids = [f"{file_data['hash']}_{i}" for i in range(len(chunks))]
            documents = chunks
            metadatas = [{
                'path': file_data['path'],
                'chunk_index': i,
                'total_chunks': len(chunks),
                'extension': file_data['extension'],
                **(metadata or {})
            } for i in range(len(chunks))]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def add_directory(self, directory_path: str, extensions: List[str] = None) -> Dict[str, int]:
        """Add all files from a directory"""
        if extensions is None:
            extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.md', '.txt', '.pdf', '.docx']
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        for root, dirs, files in os.walk(directory_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file_path).suffix
                
                if file_ext in extensions:
                    if self.add_document(file_path):
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                else:
                    stats['skipped'] += 1
        
        return stats
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Semantic search in the vector database"""
        if not CHROMADB_AVAILABLE or not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def get_context_for_query(self, query: str, max_tokens: int = 4000) -> str:
        """Get relevant context for a query, limited by token count"""
        results = self.query(query, n_results=10)
        
        context_parts = []
        total_length = 0
        
        for result in results:
            content = result['content']
            metadata = result['metadata']
            
            # Format context with file path
            formatted = f"# File: {metadata.get('path', 'unknown')}\n{content}\n\n"
            
            if total_length + len(formatted) > max_tokens * 4:  # Rough token estimate
                break
            
            context_parts.append(formatted)
            total_length += len(formatted)
        
        return "".join(context_parts)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all indexed documents"""
        if not CHROMADB_AVAILABLE or not self.collection:
            return []
        
        try:
            # Get all documents
            results = self.collection.get()
            
            # Group by file path
            files = {}
            for metadata in results['metadatas']:
                path = metadata.get('path')
                if path and path not in files:
                    files[path] = {
                        'path': path,
                        'extension': metadata.get('extension'),
                        'chunks': 0
                    }
                if path:
                    files[path]['chunks'] += 1
            
            return list(files.values())
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, file_path: str) -> bool:
        """Delete a document from the database"""
        if not CHROMADB_AVAILABLE or not self.collection:
            return False
        
        try:
            # Get all IDs for this file
            results = self.collection.get(
                where={"path": file_path}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all documents from the database"""
        if not CHROMADB_AVAILABLE or not self.client:
            return False
        
        try:
            self.client.delete_collection("codebase")
            self.collection = self.client.create_collection(
                name="codebase",
                metadata={"description": "F.R.I.D.A.Y. codebase knowledge"}
            )
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not CHROMADB_AVAILABLE or not self.collection:
            return {"available": False}
        
        try:
            count = self.collection.count()
            documents = self.list_documents()
            
            return {
                "available": True,
                "total_chunks": count,
                "total_files": len(documents),
                "files": documents
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"available": False, "error": str(e)}
    
    def summarize_document(self, file_path: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Summarize a document using RAG and optionally AI
        
        Args:
            file_path: Path to document to summarize
            use_ai: Whether to use AI for summarization (requires Gemini API)
        
        Returns:
            Dictionary with summary, key points, and metadata
        """
        try:
            # Process the document
            file_data = self.process_file(file_path)
            if not file_data:
                return {
                    "success": False,
                    "error": "Failed to process document"
                }
            
            content = file_data['content']
            
            # Extract basic metadata
            word_count = len(content.split())
            char_count = len(content)
            
            # Chunk the document
            chunks = self.chunk_text(content, chunk_size=1000, overlap=200)
            
            result = {
                "success": True,
                "file_path": file_path,
                "metadata": {
                    "word_count": word_count,
                    "char_count": char_count,
                    "total_chunks": len(chunks),
                    "extension": file_data['extension']
                }
            }
            
            # If AI summarization is requested and available
            if use_ai:
                try:
                    import google.generativeai as genai
                    import os
                    
                    # Check if Gemini is configured
                    api_key = os.getenv('GEMINI_API_KEY')
                    if not api_key:
                        result["summary"] = "AI summarization unavailable - GEMINI_API_KEY not set"
                        result["key_points"] = []
                        return result
                    
                    # Configure Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    
                    # Create summarization prompt
                    # Limit content to avoid token limits (approx 30k characters)
                    content_preview = content[:30000] if len(content) > 30000 else content
                    
                    prompt = f"""Analyze and summarize the following document. Provide:

1. A concise executive summary (2-3 paragraphs)
2. Key points and main ideas (bullet points)
3. Important topics or themes covered
4. Any notable conclusions or recommendations

Document content:
---
{content_preview}
---

Format your response as:

SUMMARY:
[Your summary here]

KEY POINTS:
- [Point 1]
- [Point 2]
...

TOPICS:
- [Topic 1]
- [Topic 2]
..."""
                    
                    # Generate summary
                    response = model.generate_content(prompt)
                    summary_text = response.text
                    
                    # Parse the response
                    sections = {}
                    current_section = None
                    current_content = []
                    
                    for line in summary_text.split('\n'):
                        line = line.strip()
                        if line.startswith('SUMMARY:'):
                            if current_section:
                                sections[current_section] = '\n'.join(current_content)
                            current_section = 'summary'
                            current_content = []
                        elif line.startswith('KEY POINTS:'):
                            if current_section:
                                sections[current_section] = '\n'.join(current_content)
                            current_section = 'key_points'
                            current_content = []
                        elif line.startswith('TOPICS:'):
                            if current_section:
                                sections[current_section] = '\n'.join(current_content)
                            current_section = 'topics'
                            current_content = []
                        elif line and current_section:
                            current_content.append(line)
                    
                    # Add last section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Extract key points as list
                    key_points = []
                    if 'key_points' in sections:
                        for line in sections['key_points'].split('\n'):
                            line = line.strip()
                            if line.startswith('-') or line.startswith('•'):
                                key_points.append(line.lstrip('-• ').strip())
                            elif line:
                                key_points.append(line)
                    
                    # Extract topics as list
                    topics = []
                    if 'topics' in sections:
                        for line in sections['topics'].split('\n'):
                            line = line.strip()
                            if line.startswith('-') or line.startswith('•'):
                                topics.append(line.lstrip('-• ').strip())
                            elif line:
                                topics.append(line)
                    
                    result["summary"] = sections.get('summary', summary_text).strip()
                    result["key_points"] = key_points
                    result["topics"] = topics
                    result["full_response"] = summary_text
                    
                except Exception as e:
                    print(f"AI summarization error: {e}")
                    result["summary"] = f"AI summarization failed: {str(e)}"
                    result["key_points"] = []
            else:
                # Basic non-AI summary
                preview_length = min(500, len(content))
                result["summary"] = content[:preview_length] + ("..." if len(content) > preview_length else "")
                result["key_points"] = []
            
            return result
            
        except Exception as e:
            print(f"Error summarizing document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
