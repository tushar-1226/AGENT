"""
Integrated Debugger Module
Provides debugging capabilities: breakpoints, step through, variable inspection, call stack
"""

import sys
import os
import json
import threading
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import traceback
import inspect

logger = logging.getLogger(__name__)


class DebugSession:
    """Represents a debugging session"""
    
    def __init__(self, session_id: str, file_path: str):
        self.session_id = session_id
        self.file_path = file_path
        self.breakpoints: Dict[int, Dict] = {}  # line_number -> breakpoint info
        self.current_line: Optional[int] = None
        self.variables: Dict[str, Any] = {}
        self.call_stack: List[Dict] = []
        self.is_running = False
        self.is_paused = False
        self.step_mode = None  # 'over', 'into', 'out'
        
    def add_breakpoint(self, line_number: int, condition: Optional[str] = None):
        """Add a breakpoint"""
        self.breakpoints[line_number] = {
            'line': line_number,
            'enabled': True,
            'condition': condition,
            'hit_count': 0
        }
        
    def remove_breakpoint(self, line_number: int):
        """Remove a breakpoint"""
        if line_number in self.breakpoints:
            del self.breakpoints[line_number]
    
    def toggle_breakpoint(self, line_number: int):
        """Toggle breakpoint enabled/disabled"""
        if line_number in self.breakpoints:
            self.breakpoints[line_number]['enabled'] = not self.breakpoints[line_number]['enabled']
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'file_path': self.file_path,
            'breakpoints': list(self.breakpoints.values()),
            'current_line': self.current_line,
            'variables': self._serialize_variables(),
            'call_stack': self.call_stack,
            'is_running': self.is_running,
            'is_paused': self.is_paused
        }
    
    def _serialize_variables(self):
        """Serialize variables for JSON"""
        serialized = {}
        for name, value in self.variables.items():
            try:
                serialized[name] = {
                    'value': str(value),
                    'type': type(value).__name__,
                    'repr': repr(value)[:200]  # Limit length
                }
            except:
                serialized[name] = {
                    'value': '<unable to serialize>',
                    'type': type(value).__name__,
                    'repr': ''
                }
        return serialized


