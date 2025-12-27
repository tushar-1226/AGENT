"""
Diff Manager - Beautiful Side-by-Side Code Diff Viewer
Compare code versions with syntax highlighting and intelligent diff
"""

import logging
import difflib
from typing import List, Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class DiffManager:
    """Manage code diffs and comparisons"""
    
    def __init__(self):
        """Initialize diff manager"""
        logger.info("Diff Manager initialized")
    
    def generate_diff(
        self,
        original: str,
        modified: str,
        context_lines: int = 3,
        format_type: str = "unified"
    ) -> Dict[str, Any]:
        """
        Generate diff between two code versions
        
        Args:
            original: Original code
            modified: Modified code
            context_lines: Number of context lines
            format_type: 'unified', 'side-by-side', or 'inline'
            
        Returns:
            Diff result with formatted output
        """
        try:
            original_lines = original.splitlines(keepends=True)
            modified_lines = modified.splitlines(keepends=True)
            
            if format_type == "unified":
                diff_output = self._unified_diff(original_lines, modified_lines, context_lines)
            elif format_type == "side-by-side":
                diff_output = self._side_by_side_diff(original_lines, modified_lines)
            else:  # inline
                diff_output = self._inline_diff(original_lines, modified_lines)
            
            stats = self._calculate_diff_stats(original_lines, modified_lines)
            
            return {
                "format": format_type,
                "diff": diff_output,
                "stats": stats,
                "original_lines": len(original_lines),
                "modified_lines": len(modified_lines)
            }
            
        except Exception as e:
            logger.error(f"Error generating diff: {e}")
            return {"error": str(e)}
    
    def _unified_diff(
        self,
        original: List[str],
        modified: List[str],
        context_lines: int
    ) -> str:
        """Generate unified diff format"""
        diff = difflib.unified_diff(
            original,
            modified,
            fromfile="original",
            tofile="modified",
            lineterm="",
            n=context_lines
        )
        return "\n".join(diff)
    
    def _side_by_side_diff(
        self,
        original: List[str],
        modified: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate side-by-side diff"""
        differ = difflib.Differ()
        diff = list(differ.compare(original, modified))
        
        result = []
        i = 0
        
        while i < len(diff):
            line = diff[i]
            
            if line.startswith("  "):  # Unchanged
                result.append({
                    "type": "unchanged",
                    "left": line[2:].rstrip(),
                    "right": line[2:].rstrip(),
                    "left_line": i + 1,
                    "right_line": i + 1
                })
            
            elif line.startswith("- "):  # Deleted
                left_line = line[2:].rstrip()
                right_line = ""
                
                # Check if next line is addition (modification)
                if i + 1 < len(diff) and diff[i + 1].startswith("+ "):
                    right_line = diff[i + 1][2:].rstrip()
                    result.append({
                        "type": "modified",
                        "left": left_line,
                        "right": right_line,
                        "left_line": i + 1,
                        "right_line": i + 1
                    })
                    i += 1
                else:
                    result.append({
                        "type": "deleted",
                        "left": left_line,
                        "right": "",
                        "left_line": i + 1,
                        "right_line": None
                    })
            
            elif line.startswith("+ "):  # Added
                result.append({
                    "type": "added",
                    "left": "",
                    "right": line[2:].rstrip(),
                    "left_line": None,
                    "right_line": i + 1
                })
            
            i += 1
        
        return result
    
    def _inline_diff(
        self,
        original: List[str],
        modified: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate inline diff with character-level changes"""
        result = []
        
        matcher = difflib.SequenceMatcher(None, original, modified)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for line in original[i1:i2]:
                    result.append({
                        "type": "unchanged",
                        "content": line.rstrip()
                    })
            
            elif tag == "delete":
                for line in original[i1:i2]:
                    result.append({
                        "type": "deleted",
                        "content": line.rstrip()
                    })
            
            elif tag == "insert":
                for line in modified[j1:j2]:
                    result.append({
                        "type": "added",
                        "content": line.rstrip()
                    })
            
            elif tag == "replace":
                # Show both deleted and added
                for line in original[i1:i2]:
                    result.append({
                        "type": "deleted",
                        "content": line.rstrip()
                    })
                for line in modified[j1:j2]:
                    result.append({
                        "type": "added",
                        "content": line.rstrip()
                    })
        
        return result
    
    def _calculate_diff_stats(
        self,
        original: List[str],
        modified: List[str]
    ) -> Dict[str, int]:
        """Calculate diff statistics"""
        matcher = difflib.SequenceMatcher(None, original, modified)
        
        stats = {
            "additions": 0,
            "deletions": 0,
            "modifications": 0,
            "unchanged": 0
        }
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["unchanged"] += (i2 - i1)
            elif tag == "delete":
                stats["deletions"] += (i2 - i1)
            elif tag == "insert":
                stats["additions"] += (j2 - j1)
            elif tag == "replace":
                stats["modifications"] += max(i2 - i1, j2 - j1)
        
        return stats
    
    def compare_files(
        self,
        file1_path: str,
        file2_path: str,
        format_type: str = "side-by-side"
    ) -> Dict[str, Any]:
        """Compare two files"""
        try:
            with open(file1_path, 'r') as f1:
                content1 = f1.read()
            
            with open(file2_path, 'r') as f2:
                content2 = f2.read()
            
            result = self.generate_diff(content1, content2, format_type=format_type)
            result["file1"] = file1_path
            result["file2"] = file2_path
            
            return result
            
        except Exception as e:
            logger.error(f"Error comparing files: {e}")
            return {"error": str(e)}
    
    def get_git_diff(
        self,
        repo_path: str,
        commit1: str = "HEAD",
        commit2: str = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get git diff between commits"""
        try:
            import subprocess
            
            cmd = ["git", "-C", repo_path, "diff"]
            
            if commit2:
                cmd.append(f"{commit1}..{commit2}")
            else:
                cmd.append(commit1)
            
            if file_path:
                cmd.append("--", file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "diff": result.stdout,
                    "commit1": commit1,
                    "commit2": commit2 or "working directory"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
        except Exception as e:
            logger.error(f"Error getting git diff: {e}")
            return {"error": str(e)}
