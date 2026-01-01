"""
Code Search & Navigation Module
Semantic code search, dependency analysis, dead code detection, find similar patterns
"""

import asyncio
import logging
import os
import re
import ast
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class CodeSearchResult:
    """Represents a code search result"""
    file_path: str
    line_number: int
    line_content: str
    context_before: List[str]
    context_after: List[str]
    relevance_score: float
    match_type: str  # exact, semantic, pattern, fuzzy


@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, variable)"""
    name: str
    type: str  # function, class, variable, import
    file_path: str
    line_number: int
    definition: str
    docstring: Optional[str]
    dependencies: List[str]


@dataclass
class DependencyNode:
    """Represents a dependency in the graph"""
    symbol: str
    file_path: str
    depends_on: List[str]
    depended_by: List[str]
    import_count: int
    is_external: bool


class CodeSearchNavigation:
    """
    Advanced Code Search & Navigation:
    - Semantic code search across entire codebase
    - Find similar code patterns
    - Dependency impact analysis
    - Dead code detection
    - Symbol navigation
    """

    def __init__(self, llm_processor=None):
        self.llm = llm_processor
        self.code_index: Dict[str, List[CodeSymbol]] = {}
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self.file_hashes: Dict[str, str] = {}
        self.search_cache: Dict[str, List[CodeSearchResult]] = {}
        logger.info("Code Search & Navigation module initialized")

    # ==================== Indexing ====================

    async def index_codebase(
        self,
        project_path: str,
        file_extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None
    ) -> Dict:
        """Index entire codebase for fast searching"""
        try:
            if not file_extensions:
                file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']
            
            if not exclude_dirs:
                exclude_dirs = ['node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build']

            indexed_files = 0
            total_symbols = 0
            start_time = datetime.now()

            # Walk through directory
            for root, dirs, files in os.walk(project_path):
                # Exclude directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1]

                    if ext in file_extensions:
                        try:
                            symbols = await self._index_file(file_path, ext)
                            self.code_index[file_path] = symbols
                            total_symbols += len(symbols)
                            indexed_files += 1
                        except Exception as e:
                            logger.warning(f"Error indexing {file_path}: {e}")

            # Build dependency graph
            await self._build_dependency_graph()

            elapsed = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "indexed_files": indexed_files,
                "total_symbols": total_symbols,
                "time_elapsed": elapsed,
                "project_path": project_path
            }

        except Exception as e:
            logger.error(f"Error indexing codebase: {e}")
            return {"success": False, "error": str(e)}

    async def _index_file(self, file_path: str, extension: str) -> List[CodeSymbol]:
        """Index a single file and extract symbols"""
        symbols = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Calculate file hash for change detection
            self.file_hashes[file_path] = hashlib.md5(content.encode()).hexdigest()

            if extension == '.py':
                symbols = self._index_python_file(file_path, content)
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                symbols = self._index_javascript_file(file_path, content)

        except Exception as e:
            logger.warning(f"Error indexing file {file_path}: {e}")

        return symbols

    def _index_python_file(self, file_path: str, content: str) -> List[CodeSymbol]:
        """Index Python file using AST"""
        symbols = []

        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Index functions
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    symbols.append(CodeSymbol(
                        name=node.name,
                        type="function",
                        file_path=file_path,
                        line_number=node.lineno,
                        definition=f"def {node.name}(...)",
                        docstring=docstring,
                        dependencies=self._extract_function_dependencies(node)
                    ))
                
                # Index classes
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    symbols.append(CodeSymbol(
                        name=node.name,
                        type="class",
                        file_path=file_path,
                        line_number=node.lineno,
                        definition=f"class {node.name}",
                        docstring=docstring,
                        dependencies=[]
                    ))
                
                # Index imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        symbols.append(CodeSymbol(
                            name=alias.name,
                            type="import",
                            file_path=file_path,
                            line_number=node.lineno,
                            definition=f"import {alias.name}",
                            docstring=None,
                            dependencies=[]
                        ))
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        symbols.append(CodeSymbol(
                            name=f"{module}.{alias.name}",
                            type="import",
                            file_path=file_path,
                            line_number=node.lineno,
                            definition=f"from {module} import {alias.name}",
                            docstring=None,
                            dependencies=[]
                        ))

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")

        return symbols

    def _index_javascript_file(self, file_path: str, content: str) -> List[CodeSymbol]:
        """Index JavaScript/TypeScript file using regex"""
        symbols = []
        lines = content.split('\n')

        # Function declarations
        func_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\('
        for i, line in enumerate(lines):
            matches = re.finditer(func_pattern, line)
            for match in matches:
                symbols.append(CodeSymbol(
                    name=match.group(1),
                    type="function",
                    file_path=file_path,
                    line_number=i + 1,
                    definition=line.strip(),
                    docstring=None,
                    dependencies=[]
                ))

        # Arrow functions
        arrow_pattern = r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>'
        for i, line in enumerate(lines):
            matches = re.finditer(arrow_pattern, line)
            for match in matches:
                symbols.append(CodeSymbol(
                    name=match.group(1),
                    type="function",
                    file_path=file_path,
                    line_number=i + 1,
                    definition=line.strip(),
                    docstring=None,
                    dependencies=[]
                ))

        # Class declarations
        class_pattern = r'(?:export\s+)?class\s+(\w+)'
        for i, line in enumerate(lines):
            matches = re.finditer(class_pattern, line)
            for match in matches:
                symbols.append(CodeSymbol(
                    name=match.group(1),
                    type="class",
                    file_path=file_path,
                    line_number=i + 1,
                    definition=line.strip(),
                    docstring=None,
                    dependencies=[]
                ))

        # Imports
        import_pattern = r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'
        for i, line in enumerate(lines):
            matches = re.finditer(import_pattern, line)
            for match in matches:
                symbols.append(CodeSymbol(
                    name=match.group(1),
                    type="import",
                    file_path=file_path,
                    line_number=i + 1,
                    definition=line.strip(),
                    docstring=None,
                    dependencies=[]
                ))

        return symbols

    def _extract_function_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract dependencies from function AST node"""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.append(child.func.attr)

        return list(set(dependencies))

    # ==================== Semantic Search ====================

    async def semantic_search(
        self,
        query: str,
        project_path: Optional[str] = None,
        max_results: int = 20
    ) -> Dict:
        """Perform semantic search across codebase"""
        try:
            # Check cache
            cache_key = f"{query}:{project_path}"
            if cache_key in self.search_cache:
                return {
                    "success": True,
                    "results": self.search_cache[cache_key][:max_results],
                    "cached": True
                }

            results = []

            # Search indexed symbols
            for file_path, symbols in self.code_index.items():
                if project_path and not file_path.startswith(project_path):
                    continue

                for symbol in symbols:
                    relevance = self._calculate_relevance(query, symbol)
                    if relevance > 0.3:  # Threshold
                        # Read file context
                        context = await self._get_code_context(
                            file_path,
                            symbol.line_number
                        )
                        
                        results.append(CodeSearchResult(
                            file_path=file_path,
                            line_number=symbol.line_number,
                            line_content=symbol.definition,
                            context_before=context["before"],
                            context_after=context["after"],
                            relevance_score=relevance,
                            match_type="semantic"
                        ))

            # Sort by relevance
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            # Cache results
            self.search_cache[cache_key] = results

            return {
                "success": True,
                "results": [asdict(r) for r in results[:max_results]],
                "total_found": len(results),
                "cached": False
            }

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_relevance(self, query: str, symbol: CodeSymbol) -> float:
        """Calculate relevance score between query and symbol"""
        score = 0.0
        query_lower = query.lower()

        # Exact name match
        if query_lower == symbol.name.lower():
            score += 1.0
        # Partial name match
        elif query_lower in symbol.name.lower():
            score += 0.7
        # Name contains query words
        elif any(word in symbol.name.lower() for word in query_lower.split()):
            score += 0.5

        # Docstring match
        if symbol.docstring:
            if query_lower in symbol.docstring.lower():
                score += 0.4

        # Definition match
        if query_lower in symbol.definition.lower():
            score += 0.3

        return min(score, 1.0)

    async def _get_code_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 3
    ) -> Dict:
        """Get code context around a line"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)

            return {
                "before": [line.rstrip() for line in lines[start:line_number-1]],
                "after": [line.rstrip() for line in lines[line_number:end]]
            }

        except Exception as e:
            logger.warning(f"Error getting context: {e}")
            return {"before": [], "after": []}

    # ==================== Pattern Search ====================

    async def find_similar_patterns(
        self,
        code_snippet: str,
        language: str = "python",
        threshold: float = 0.7
    ) -> Dict:
        """Find similar code patterns in the codebase"""
        try:
            results = []

            # Normalize code snippet
            normalized_query = self._normalize_code(code_snippet, language)

            for file_path, symbols in self.code_index.items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Find similar patterns
                    similar_blocks = self._find_code_blocks(content, normalized_query, language)
                    
                    for block, similarity in similar_blocks:
                        if similarity >= threshold:
                            results.append({
                                "file_path": file_path,
                                "code_block": block,
                                "similarity": similarity
                            })

                except Exception as e:
                    continue

            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)

            return {
                "success": True,
                "results": results[:20],
                "total_found": len(results)
            }

        except Exception as e:
            logger.error(f"Error finding similar patterns: {e}")
            return {"success": False, "error": str(e)}

    def _normalize_code(self, code: str, language: str) -> str:
        """Normalize code for comparison"""
        # Remove comments and extra whitespace
        if language == "python":
            # Remove Python comments
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        elif language in ["javascript", "typescript"]:
            # Remove JS comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        return code.strip()

    def _find_code_blocks(
        self,
        content: str,
        query: str,
        language: str
    ) -> List[Tuple[str, float]]:
        """Find similar code blocks in content"""
        blocks = []
        
        # Simple similarity: count matching tokens
        query_tokens = set(query.split())
        
        # Split content into blocks (functions, classes)
        if language == "python":
            pattern = r'((?:def|class)\s+\w+.*?(?=\n(?:def|class)|$))'
        else:
            pattern = r'((?:function|class)\s+\w+.*?(?=\n(?:function|class)|$))'

        for match in re.finditer(pattern, content, re.DOTALL):
            block = match.group(1)
            normalized_block = self._normalize_code(block, language)
            block_tokens = set(normalized_block.split())
            
            # Calculate Jaccard similarity
            intersection = len(query_tokens & block_tokens)
            union = len(query_tokens | block_tokens)
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0:
                blocks.append((block, similarity))

        return blocks

    # ==================== Dependency Analysis ====================

    async def _build_dependency_graph(self):
        """Build dependency graph from indexed code"""
        try:
            for file_path, symbols in self.code_index.items():
                for symbol in symbols:
                    if symbol.type in ["function", "class"]:
                        node_key = f"{file_path}::{symbol.name}"
                        
                        if node_key not in self.dependency_graph:
                            self.dependency_graph[node_key] = DependencyNode(
                                symbol=symbol.name,
                                file_path=file_path,
                                depends_on=[],
                                depended_by=[],
                                import_count=0,
                                is_external=False
                            )

                        # Add dependencies
                        for dep in symbol.dependencies:
                            dep_key = self._find_symbol(dep)
                            if dep_key:
                                self.dependency_graph[node_key].depends_on.append(dep_key)
                                if dep_key in self.dependency_graph:
                                    self.dependency_graph[dep_key].depended_by.append(node_key)

        except Exception as e:
            logger.error(f"Error building dependency graph: {e}")

    def _find_symbol(self, symbol_name: str) -> Optional[str]:
        """Find symbol in index"""
        for file_path, symbols in self.code_index.items():
            for symbol in symbols:
                if symbol.name == symbol_name:
                    return f"{file_path}::{symbol.name}"
        return None

    async def analyze_dependencies(
        self,
        symbol_name: str,
        file_path: Optional[str] = None
    ) -> Dict:
        """Analyze dependencies for a symbol"""
        try:
            # Find the symbol
            node_key = None
            if file_path:
                node_key = f"{file_path}::{symbol_name}"
            else:
                node_key = self._find_symbol(symbol_name)

            if not node_key or node_key not in self.dependency_graph:
                return {"success": False, "error": "Symbol not found"}

            node = self.dependency_graph[node_key]

            return {
                "success": True,
                "symbol": symbol_name,
                "file_path": node.file_path,
                "depends_on": node.depends_on,
                "depended_by": node.depended_by,
                "dependency_count": len(node.depends_on),
                "dependent_count": len(node.depended_by)
            }

        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {"success": False, "error": str(e)}

    async def impact_analysis(
        self,
        symbol_name: str,
        file_path: Optional[str] = None
    ) -> Dict:
        """Analyze impact of changing a symbol"""
        try:
            node_key = None
            if file_path:
                node_key = f"{file_path}::{symbol_name}"
            else:
                node_key = self._find_symbol(symbol_name)

            if not node_key or node_key not in self.dependency_graph:
                return {"success": False, "error": "Symbol not found"}

            # Find all symbols that would be affected
            affected = set()
            to_visit = [node_key]
            visited = set()

            while to_visit:
                current = to_visit.pop()
                if current in visited:
                    continue
                visited.add(current)

                if current in self.dependency_graph:
                    node = self.dependency_graph[current]
                    for dependent in node.depended_by:
                        affected.add(dependent)
                        to_visit.append(dependent)

            affected_files = set()
            for symbol_key in affected:
                file_path = symbol_key.split("::")[0]
                affected_files.add(file_path)

            return {
                "success": True,
                "symbol": symbol_name,
                "affected_symbols": list(affected),
                "affected_files": list(affected_files),
                "impact_score": len(affected),
                "warning": "Changing this symbol will affect the listed symbols" if affected else "No dependencies found"
            }

        except Exception as e:
            logger.error(f"Error in impact analysis: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Dead Code Detection ====================

    async def detect_dead_code(self, project_path: str) -> Dict:
        """Detect unused functions, classes, and variables"""
        try:
            dead_code = []

            for file_path, symbols in self.code_index.items():
                if not file_path.startswith(project_path):
                    continue

                for symbol in symbols:
                    if symbol.type in ["function", "class"]:
                        node_key = f"{file_path}::{symbol.name}"
                        
                        # Check if symbol is used
                        if node_key in self.dependency_graph:
                            node = self.dependency_graph[node_key]
                            
                            # If nothing depends on it and it's not exported/main
                            if (len(node.depended_by) == 0 and 
                                not symbol.name.startswith('_') and
                                symbol.name not in ['main', '__init__']):
                                
                                dead_code.append({
                                    "symbol": symbol.name,
                                    "type": symbol.type,
                                    "file_path": file_path,
                                    "line_number": symbol.line_number,
                                    "reason": "No references found"
                                })

            return {
                "success": True,
                "dead_code": dead_code,
                "total_found": len(dead_code)
            }

        except Exception as e:
            logger.error(f"Error detecting dead code: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Symbol Navigation ====================

    async def find_definition(self, symbol_name: str) -> Dict:
        """Find definition of a symbol"""
        try:
            matches = []

            for file_path, symbols in self.code_index.items():
                for symbol in symbols:
                    if symbol.name == symbol_name:
                        matches.append({
                            "symbol": symbol.name,
                            "type": symbol.type,
                            "file_path": file_path,
                            "line_number": symbol.line_number,
                            "definition": symbol.definition,
                            "docstring": symbol.docstring
                        })

            return {
                "success": True,
                "matches": matches,
                "total_found": len(matches)
            }

        except Exception as e:
            logger.error(f"Error finding definition: {e}")
            return {"success": False, "error": str(e)}

    async def find_references(self, symbol_name: str) -> Dict:
        """Find all references to a symbol"""
        try:
            node_key = self._find_symbol(symbol_name)
            
            if not node_key or node_key not in self.dependency_graph:
                return {"success": False, "error": "Symbol not found"}

            node = self.dependency_graph[node_key]
            references = []

            # Add symbols that depend on this one
            for dependent in node.depended_by:
                ref_file, ref_symbol = dependent.split("::")
                references.append({
                    "file_path": ref_file,
                    "symbol": ref_symbol,
                    "reference_type": "usage"
                })

            return {
                "success": True,
                "references": references,
                "total_found": len(references)
            }

        except Exception as e:
            logger.error(f"Error finding references: {e}")
            return {"success": False, "error": str(e)}
