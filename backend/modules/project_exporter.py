"""
Project Exporter - Export Projects as ZIP
Export entire projects with filtering and compression
"""

import logging
import zipfile
import os
from typing import List, Optional, Set
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class ProjectExporter:
    """Export projects as ZIP archives"""
    
    # Default exclusions
    DEFAULT_EXCLUDE_PATTERNS = {
        # Version control
        ".git", ".svn", ".hg",
        # Dependencies
        "node_modules", "venv", "env", ".venv", "__pycache__",
        # Build outputs
        "dist", "build", ".next", "out", "target",
        # IDE
        ".vscode", ".idea", ".vs",
        # OS
        ".DS_Store", "Thumbs.db",
        # Logs
        "*.log", "logs",
        # Databases
        "*.db", "*.sqlite", "*.sqlite3"
    }
    
    def __init__(self):
        """Initialize project exporter"""
        logger.info("Project Exporter initialized")
    
    def export_project(
        self,
        project_path: str,
        output_path: Optional[str] = None,
        exclude_patterns: Optional[List[str]] = None,
        include_hidden: bool = False,
        compression_level: int = 6
    ) -> dict:
        """
        Export project as ZIP file
        
        Args:
            project_path: Path to project directory
            output_path: Output ZIP file path (auto-generated if None)
            exclude_patterns: Additional patterns to exclude
            include_hidden: Include hidden files/folders
            compression_level: ZIP compression level (0-9)
            
        Returns:
            Export result with file path and stats
        """
        try:
            project_path = Path(project_path)
            
            if not project_path.exists():
                return {"error": "Project path does not exist"}
            
            # Generate output path if not provided
            if output_path is None:
                output_path = f"{project_path.name}_export.zip"
            
            # Combine exclude patterns
            exclude = self.DEFAULT_EXCLUDE_PATTERNS.copy()
            if exclude_patterns:
                exclude.update(exclude_patterns)
            
            # Create ZIP file
            stats = {
                "total_files": 0,
                "total_size": 0,
                "compressed_size": 0,
                "excluded_files": 0
            }
            
            with zipfile.ZipFile(
                output_path,
                'w',
                zipfile.ZIP_DEFLATED,
                compresslevel=compression_level
            ) as zipf:
                
                for root, dirs, files in os.walk(project_path):
                    # Filter directories
                    dirs[:] = [d for d in dirs if self._should_include(
                        d, exclude, include_hidden, is_dir=True
                    )]
                    
                    for file in files:
                        if not self._should_include(file, exclude, include_hidden):
                            stats["excluded_files"] += 1
                            continue
                        
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(project_path)
                        
                        try:
                            zipf.write(file_path, arcname)
                            stats["total_files"] += 1
                            stats["total_size"] += file_path.stat().st_size
                        except Exception as e:
                            logger.warning(f"Could not add {file_path}: {e}")
            
            # Get compressed size
            stats["compressed_size"] = Path(output_path).stat().st_size
            stats["compression_ratio"] = (
                1 - stats["compressed_size"] / stats["total_size"]
            ) * 100 if stats["total_size"] > 0 else 0
            
            return {
                "success": True,
                "output_path": str(output_path),
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error exporting project: {e}")
            return {"error": str(e)}
    
    def _should_include(
        self,
        name: str,
        exclude_patterns: Set[str],
        include_hidden: bool,
        is_dir: bool = False
    ) -> bool:
        """Check if file/directory should be included"""
        
        # Hidden files/folders
        if not include_hidden and name.startswith('.'):
            return False
        
        # Check exclude patterns
        for pattern in exclude_patterns:
            if pattern.startswith('*.'):
                # Extension pattern
                if name.endswith(pattern[1:]):
                    return False
            else:
                # Exact match
                if name == pattern:
                    return False
        
        return True
    
    def export_files(
        self,
        file_paths: List[str],
        output_path: str,
        base_path: Optional[str] = None
    ) -> dict:
        """
        Export specific files to ZIP
        
        Args:
            file_paths: List of file paths to export
            output_path: Output ZIP file path
            base_path: Base path for relative paths in ZIP
            
        Returns:
            Export result
        """
        try:
            stats = {
                "total_files": 0,
                "total_size": 0,
                "failed_files": 0
            }
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    file_path = Path(file_path)
                    
                    if not file_path.exists():
                        stats["failed_files"] += 1
                        continue
                    
                    # Determine archive name
                    if base_path:
                        try:
                            arcname = file_path.relative_to(base_path)
                        except ValueError:
                            arcname = file_path.name
                    else:
                        arcname = file_path.name
                    
                    try:
                        zipf.write(file_path, arcname)
                        stats["total_files"] += 1
                        stats["total_size"] += file_path.stat().st_size
                    except Exception as e:
                        logger.warning(f"Could not add {file_path}: {e}")
                        stats["failed_files"] += 1
            
            stats["compressed_size"] = Path(output_path).stat().st_size
            
            return {
                "success": True,
                "output_path": str(output_path),
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error exporting files: {e}")
            return {"error": str(e)}
    
    def list_archive_contents(self, archive_path: str) -> dict:
        """List contents of ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                files = []
                total_size = 0
                compressed_size = 0
                
                for info in zipf.filelist:
                    files.append({
                        "filename": info.filename,
                        "size": info.file_size,
                        "compressed_size": info.compress_size,
                        "date": f"{info.date_time[0]}-{info.date_time[1]:02d}-{info.date_time[2]:02d}"
                    })
                    total_size += info.file_size
                    compressed_size += info.compress_size
                
                return {
                    "files": files,
                    "total_files": len(files),
                    "total_size": total_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": (1 - compressed_size / total_size) * 100 if total_size > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error listing archive: {e}")
            return {"error": str(e)}
