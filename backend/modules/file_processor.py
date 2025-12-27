"""
File Processor Module for Friday Agent
Handles file uploads, analysis with Gemini Vision, and PDF text extraction
"""
import os
import logging
import mimetypes
from pathlib import Path
from typing import Dict, Optional, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileProcessor:
    def __init__(self, upload_dir: str = "uploads"):
        """Initialize file processor"""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.vision_available = True
            logger.info("Gemini Vision initialized")
        else:
            self.vision_available = False
            logger.warning("GEMINI_API_KEY not found - vision features disabled")
        
        # Supported file types
        self.supported_images = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        self.supported_documents = {'.pdf', '.txt'}
        
        logger.info(f"File processor initialized. Upload directory: {self.upload_dir}")
    
    def validate_file(self, filename: str, file_size: int) -> Dict:
        """Validate file type and size"""
        file_ext = Path(filename).suffix.lower()
        
        # Check if supported
        if file_ext not in (self.supported_images | self.supported_documents):
            return {
                "valid": False,
                "error": f"Unsupported file type: {file_ext}. Supported: images (jpg, png, gif, webp) and PDF"
            }
        
        # Check size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return {
                "valid": False,
                "error": f"File too large: {file_size / 1024 / 1024:.1f}MB. Maximum: 10MB"
            }
        
        return {
            "valid": True,
            "type": "image" if file_ext in self.supported_images else "document",
            "extension": file_ext
        }
    
    async def save_file(self, filename: str, file_content: bytes) -> str:
        """Save uploaded file and return path"""
        import uuid
        from datetime import datetime
        
        # Generate unique filename
        file_ext = Path(filename).suffix.lower()
        unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = self.upload_dir / unique_name
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved file: {file_path}")
        
        return str(file_path)
    
    async def analyze_image(self, file_path: str, prompt: Optional[str] = None) -> Dict:
        """Analyze image using Gemini Vision"""
        if not self.vision_available:
            return {
                "success": False,
                "error": "Vision API not available"
            }
        
        try:
            from PIL import Image
            
            # Load image
            image = Image.open(file_path)
            
            # Default prompt if none provided
            if not prompt:
                prompt = """Analyze this image and provide:
1. A brief description of what you see
2. Key objects or elements present
3. Any text visible in the image
4. Overall context or purpose

Be concise but informative."""
            
            # Generate analysis
            response = self.model.generate_content([prompt, image])
            
            # Get image metadata
            width, height = image.size
            format_name = image.format
            
            return {
                "success": True,
                "analysis": response.text,
                "metadata": {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "mode": image.mode
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def extract_pdf_text(self, file_path: str) -> Dict:
        """Extract text from PDF file"""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num} ---\n{text}")
            
            full_text = "\n\n".join(text_content)
            
            return {
                "success": True,
                "text": full_text,
                "metadata": {
                    "pages": len(reader.pages),
                    "page_count": len(text_content),
                    "has_text": len(full_text) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_document(self, file_path: str, prompt: Optional[str] = None) -> Dict:
        """Analyze document (PDF or text) with Gemini"""
        file_ext = Path(file_path).suffix.lower()
        
        # Extract text first
        if file_ext == '.pdf':
            extraction_result = await self.extract_pdf_text(file_path)
            if not extraction_result['success']:
                return extraction_result
            
            document_text = extraction_result['text']
            metadata = extraction_result['metadata']
        else:
            # Plain text file
            with open(file_path, 'r', encoding='utf-8') as f:
                document_text = f.read()
            metadata = {"type": "text"}
        
        # Analyze with Gemini if available
        if self.vision_available and document_text.strip():
            try:
                if not prompt:
                    prompt = "Summarize this document and extract key information:"
                
                full_prompt = f"{prompt}\n\n{document_text[:8000]}"  # Limit to 8k chars
                
                response = self.model.generate_content(full_prompt)
                
                return {
                    "success": True,
                    "text": document_text,
                    "analysis": response.text,
                    "metadata": metadata
                }
            except Exception as e:
                logger.error(f"Error analyzing document with Gemini: {e}")
                # Fall back to just returning text
                return {
                    "success": True,
                    "text": document_text,
                    "analysis": "Document text extracted (analysis unavailable)",
                    "metadata": metadata
                }
        else:
            return {
                "success": True,
                "text": document_text,
                "analysis": "Text extraction only (AI analysis disabled)",
                "metadata": metadata
            }
    
    async def process_file(self, file_path: str, file_type: str, user_prompt: Optional[str] = None) -> Dict:
        """Process file based on type"""
        if file_type == "image":
            return await self.analyze_image(file_path, user_prompt)
        elif file_type == "document":
            return await self.analyze_document(file_path, user_prompt)
        else:
            return {
                "success": False,
                "error": f"Unknown file type: {file_type}"
            }
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """Delete files older than specified days"""
        from datetime import datetime, timedelta
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} old files")
        return deleted_count
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get file metadata"""
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "File not found"}
        
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))
        
        return {
            "filename": path.name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "mime_type": mime_type,
            "extension": path.suffix.lower(),
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }
