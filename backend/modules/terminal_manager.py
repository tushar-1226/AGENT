"""
Integrated Terminal Manager
Execute terminal commands with real-time output streaming
"""
import asyncio
import os
import subprocess
from typing import Dict, List, Optional, Callable
import uuid
from datetime import datetime

class TerminalSession:
    def __init__(self, session_id: str, cwd: str = None):
        self.session_id = session_id
        self.cwd = cwd or os.getcwd()
        self.history: List[Dict] = []
        self.created_at = datetime.now()
    
    def add_to_history(self, command: str, output: str, exit_code: int):
        """Add command to history"""
        self.history.append({
            'command': command,
            'output': output,
            'exit_code': exit_code,
            'timestamp': datetime.now().isoformat(),
            'cwd': self.cwd
        })

class TerminalManager:
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
        
        # Whitelist of safe commands (can be expanded)
        self.safe_commands = {
            'ls', 'dir', 'pwd', 'cd', 'cat', 'echo', 'grep', 'find',
            'git', 'npm', 'pip', 'python', 'node', 'cargo', 'go',
            'make', 'cmake', 'gcc', 'javac', 'mvn', 'gradle',
            'docker', 'kubectl', 'terraform', 'ansible'
        }
        
        # Dangerous commands that need confirmation
        self.dangerous_commands = {
            'rm', 'rmdir', 'del', 'format', 'mkfs', 'dd',
            'shutdown', 'reboot', 'halt', 'poweroff'
        }
    
    def create_session(self, cwd: str = None) -> str:
        """Create a new terminal session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = TerminalSession(session_id, cwd)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a terminal session"""
        return self.sessions.get(session_id)
    
    def is_command_safe(self, command: str) -> tuple[bool, str]:
        """Check if command is safe to execute"""
        # Get the base command
        base_command = command.strip().split()[0] if command.strip() else ''
        
        # Check for dangerous commands
        if base_command in self.dangerous_commands:
            return False, f"Dangerous command '{base_command}' requires user confirmation"
        
        # Check for shell operators that could be dangerous
        dangerous_operators = ['>', '>>', '|', '&&', '||', ';']
        if any(op in command for op in dangerous_operators):
            # Allow some safe uses
            if not any(danger in command for danger in ['rm ', 'del ', 'format']):
                return True, "Command contains operators but appears safe"
        
        return True, "Command is safe"
    
    async def execute_command(
        self, 
        session_id: str, 
        command: str,
        output_callback: Optional[Callable] = None,
        force: bool = False
    ) -> Dict:
        """Execute a command asynchronously with streaming output"""
        session = self.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found',
                'exit_code': -1
            }
        
        # Safety check
        if not force:
            is_safe, message = self.is_command_safe(command)
            if not is_safe:
                return {
                    'success': False,
                    'error': message,
                    'requires_confirmation': True,
                    'exit_code': -1
                }
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session.cwd,
                env=os.environ.copy()
            )
            
            output_lines = []
            
            # Read output in real-time
            async def read_stream(stream, is_stderr=False):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    
                    decoded_line = line.decode('utf-8', errors='replace')
                    output_lines.append(decoded_line)
                    
                    # Call callback for real-time streaming
                    if output_callback:
                        await output_callback({
                            'type': 'stderr' if is_stderr else 'stdout',
                            'data': decoded_line
                        })
            
            # Read both stdout and stderr concurrently
            await asyncio.gather(
                read_stream(process.stdout, False),
                read_stream(process.stderr, True)
            )
            
            # Wait for process to complete
            exit_code = await process.wait()
            
            # Combine output
            full_output = ''.join(output_lines)
            
            # Add to history
            session.add_to_history(command, full_output, exit_code)
            
            # Handle directory change
            if command.strip().startswith('cd '):
                new_dir = command.strip()[3:].strip()
                if new_dir:
                    try:
                        new_path = os.path.join(session.cwd, new_dir)
                        if os.path.isdir(new_path):
                            session.cwd = os.path.abspath(new_path)
                    except Exception:
                        pass
            
            return {
                'success': exit_code == 0,
                'output': full_output,
                'exit_code': exit_code,
                'cwd': session.cwd
            }
            
        except Exception as e:
            error_msg = f"Command execution error: {str(e)}"
            session.add_to_history(command, error_msg, -1)
            return {
                'success': False,
                'error': error_msg,
                'exit_code': -1
            }
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get command history for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        return session.history[-limit:]
    
    def change_directory(self, session_id: str, path: str) -> bool:
        """Change working directory for a session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            new_path = os.path.join(session.cwd, path)
            if os.path.isdir(new_path):
                session.cwd = os.path.abspath(new_path)
                return True
        except Exception:
            pass
        
        return False
    
    def get_current_directory(self, session_id: str) -> Optional[str]:
        """Get current working directory for a session"""
        session = self.get_session(session_id)
        return session.cwd if session else None
    
    def list_sessions(self) -> List[Dict]:
        """List all active sessions"""
        return [{
            'session_id': session.session_id,
            'cwd': session.cwd,
            'created_at': session.created_at.isoformat(),
            'command_count': len(session.history)
        } for session in self.sessions.values()]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a terminal session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_suggestions(self, partial_command: str, session_id: str) -> List[str]:
        """Get command suggestions based on partial input"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        suggestions = []
        
        # Suggest from history
        for entry in reversed(session.history):
            cmd = entry['command']
            if cmd.startswith(partial_command) and cmd not in suggestions:
                suggestions.append(cmd)
                if len(suggestions) >= 5:
                    break
        
        # Suggest common commands
        common_commands = [
            'ls -la', 'git status', 'git log', 'npm install',
            'npm run dev', 'python -m', 'pip install',
            'docker ps', 'docker logs', 'kubectl get pods'
        ]
        
        for cmd in common_commands:
            if cmd.startswith(partial_command) and cmd not in suggestions:
                suggestions.append(cmd)
                if len(suggestions) >= 10:
                    break
        
        return suggestions
