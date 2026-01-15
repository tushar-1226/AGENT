"""
Visual Programming Module
Drag-and-drop workflow builder, flowchart to code, visual API designer
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of visual programming nodes"""
    START = "start"
    END = "end"
    FUNCTION = "function"
    CONDITION = "condition"
    LOOP = "loop"
    API_CALL = "api_call"
    DATABASE = "database"
    VARIABLE = "variable"
    INPUT = "input"
    OUTPUT = "output"
    CUSTOM = "custom"


class ConnectionType(Enum):
    """Types of connections between nodes"""
    SEQUENTIAL = "sequential"
    CONDITIONAL_TRUE = "conditional_true"
    CONDITIONAL_FALSE = "conditional_false"
    LOOP_BODY = "loop_body"
    ERROR_HANDLER = "error_handler"


@dataclass
class FlowNode:
    """Represents a node in visual workflow"""
    id: str
    type: str
    label: str
    position: Dict[str, float]  # x, y coordinates
    config: Dict[str, Any]
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class FlowConnection:
    """Represents a connection between nodes"""
    id: str
    source_node: str
    target_node: str
    source_port: str
    target_port: str
    connection_type: str


@dataclass
class VisualWorkflow:
    """Represents a complete visual workflow"""
    workflow_id: str
    name: str
    description: str
    nodes: List[FlowNode]
    connections: List[FlowConnection]
    created_at: float
    updated_at: float
    metadata: Dict[str, Any]


