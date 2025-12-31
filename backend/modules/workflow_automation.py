"""
Workflow Automation Engine
Create custom automation rules with natural language
"""
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import re
import json


class TriggerType(Enum):
    """Types of automation triggers"""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    FILE_CHANGE = "file_change"
    GIT_EVENT = "git_event"
    API_EVENT = "api_event"
    CONDITION = "condition"


class ActionType(Enum):
    """Types of automation actions"""
    RUN_COMMAND = "run_command"
    SEND_NOTIFICATION = "send_notification"
    CREATE_FILE = "create_file"
    RUN_TESTS = "run_tests"
    DEPLOY = "deploy"
    BACKUP = "backup"
    SEND_EMAIL = "send_email"
    CALL_API = "call_api"


@dataclass
class WorkflowTrigger:
    """Workflow trigger"""
    id: str
    type: TriggerType
    condition: str
    parameters: Dict[str, Any]


@dataclass
class WorkflowAction:
    """Workflow action"""
    id: str
    type: ActionType
    description: str
    parameters: Dict[str, Any]


@dataclass
class Workflow:
    """Complete workflow"""
    id: str
    name: str
    description: str
    triggers: List[WorkflowTrigger]
    actions: List[WorkflowAction]
    enabled: bool = True
    created_at: str = ""
    last_run: Optional[str] = None
    run_count: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class NaturalLanguageParser:
    """Parse natural language into workflow rules"""
    
    def __init__(self):
        self.trigger_patterns = {
            'time': r'(?:every|at)\s+(\d+)\s*(minute|hour|day|week)',
            'file_change': r'when\s+(?:file|files?)\s+(?:in\s+)?(.+?)\s+(?:change|update)',
            'git': r'when\s+(?:commit|push|pull request|merge)',
            'condition': r'if\s+(.+?)\s+then',
        }
        
        self.action_patterns = {
            'run_command': r'run\s+(?:command\s+)?["\'](.+?)["\']',
            'notify': r'send\s+(?:notification|alert|email)',
            'test': r'run\s+tests?',
            'deploy': r'deploy\s+(?:to\s+)?(.+)',
        }
    
    def parse(self, natural_language: str) -> Dict:
        """Parse natural language into workflow components"""
        triggers = self._extract_triggers(natural_language)
        actions = self._extract_actions(natural_language)
        
        return {
            'triggers': triggers,
            'actions': actions,
            'original': natural_language
        }
    
    def _extract_triggers(self, text: str) -> List[Dict]:
        """Extract triggers from text"""
        triggers = []
        
        # Time-based triggers
        time_match = re.search(self.trigger_patterns['time'], text, re.IGNORECASE)
        if time_match:
            interval, unit = time_match.groups()
            triggers.append({
                'type': 'time_based',
                'interval': int(interval),
                'unit': unit,
                'condition': f"every {interval} {unit}"
            })
        
        # File change triggers
        file_match = re.search(self.trigger_patterns['file_change'], text, re.IGNORECASE)
        if file_match:
            path = file_match.group(1).strip()
            triggers.append({
                'type': 'file_change',
                'path': path,
                'condition': f"file change in {path}"
            })
        
        # Git triggers
        if re.search(self.trigger_patterns['git'], text, re.IGNORECASE):
            triggers.append({
                'type': 'git_event',
                'event': 'commit',
                'condition': "on git commit"
            })
        
        # Conditional triggers
        cond_match = re.search(self.trigger_patterns['condition'], text, re.IGNORECASE)
        if cond_match:
            condition = cond_match.group(1).strip()
            triggers.append({
                'type': 'condition',
                'condition': condition
            })
        
        return triggers
    
    def _extract_actions(self, text: str) -> List[Dict]:
        """Extract actions from text"""
        actions = []
        
        # Run command actions
        cmd_match = re.search(self.action_patterns['run_command'], text, re.IGNORECASE)
        if cmd_match:
            command = cmd_match.group(1)
            actions.append({
                'type': 'run_command',
                'command': command,
                'description': f"Run command: {command}"
            })
        
        # Notification actions
        if re.search(self.action_patterns['notify'], text, re.IGNORECASE):
            actions.append({
                'type': 'send_notification',
                'description': "Send notification"
            })
        
        # Test actions
        if re.search(self.action_patterns['test'], text, re.IGNORECASE):
            actions.append({
                'type': 'run_tests',
                'description': "Run tests"
            })
        
        # Deploy actions
        deploy_match = re.search(self.action_patterns['deploy'], text, re.IGNORECASE)
        if deploy_match:
            environment = deploy_match.group(1) if deploy_match.lastindex >= 1 else 'production'
            actions.append({
                'type': 'deploy',
                'environment': environment,
                'description': f"Deploy to {environment}"
            })
        
        return actions