class IntegratedDebugger:
    """Main debugger class"""
    
    def __init__(self):
        self.sessions: Dict[str, DebugSession] = {}
        self.active_session_id: Optional[str] = None
        
    def create_session(self, file_path: str) -> str:
        """Create a new debug session"""
        import uuid
        session_id = str(uuid.uuid4())
        session = DebugSession(session_id, file_path)
        self.sessions[session_id] = session
        self.active_session_id = session_id
        
        logger.info(f"Created debug session {session_id} for {file_path}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[DebugSession]:
        """Get debug session by ID"""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a debug session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.active_session_id == session_id:
                self.active_session_id = None
            return True
        return False
    
    def add_breakpoint(self, session_id: str, line_number: int, condition: Optional[str] = None) -> bool:
        """Add breakpoint to session"""
        session = self.get_session(session_id)
        if session:
            session.add_breakpoint(line_number, condition)
            logger.info(f"Added breakpoint at line {line_number} in session {session_id}")
            return True
        return False
    
    def remove_breakpoint(self, session_id: str, line_number: int) -> bool:
        """Remove breakpoint from session"""
        session = self.get_session(session_id)
        if session:
            session.remove_breakpoint(line_number)
            logger.info(f"Removed breakpoint at line {line_number} from session {session_id}")
            return True
        return False
    
    def toggle_breakpoint(self, session_id: str, line_number: int) -> bool:
        """Toggle breakpoint"""
        session = self.get_session(session_id)
        if session:
            session.toggle_breakpoint(line_number)
            return True
        return False
    
    def start_debugging(self, session_id: str) -> Dict:
        """Start debugging session"""
        session = self.get_session(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            session.is_running = True
            session.is_paused = False
            
            # Execute the file in debug mode
            result = self._execute_with_tracing(session)
            
            return {
                'success': True,
                'session': session.to_dict(),
                'result': result
            }
        except Exception as e:
            logger.error(f"Error starting debug: {e}")
            return {'success': False, 'error': str(e)}
    
    def step_over(self, session_id: str) -> Dict:
        """Step over current line"""
        session = self.get_session(session_id)
        if session:
            session.step_mode = 'over'
            session.is_paused = False
            return {'success': True, 'session': session.to_dict()}
        return {'success': False, 'error': 'Session not found'}
    
    def step_into(self, session_id: str) -> Dict:
        """Step into function"""
        session = self.get_session(session_id)
        if session:
            session.step_mode = 'into'
            session.is_paused = False
            return {'success': True, 'session': session.to_dict()}
        return {'success': False, 'error': 'Session not found'}
    
    def step_out(self, session_id: str) -> Dict:
        """Step out of current function"""
        session = self.get_session(session_id)
        if session:
            session.step_mode = 'out'
            session.is_paused = False
            return {'success': True, 'session': session.to_dict()}
        return {'success': False, 'error': 'Session not found'}
    
    def continue_execution(self, session_id: str) -> Dict:
        """Continue execution until next breakpoint"""
        session = self.get_session(session_id)
        if session:
            session.step_mode = None
            session.is_paused = False
            return {'success': True, 'session': session.to_dict()}
        return {'success': False, 'error': 'Session not found'}
    
    def pause(self, session_id: str) -> Dict:
        """Pause execution"""
        session = self.get_session(session_id)
        if session:
            session.is_paused = True
            return {'success': True, 'session': session.to_dict()}
        return {'success': False, 'error': 'Session not found'}
    
    def stop(self, session_id: str) -> Dict:
        """Stop debugging"""
        session = self.get_session(session_id)
        if session:
            session.is_running = False
            session.is_paused = False
            session.current_line = None
            return {'success': True, 'session': session.to_dict()}
        return {'success': False, 'error': 'Session not found'}
    
    def get_variables(self, session_id: str, scope: str = 'local') -> Dict:
        """Get variables in current scope"""
        session = self.get_session(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        return {
            'success': True,
            'variables': session._serialize_variables(),
            'scope': scope
        }
    
    def evaluate_expression(self, session_id: str, expression: str) -> Dict:
        """Evaluate expression in current context"""
        session = self.get_session(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            # Evaluate in the context of current variables
            result = eval(expression, {}, session.variables)
            return {
                'success': True,
                'result': str(result),
                'type': type(result).__name__
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_call_stack(self, session_id: str) -> Dict:
        """Get current call stack"""
        session = self.get_session(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        return {
            'success': True,
            'call_stack': session.call_stack
        }
    
    def _execute_with_tracing(self, session: DebugSession) -> Dict:
        """Execute code with tracing for debugging"""
        try:
            # Read the file
            with open(session.file_path, 'r') as f:
                code = f.read()
            
            # Create execution context
            exec_globals = {'__name__': '__main__'}
            exec_locals = {}
            
            # Set up tracing
            def trace_function(frame, event, arg):
                if event == 'line':
                    line_no = frame.f_lineno
                    session.current_line = line_no
                    
                    # Update variables
                    session.variables = {**frame.f_locals}
                    
                    # Update call stack
                    stack = []
                    current_frame = frame
                    while current_frame:
                        stack.append({
                            'function': current_frame.f_code.co_name,
                            'file': current_frame.f_code.co_filename,
                            'line': current_frame.f_lineno
                        })
                        current_frame = current_frame.f_back
                    session.call_stack = stack
                    
                    # Check breakpoints
                    if line_no in session.breakpoints:
                        bp = session.breakpoints[line_no]
                        if bp['enabled']:
                            bp['hit_count'] += 1
                            session.is_paused = True
                            logger.info(f"Hit breakpoint at line {line_no}")
                
                return trace_function
            
            # Execute with tracing
            sys.settrace(trace_function)
            try:
                exec(code, exec_globals, exec_locals)
            finally:
                sys.settrace(None)
            
            session.is_running = False
            
            return {
                'output': 'Execution completed',
                'final_variables': session._serialize_variables()
            }
            
        except Exception as e:
            session.is_running = False
            logger.error(f"Execution error: {e}")
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def list_sessions(self) -> List[Dict]:
        """List all debug sessions"""
        return [session.to_dict() for session in self.sessions.values()]


# Global instance
integrated_debugger = None


def get_debugger():
    """Get or create debugger instance"""
    global integrated_debugger
    if integrated_debugger is None:
        integrated_debugger = IntegratedDebugger()
    return integrated_debugger