class VisualProgramming:
    """
    Visual Programming Interface:
    - Drag-and-drop workflow builder
    - Flowchart to code conversion
    - Visual API endpoint designer
    - Database schema visual editor
    """

    def __init__(self, llm_processor=None):
        self.llm = llm_processor
        self.workflows: Dict[str, VisualWorkflow] = {}
        self.templates: Dict[str, Dict] = self._load_templates()
        logger.info("Visual Programming module initialized")

    def _load_templates(self) -> Dict[str, Dict]:
        """Load pre-built workflow templates"""
        return {
            "rest_api": {
                "name": "REST API Endpoint",
                "description": "Basic REST API with CRUD operations",
                "nodes": [
                    {"type": "start", "label": "API Request"},
                    {"type": "condition", "label": "Auth Check"},
                    {"type": "database", "label": "DB Query"},
                    {"type": "function", "label": "Transform Data"},
                    {"type": "output", "label": "JSON Response"}
                ]
            },
            "data_pipeline": {
                "name": "Data Processing Pipeline",
                "description": "ETL pipeline for data processing",
                "nodes": [
                    {"type": "input", "label": "Data Source"},
                    {"type": "function", "label": "Extract"},
                    {"type": "function", "label": "Transform"},
                    {"type": "database", "label": "Load"},
                    {"type": "output", "label": "Success"}
                ]
            },
            "webhook_handler": {
                "name": "Webhook Handler",
                "description": "Process incoming webhooks",
                "nodes": [
                    {"type": "start", "label": "Webhook Received"},
                    {"type": "function", "label": "Validate Payload"},
                    {"type": "condition", "label": "Check Event Type"},
                    {"type": "api_call", "label": "External API"},
                    {"type": "database", "label": "Store Event"},
                    {"type": "output", "label": "ACK Response"}
                ]
            }
        }

    # ==================== Workflow Management ====================

    async def create_workflow(
        self,
        name: str,
        description: str,
        template: Optional[str] = None
    ) -> Dict:
        """Create a new visual workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Load from template if specified
            nodes = []
            connections = []
            
            if template and template in self.templates:
                template_data = self.templates[template]
                nodes = self._create_nodes_from_template(template_data["nodes"])
                connections = self._create_connections_from_template(nodes)

            workflow = VisualWorkflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                nodes=nodes,
                connections=connections,
                created_at=datetime.now().timestamp(),
                updated_at=datetime.now().timestamp(),
                metadata={
                    "template": template,
                    "version": "1.0.0",
                    "language": "python"
                }
            )

            self.workflows[workflow_id] = workflow

            return {
                "success": True,
                "workflow_id": workflow_id,
                "workflow": asdict(workflow)
            }

        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {"success": False, "error": str(e)}

    def _create_nodes_from_template(self, template_nodes: List[Dict]) -> List[FlowNode]:
        """Create flow nodes from template"""
        nodes = []
        y_position = 100
        
        for i, node_def in enumerate(template_nodes):
            node = FlowNode(
                id=f"node_{i}",
                type=node_def["type"],
                label=node_def["label"],
                position={"x": 300, "y": y_position},
                config=node_def.get("config", {}),
                inputs=["input"] if i > 0 else [],
                outputs=["output"] if i < len(template_nodes) - 1 else []
            )
            nodes.append(node)
            y_position += 150

        return nodes

    def _create_connections_from_template(self, nodes: List[FlowNode]) -> List[FlowConnection]:
        """Create connections between template nodes"""
        connections = []
        
        for i in range(len(nodes) - 1):
            connection = FlowConnection(
                id=f"conn_{i}",
                source_node=nodes[i].id,
                target_node=nodes[i + 1].id,
                source_port="output",
                target_port="input",
                connection_type=ConnectionType.SEQUENTIAL.value
            )
            connections.append(connection)

        return connections

    async def add_node(
        self,
        workflow_id: str,
        node_type: str,
        label: str,
        position: Dict[str, float],
        config: Optional[Dict] = None
    ) -> Dict:
        """Add a node to workflow"""
        try:
            if workflow_id not in self.workflows:
                return {"success": False, "error": "Workflow not found"}

            workflow = self.workflows[workflow_id]
            
            node_id = f"node_{len(workflow.nodes)}"
            node = FlowNode(
                id=node_id,
                type=node_type,
                label=label,
                position=position,
                config=config or {},
                inputs=["input"] if node_type != NodeType.START.value else [],
                outputs=["output"] if node_type != NodeType.END.value else []
            )

            workflow.nodes.append(node)
            workflow.updated_at = datetime.now().timestamp()

            return {
                "success": True,
                "node_id": node_id,
                "node": asdict(node)
            }

        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return {"success": False, "error": str(e)}

    async def connect_nodes(
        self,
        workflow_id: str,
        source_node: str,
        target_node: str,
        connection_type: str = "sequential"
    ) -> Dict:
        """Connect two nodes in workflow"""
        try:
            if workflow_id not in self.workflows:
                return {"success": False, "error": "Workflow not found"}

            workflow = self.workflows[workflow_id]
            
            connection_id = f"conn_{len(workflow.connections)}"
            connection = FlowConnection(
                id=connection_id,
                source_node=source_node,
                target_node=target_node,
                source_port="output",
                target_port="input",
                connection_type=connection_type
            )

            workflow.connections.append(connection)
            workflow.updated_at = datetime.now().timestamp()

            return {
                "success": True,
                "connection_id": connection_id,
                "connection": asdict(connection)
            }

        except Exception as e:
            logger.error(f"Error connecting nodes: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Code Generation ====================

    async def generate_code(
        self,
        workflow_id: str,
        language: str = "python",
        framework: Optional[str] = None
    ) -> Dict:
        """Generate code from visual workflow"""
        try:
            if workflow_id not in self.workflows:
                return {"success": False, "error": "Workflow not found"}

            workflow = self.workflows[workflow_id]

            if language == "python":
                code = await self._generate_python_code(workflow, framework)
            elif language == "javascript":
                code = await self._generate_javascript_code(workflow, framework)
            elif language == "typescript":
                code = await self._generate_typescript_code(workflow, framework)
            else:
                return {"success": False, "error": f"Unsupported language: {language}"}

            return {
                "success": True,
                "code": code,
                "language": language,
                "framework": framework
            }

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_python_code(
        self,
        workflow: VisualWorkflow,
        framework: Optional[str]
    ) -> str:
        """Generate Python code from workflow"""
        code_parts = []
        
        # Add imports
        code_parts.append("# Generated by FRIDAY Visual Programming")
        code_parts.append("# Workflow: " + workflow.name)
        code_parts.append("")
        code_parts.append("import asyncio")
        code_parts.append("import logging")
        code_parts.append("from typing import Dict, Any")
        code_parts.append("")
        
        if framework == "fastapi":
            code_parts.append("from fastapi import APIRouter, HTTPException")
            code_parts.append("from pydantic import BaseModel")
            code_parts.append("")
            code_parts.append("router = APIRouter()")
            code_parts.append("")

        # Generate main function
        function_name = workflow.name.lower().replace(" ", "_")
        code_parts.append(f"async def {function_name}(data: Dict[str, Any]) -> Dict[str, Any]:")
        code_parts.append('    """')
        code_parts.append(f"    {workflow.description}")
        code_parts.append('    """')
        code_parts.append("    try:")
        
        # Process nodes in execution order
        execution_order = self._get_execution_order(workflow)
        
        for node in execution_order:
            node_code = self._generate_node_code(node, "python")
            code_parts.extend([f"        {line}" for line in node_code.split("\n")])
            code_parts.append("")

        code_parts.append("        return {'success': True, 'result': result}")
        code_parts.append("    except Exception as e:")
        code_parts.append("        logging.error(f'Error in workflow: {e}')")
        code_parts.append("        return {'success': False, 'error': str(e)}")
        code_parts.append("")

        # Add FastAPI endpoint if using framework
        if framework == "fastapi":
            code_parts.append("class WorkflowRequest(BaseModel):")
            code_parts.append("    data: Dict[str, Any]")
            code_parts.append("")
            code_parts.append(f"@router.post('/{function_name}')")
            code_parts.append(f"async def {function_name}_endpoint(request: WorkflowRequest):")
            code_parts.append(f"    result = await {function_name}(request.data)")
            code_parts.append("    if not result['success']:")
            code_parts.append("        raise HTTPException(status_code=500, detail=result['error'])")
            code_parts.append("    return result")

        return "\n".join(code_parts)

    async def _generate_javascript_code(
        self,
        workflow: VisualWorkflow,
        framework: Optional[str]
    ) -> str:
        """Generate JavaScript code from workflow"""
        code_parts = []
        
        code_parts.append("// Generated by FRIDAY Visual Programming")
        code_parts.append(f"// Workflow: {workflow.name}")
        code_parts.append("")
        
        if framework == "express":
            code_parts.append("const express = require('express');")
            code_parts.append("const router = express.Router();")
            code_parts.append("")

        function_name = workflow.name.replace(" ", "_").lower()
        code_parts.append(f"async function {function_name}(data) {{")
        code_parts.append(f"  // {workflow.description}")
        code_parts.append("  try {")
        
        execution_order = self._get_execution_order(workflow)
        for node in execution_order:
            node_code = self._generate_node_code(node, "javascript")
            code_parts.extend([f"    {line}" for line in node_code.split("\n")])
        
        code_parts.append("    return { success: true, result };")
        code_parts.append("  } catch (error) {")
        code_parts.append("    console.error('Error in workflow:', error);")
        code_parts.append("    return { success: false, error: error.message };")
        code_parts.append("  }")
        code_parts.append("}")
        code_parts.append("")

        if framework == "express":
            code_parts.append(f"router.post('/{function_name}', async (req, res) => {{")
            code_parts.append(f"  const result = await {function_name}(req.body);")
            code_parts.append("  if (!result.success) {")
            code_parts.append("    return res.status(500).json(result);")
            code_parts.append("  }")
            code_parts.append("  res.json(result);")
            code_parts.append("});")
            code_parts.append("")
            code_parts.append("module.exports = router;")

        return "\n".join(code_parts)

    async def _generate_typescript_code(
        self,
        workflow: VisualWorkflow,
        framework: Optional[str]
    ) -> str:
        """Generate TypeScript code from workflow"""
        code_parts = []
        
        code_parts.append("// Generated by FRIDAY Visual Programming")
        code_parts.append(f"// Workflow: {workflow.name}")
        code_parts.append("")
        code_parts.append("interface WorkflowData {")
        code_parts.append("  [key: string]: any;")
        code_parts.append("}")
        code_parts.append("")
        code_parts.append("interface WorkflowResult {")
        code_parts.append("  success: boolean;")
        code_parts.append("  result?: any;")
        code_parts.append("  error?: string;")
        code_parts.append("}")
        code_parts.append("")

        function_name = workflow.name.replace(" ", "_").lower()
        code_parts.append(f"async function {function_name}(data: WorkflowData): Promise<WorkflowResult> {{")
        code_parts.append(f"  // {workflow.description}")
        code_parts.append("  try {")
        
        execution_order = self._get_execution_order(workflow)
        for node in execution_order:
            node_code = self._generate_node_code(node, "typescript")
            code_parts.extend([f"    {line}" for line in node_code.split("\n")])
        
        code_parts.append("    return { success: true, result };")
        code_parts.append("  } catch (error) {")
        code_parts.append("    console.error('Error in workflow:', error);")
        code_parts.append("    return { success: false, error: (error as Error).message };")
        code_parts.append("  }")
        code_parts.append("}")
        code_parts.append("")
        code_parts.append(f"export {{ {function_name} }};")

        return "\n".join(code_parts)

    def _generate_node_code(self, node: FlowNode, language: str) -> str:
        """Generate code for a single node"""
        if language == "python":
            return self._generate_python_node_code(node)
        elif language in ["javascript", "typescript"]:
            return self._generate_js_node_code(node, language)
        return ""

    def _generate_python_node_code(self, node: FlowNode) -> str:
        """Generate Python code for a node"""
        if node.type == NodeType.FUNCTION.value:
            func_name = node.config.get("function", "process_data")
            return f"result = await {func_name}(data)"
        
        elif node.type == NodeType.CONDITION.value:
            condition = node.config.get("condition", "True")
            return f"if {condition}:\n    # True branch\n    pass\nelse:\n    # False branch\n    pass"
        
        elif node.type == NodeType.LOOP.value:
            iterator = node.config.get("iterator", "items")
            return f"for item in {iterator}:\n    # Process item\n    pass"
        
        elif node.type == NodeType.API_CALL.value:
            url = node.config.get("url", "https://api.example.com")
            method = node.config.get("method", "GET")
            return f"import aiohttp\nasync with aiohttp.ClientSession() as session:\n    async with session.{method.lower()}('{url}') as response:\n        result = await response.json()"
        
        elif node.type == NodeType.DATABASE.value:
            query = node.config.get("query", "SELECT * FROM table")
            return f"# Database query\nresult = await db.execute('{query}')"
        
        elif node.type == NodeType.VARIABLE.value:
            var_name = node.config.get("name", "variable")
            var_value = node.config.get("value", "None")
            return f"{var_name} = {var_value}"
        
        elif node.type == NodeType.OUTPUT.value:
            return "# Return result\nreturn result"
        
        return f"# {node.label}\npass"

    def _generate_js_node_code(self, node: FlowNode, language: str) -> str:
        """Generate JavaScript/TypeScript code for a node"""
        if node.type == NodeType.FUNCTION.value:
            func_name = node.config.get("function", "processData")
            return f"const result = await {func_name}(data);"
        
        elif node.type == NodeType.CONDITION.value:
            condition = node.config.get("condition", "true")
            return f"if ({condition}) {{\n  // True branch\n}} else {{\n  // False branch\n}}"
        
        elif node.type == NodeType.API_CALL.value:
            url = node.config.get("url", "https://api.example.com")
            return f"const response = await fetch('{url}');\nconst result = await response.json();"
        
        elif node.type == NodeType.VARIABLE.value:
            var_name = node.config.get("name", "variable")
            var_value = node.config.get("value", "null")
            const_or_let = "const" if language == "typescript" else "let"
            return f"{const_or_let} {var_name} = {var_value};"
        
        return f"// {node.label}"

    def _get_execution_order(self, workflow: VisualWorkflow) -> List[FlowNode]:
        """Determine execution order of nodes using topological sort"""
        # Build adjacency list
        graph = {node.id: [] for node in workflow.nodes}
        in_degree = {node.id: 0 for node in workflow.nodes}
        node_map = {node.id: node for node in workflow.nodes}
        
        for conn in workflow.connections:
            graph[conn.source_node].append(conn.target_node)
            in_degree[conn.target_node] += 1
        
        # Find start nodes (in_degree == 0)
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(node_map[current])
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return execution_order

    # ==================== Visual API Designer ====================

    async def design_api_endpoint(
        self,
        endpoint_name: str,
        method: str,
        path: str,
        workflow_id: Optional[str] = None
    ) -> Dict:
        """Design a visual API endpoint"""
        try:
            # Create workflow for API endpoint
            if not workflow_id:
                workflow_result = await self.create_workflow(
                    name=endpoint_name,
                    description=f"{method} {path}",
                    template="rest_api"
                )
                workflow_id = workflow_result["workflow_id"]

            api_spec = {
                "endpoint_name": endpoint_name,
                "method": method,
                "path": path,
                "workflow_id": workflow_id,
                "parameters": [],
                "request_body": {},
                "responses": {
                    "200": {"description": "Success"},
                    "400": {"description": "Bad Request"},
                    "500": {"description": "Internal Server Error"}
                }
            }

            return {
                "success": True,
                "api_spec": api_spec,
                "workflow_id": workflow_id
            }

        except Exception as e:
            logger.error(f"Error designing API endpoint: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Database Schema Editor ====================

    async def design_database_schema(
        self,
        schema_name: str,
        tables: List[Dict]
    ) -> Dict:
        """Visual database schema design"""
        try:
            schema = {
                "schema_name": schema_name,
                "tables": [],
                "relationships": []
            }

            for table_def in tables:
                table = {
                    "name": table_def["name"],
                    "columns": table_def.get("columns", []),
                    "primary_key": table_def.get("primary_key"),
                    "indexes": table_def.get("indexes", [])
                }
                schema["tables"].append(table)

            # Generate SQL
            sql = self._generate_sql_from_schema(schema)

            return {
                "success": True,
                "schema": schema,
                "sql": sql
            }

        except Exception as e:
            logger.error(f"Error designing database schema: {e}")
            return {"success": False, "error": str(e)}

    def _generate_sql_from_schema(self, schema: Dict) -> str:
        """Generate SQL CREATE TABLE statements from schema"""
        sql_parts = []
        
        sql_parts.append(f"-- Database Schema: {schema['schema_name']}")
        sql_parts.append("")

        for table in schema["tables"]:
            sql_parts.append(f"CREATE TABLE {table['name']} (")
            
            columns = []
            for col in table["columns"]:
                col_def = f"  {col['name']} {col['type']}"
                if col.get("not_null"):
                    col_def += " NOT NULL"
                if col.get("unique"):
                    col_def += " UNIQUE"
                if col.get("default"):
                    col_def += f" DEFAULT {col['default']}"
                columns.append(col_def)
            
            if table.get("primary_key"):
                columns.append(f"  PRIMARY KEY ({table['primary_key']})")
            
            sql_parts.append(",\n".join(columns))
            sql_parts.append(");")
            sql_parts.append("")

        return "\n".join(sql_parts)

    # ==================== Import/Export ====================

    async def export_workflow(self, workflow_id: str, format: str = "json") -> Dict:
        """Export workflow to various formats"""
        try:
            if workflow_id not in self.workflows:
                return {"success": False, "error": "Workflow not found"}

            workflow = self.workflows[workflow_id]

            if format == "json":
                exported = json.dumps(asdict(workflow), indent=2)
            elif format == "yaml":
                # Would require PyYAML
                exported = "# YAML export not implemented"
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}

            return {
                "success": True,
                "format": format,
                "data": exported
            }

        except Exception as e:
            logger.error(f"Error exporting workflow: {e}")
            return {"success": False, "error": str(e)}

    async def import_workflow(self, workflow_data: str, format: str = "json") -> Dict:
        """Import workflow from file"""
        try:
            if format == "json":
                data = json.loads(workflow_data)
                workflow_id = data["workflow_id"]
                
                # Reconstruct workflow objects
                nodes = [FlowNode(**node) for node in data["nodes"]]
                connections = [FlowConnection(**conn) for conn in data["connections"]]
                
                workflow = VisualWorkflow(
                    workflow_id=workflow_id,
                    name=data["name"],
                    description=data["description"],
                    nodes=nodes,
                    connections=connections,
                    created_at=data["created_at"],
                    updated_at=datetime.now().timestamp(),
                    metadata=data.get("metadata", {})
                )
                
                self.workflows[workflow_id] = workflow

                return {
                    "success": True,
                    "workflow_id": workflow_id
                }

        except Exception as e:
            logger.error(f"Error importing workflow: {e}")
            return {"success": False, "error": str(e)}

    # ==================== Utilities ====================

    async def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow by ID"""
        try:
            if workflow_id not in self.workflows:
                return {"success": False, "error": "Workflow not found"}

            return {
                "success": True,
                "workflow": asdict(self.workflows[workflow_id])
            }

        except Exception as e:
            logger.error(f"Error getting workflow: {e}")
            return {"success": False, "error": str(e)}

    async def list_workflows(self) -> Dict:
        """List all workflows"""
        try:
            workflows = [
                {
                    "workflow_id": wf.workflow_id,
                    "name": wf.name,
                    "description": wf.description,
                    "nodes_count": len(wf.nodes),
                    "updated_at": wf.updated_at
                }
                for wf in self.workflows.values()
            ]

            return {
                "success": True,
                "workflows": workflows,
                "total": len(workflows)
            }

        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return {"success": False, "error": str(e)}

    async def get_templates(self) -> Dict:
        """Get available workflow templates"""
        return {
            "success": True,
            "templates": self.templates
        }