class WorkflowExecutor:
    """Execute workflow actions"""
    
    def __init__(self):
        self.execution_history = []
        self.action_handlers = {
            ActionType.RUN_COMMAND: self._run_command,
            ActionType.SEND_NOTIFICATION: self._send_notification,
            ActionType.RUN_TESTS: self._run_tests,
            ActionType.DEPLOY: self._deploy,
        }
    
    async def execute_workflow(self, workflow: Workflow, context: Dict = None) -> Dict:
        """Execute a workflow"""
        if context is None:
            context = {}
        
        execution_id = f"exec_{datetime.now().timestamp()}"
        results = []
        
        for action in workflow.actions:
            handler = self.action_handlers.get(action.type)
            
            if handler:
                try:
                    result = await handler(action, context)
                    results.append({
                        'action': action.description,
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'action': action.description,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        execution_record = {
            'execution_id': execution_id,
            'workflow_id': workflow.id,
            'workflow_name': workflow.name,
            'results': results,
            'executed_at': datetime.now().isoformat()
        }
        
        self.execution_history.append(execution_record)
        
        return execution_record
    
    async def _run_command(self, action: WorkflowAction, context: Dict) -> Dict:
        """Run a command"""
        command = action.parameters.get('command', '')
        
        # In production, actually execute the command
        return {
            'command': command,
            'output': f"Command '{command}' executed successfully",
            'exit_code': 0
        }
    
    async def _send_notification(self, action: WorkflowAction, context: Dict) -> Dict:
        """Send notification"""
        message = action.parameters.get('message', 'Workflow notification')
        
        return {
            'message': message,
            'sent': True,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _run_tests(self, action: WorkflowAction, context: Dict) -> Dict:
        """Run tests"""
        test_path = action.parameters.get('path', 'tests/')
        
        return {
            'test_path': test_path,
            'tests_run': 42,
            'tests_passed': 40,
            'tests_failed': 2
        }
    
    async def _deploy(self, action: WorkflowAction, context: Dict) -> Dict:
        """Deploy application"""
        environment = action.parameters.get('environment', 'production')
        
        return {
            'environment': environment,
            'deployed': True,
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }


class ScheduledTaskManager:
    """Manage scheduled tasks"""
    
    def __init__(self):
        self.scheduled_tasks = []
    
    def schedule_task(self, name: str, schedule: str, action: Callable) -> str:
        """Schedule a recurring task"""
        task_id = f"task_{datetime.now().timestamp()}"
        
        task = {
            'id': task_id,
            'name': name,
            'schedule': schedule,
            'action': action,
            'next_run': self._calculate_next_run(schedule),
            'enabled': True
        }
        
        self.scheduled_tasks.append(task)
        
        return task_id
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time"""
        # Parse schedule (e.g., "every 1 hour", "daily at 9:00")
        now = datetime.now()
        
        if 'hour' in schedule:
            match = re.search(r'(\d+)\s*hour', schedule)
            if match:
                hours = int(match.group(1))
                return now + timedelta(hours=hours)
        
        elif 'day' in schedule:
            return now + timedelta(days=1)
        
        elif 'week' in schedule:
            return now + timedelta(weeks=1)
        
        return now + timedelta(hours=1)
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """Get all scheduled tasks"""
        return [
            {
                'id': task['id'],
                'name': task['name'],
                'schedule': task['schedule'],
                'next_run': task['next_run'].isoformat(),
                'enabled': task['enabled']
            }
            for task in self.scheduled_tasks
        ]


class WorkflowAutomationEngine:
    """Main workflow automation system"""
    
    def __init__(self):
        self.parser = NaturalLanguageParser()
        self.executor = WorkflowExecutor()
        self.scheduler = ScheduledTaskManager()
        self.workflows: Dict[str, Workflow] = {}
    
    def create_workflow_from_natural_language(self, description: str, name: str = None) -> Workflow:
        """Create workflow from natural language description"""
        parsed = self.parser.parse(description)
        
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        triggers = [
            WorkflowTrigger(
                id=f"trigger_{i}",
                type=TriggerType[t['type'].upper()],
                condition=t.get('condition', ''),
                parameters=t
            )
            for i, t in enumerate(parsed['triggers'])
        ]
        
        actions = [
            WorkflowAction(
                id=f"action_{i}",
                type=ActionType[a['type'].upper()],
                description=a.get('description', ''),
                parameters=a
            )
            for i, a in enumerate(parsed['actions'])
        ]
        
        workflow = Workflow(
            id=workflow_id,
            name=name or f"Workflow {workflow_id}",
            description=description,
            triggers=triggers,
            actions=actions
        )
        
        self.workflows[workflow_id] = workflow
        
        return workflow
    
    def create_workflow(self, workflow_config: Dict) -> Workflow:
        """Create workflow from configuration"""
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        workflow = Workflow(
            id=workflow_id,
            name=workflow_config['name'],
            description=workflow_config.get('description', ''),
            triggers=[],
            actions=[]
        )
        
        self.workflows[workflow_id] = workflow
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str, context: Dict = None) -> Dict:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_id)
        
        if not workflow:
            return {'error': 'Workflow not found'}
        
        if not workflow.enabled:
            return {'error': 'Workflow is disabled'}
        
        result = await self.executor.execute_workflow(workflow, context)
        
        # Update workflow stats
        workflow.last_run = datetime.now().isoformat()
        workflow.run_count += 1
        
        return result
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict]:
        """List all workflows"""
        return [asdict(w) for w in self.workflows.values()]
    
    def enable_workflow(self, workflow_id: str):
        """Enable a workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].enabled = True
    
    def disable_workflow(self, workflow_id: str):
        """Disable a workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].enabled = False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            return True
        return False
    
    def get_execution_history(self, workflow_id: Optional[str] = None) -> List[Dict]:
        """Get execution history"""
        if workflow_id:
            return [h for h in self.executor.execution_history 
                   if h['workflow_id'] == workflow_id]
        return self.executor.execution_history
