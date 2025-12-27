"""
Documentation Generator - Living Documentation System
Automatically generates and maintains comprehensive documentation
"""

import logging
import ast
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class DocGenerator:
    """Living documentation generator with diagram support"""
    
    def __init__(self, gemini_processor=None):
        """
        Initialize documentation generator
        
        Args:
            gemini_processor: Gemini AI processor for enhanced docs
        """
        self.gemini = gemini_processor
        self.doc_cache = {}
        logger.info("Documentation Generator initialized")
    
    async def generate_documentation(
        self,
        project_path: str,
        include_diagrams: bool = True,
        include_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for a project
        
        Args:
            project_path: Path to project directory
            include_diagrams: Whether to generate architecture diagrams
            include_examples: Whether to include usage examples
            
        Returns:
            Documentation object with markdown content and metadata
        """
        try:
            logger.info(f"Generating documentation for {project_path}")
            
            project_path = Path(project_path)
            
            # Scan project files
            files = self._scan_project_files(project_path)
            
            # Extract documentation from files
            api_docs = await self._extract_api_documentation(files)
            
            # Generate architecture diagrams
            diagrams = {}
            if include_diagrams:
                diagrams = await self._generate_diagrams(files, api_docs)
            
            # Generate usage examples
            examples = {}
            if include_examples:
                examples = await self._generate_examples(api_docs)
            
            # Build complete documentation
            documentation = {
                "project_name": project_path.name,
                "project_path": str(project_path),
                "api_reference": api_docs,
                "diagrams": diagrams,
                "examples": examples,
                "markdown": self._build_markdown_documentation(
                    project_path.name, api_docs, diagrams, examples
                ),
                "generated_at": self._get_timestamp()
            }
            
            return documentation
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return {
                "error": str(e)
            }
    
    def _scan_project_files(self, project_path: Path) -> List[Dict[str, Any]]:
        """Scan project for Python files"""
        
        files = []
        
        # Supported file extensions
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        
        for ext in extensions:
            for file_path in project_path.rglob(f'*{ext}'):
                # Skip common directories
                if any(skip in file_path.parts for skip in ['venv', 'node_modules', '__pycache__', '.git']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    files.append({
                        "path": str(file_path),
                        "relative_path": str(file_path.relative_to(project_path)),
                        "language": self._detect_language(file_path.suffix),
                        "content": content
                    })
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        return files
    
    def _detect_language(self, extension: str) -> str:
        """Detect language from file extension"""
        mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript'
        }
        return mapping.get(extension, 'unknown')
    
    async def _extract_api_documentation(
        self, files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract API documentation from files"""
        
        api_docs = {
            "modules": [],
            "classes": [],
            "functions": [],
            "constants": []
        }
        
        for file_info in files:
            if file_info["language"] == "python":
                docs = self._extract_python_docs(file_info)
                api_docs["modules"].append(docs)
        
        return api_docs
    
    def _extract_python_docs(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract documentation from Python file"""
        
        module_doc = {
            "file": file_info["relative_path"],
            "docstring": "",
            "classes": [],
            "functions": [],
            "imports": []
        }
        
        try:
            tree = ast.parse(file_info["content"])
            
            # Module docstring
            module_doc["docstring"] = ast.get_docstring(tree) or ""
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = self._extract_class_doc(node)
                    module_doc["classes"].append(class_doc)
                
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        func_doc = self._extract_function_doc(node)
                        module_doc["functions"].append(func_doc)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._extract_import(node)
                    module_doc["imports"].append(import_info)
        
        except Exception as e:
            logger.error(f"Error parsing {file_info['path']}: {e}")
        
        return module_doc
    
    def _extract_class_doc(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract documentation from class node"""
        
        class_doc = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": [],
            "attributes": [],
            "bases": [self._get_name(base) for base in node.bases]
        }
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._extract_function_doc(item)
                class_doc["methods"].append(method_doc)
            
            elif isinstance(item, ast.AnnAssign):
                # Class attributes with type hints
                if isinstance(item.target, ast.Name):
                    class_doc["attributes"].append({
                        "name": item.target.id,
                        "type": self._get_annotation(item.annotation)
                    })
        
        return class_doc
    
    def _extract_function_doc(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract documentation from function node"""
        
        func_doc = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "parameters": [],
            "return_type": self._get_annotation(node.returns) if node.returns else None,
            "decorators": [self._get_name(dec) for dec in node.decorator_list]
        }
        
        # Extract parameters
        for arg in node.args.args:
            param = {
                "name": arg.arg,
                "type": self._get_annotation(arg.annotation) if arg.annotation else None,
                "default": None
            }
            func_doc["parameters"].append(param)
        
        # Extract defaults
        defaults = node.args.defaults
        if defaults:
            # Defaults apply to the last N parameters
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                param_index = len(func_doc["parameters"]) - num_defaults + i
                func_doc["parameters"][param_index]["default"] = ast.unparse(default)
        
        return func_doc
    
    def _extract_import(self, node) -> str:
        """Extract import statement"""
        return ast.unparse(node)
    
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return ast.unparse(node)
    
    def _get_annotation(self, node) -> str:
        """Get type annotation as string"""
        if node is None:
            return None
        return ast.unparse(node)
    
    async def _generate_diagrams(
        self, files: List[Dict[str, Any]], api_docs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate Mermaid architecture diagrams"""
        
        diagrams = {}
        
        # Class diagram
        diagrams["class_diagram"] = self._generate_class_diagram(api_docs)
        
        # Module dependency diagram
        diagrams["dependency_diagram"] = self._generate_dependency_diagram(api_docs)
        
        return diagrams
    
    def _generate_class_diagram(self, api_docs: Dict[str, Any]) -> str:
        """Generate Mermaid class diagram"""
        
        mermaid = ["classDiagram"]
        
        for module in api_docs["modules"]:
            for class_info in module["classes"]:
                class_name = class_info["name"]
                
                # Add class
                mermaid.append(f"    class {class_name} {{")
                
                # Add attributes
                for attr in class_info["attributes"]:
                    attr_type = attr.get("type", "Any")
                    mermaid.append(f"        +{attr['name']}: {attr_type}")
                
                # Add methods
                for method in class_info["methods"]:
                    params = ", ".join([p["name"] for p in method["parameters"]])
                    return_type = method.get("return_type", "None")
                    mermaid.append(f"        +{method['name']}({params}): {return_type}")
                
                mermaid.append("    }")
                
                # Add inheritance
                for base in class_info["bases"]:
                    if base != "object":
                        mermaid.append(f"    {base} <|-- {class_name}")
        
        return "\n".join(mermaid)
    
    def _generate_dependency_diagram(self, api_docs: Dict[str, Any]) -> str:
        """Generate module dependency diagram"""
        
        mermaid = ["graph TD"]
        
        for i, module in enumerate(api_docs["modules"]):
            module_name = Path(module["file"]).stem
            node_id = f"M{i}"
            
            mermaid.append(f"    {node_id}[{module_name}]")
            
            # Add dependencies based on imports
            for import_stmt in module["imports"]:
                # Simple extraction of module names
                if "import" in import_stmt:
                    imported = re.findall(r'import\s+(\w+)', import_stmt)
                    for imp in imported:
                        mermaid.append(f"    {node_id} --> {imp}")
        
        return "\n".join(mermaid)
    
    async def _generate_examples(
        self, api_docs: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate usage examples using AI"""
        
        if not self.gemini:
            return {}
        
        examples = {}
        
        try:
            # Generate examples for key functions/classes
            for module in api_docs["modules"][:3]:  # Limit to first 3 modules
                for func in module["functions"][:2]:  # First 2 functions per module
                    example = await self._generate_function_example(func)
                    if example:
                        examples[func["name"]] = example
        
        except Exception as e:
            logger.error(f"Error generating examples: {e}")
        
        return examples
    
    async def _generate_function_example(self, func_doc: Dict[str, Any]) -> Optional[str]:
        """Generate usage example for a function"""
        
        try:
            prompt = f"""Generate a simple usage example for this Python function:

Function: {func_doc['name']}
Parameters: {', '.join([p['name'] for p in func_doc['parameters']])}
Docstring: {func_doc['docstring']}

Provide a short code example showing how to use this function.
Format as a Python code block."""
            
            response = await self.gemini.generate_content(prompt)
            
            # Extract code block
            match = re.search(r'```python\s*\n(.*?)```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating example: {e}")
            return None
    
    def _build_markdown_documentation(
        self,
        project_name: str,
        api_docs: Dict[str, Any],
        diagrams: Dict[str, str],
        examples: Dict[str, List[str]]
    ) -> str:
        """Build complete markdown documentation"""
        
        md = [f"# {project_name} - API Documentation\n"]
        md.append(f"*Generated: {self._get_timestamp()}*\n")
        
        # Table of contents
        md.append("## Table of Contents\n")
        md.append("- [Architecture](#architecture)")
        md.append("- [API Reference](#api-reference)")
        md.append("- [Examples](#examples)\n")
        
        # Architecture section
        if diagrams:
            md.append("## Architecture\n")
            
            if "class_diagram" in diagrams:
                md.append("### Class Diagram\n")
                md.append("```mermaid")
                md.append(diagrams["class_diagram"])
                md.append("```\n")
            
            if "dependency_diagram" in diagrams:
                md.append("### Module Dependencies\n")
                md.append("```mermaid")
                md.append(diagrams["dependency_diagram"])
                md.append("```\n")
        
        # API Reference
        md.append("## API Reference\n")
        
        for module in api_docs["modules"]:
            md.append(f"### {module['file']}\n")
            
            if module["docstring"]:
                md.append(f"{module['docstring']}\n")
            
            # Classes
            for class_info in module["classes"]:
                md.append(f"#### Class: `{class_info['name']}`\n")
                
                if class_info["docstring"]:
                    md.append(f"{class_info['docstring']}\n")
                
                # Methods
                if class_info["methods"]:
                    md.append("**Methods:**\n")
                    for method in class_info["methods"]:
                        params = ", ".join([
                            f"{p['name']}: {p.get('type', 'Any')}" 
                            for p in method["parameters"]
                        ])
                        md.append(f"- `{method['name']}({params})`")
                        if method["docstring"]:
                            md.append(f"  - {method['docstring']}")
                    md.append("")
            
            # Functions
            for func in module["functions"]:
                params = ", ".join([
                    f"{p['name']}: {p.get('type', 'Any')}" 
                    for p in func["parameters"]
                ])
                md.append(f"#### Function: `{func['name']}({params})`\n")
                
                if func["docstring"]:
                    md.append(f"{func['docstring']}\n")
        
        # Examples
        if examples:
            md.append("## Examples\n")
            for func_name, example in examples.items():
                md.append(f"### {func_name}\n")
                md.append("```python")
                md.append(example)
                md.append("```\n")
        
        return "\n".join(md)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generator statistics"""
        return {
            "cache_size": len(self.doc_cache),
            "has_gemini": self.gemini is not None
        }
