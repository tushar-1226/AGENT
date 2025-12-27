"""
App Launcher Module for Friday Agent
Handles opening and managing applications
"""
import subprocess
import platform
import os
import psutil
import logging
from typing import Optional, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppLauncher:
    def __init__(self):
        self.system = platform.system()
        self.running_apps = {}
        
        # Common application commands for different platforms
        self.app_commands = {
            'Linux': {
                'chrome': 'google-chrome',
                'firefox': 'firefox',
                'code': 'code',
                'vscode': 'code',
                'terminal': 'gnome-terminal',
                'file manager': 'nautilus',
                'calculator': 'gnome-calculator',
                'text editor': 'gedit',
                'browser': 'firefox',
                'spotify': 'spotify',
                'slack': 'slack',
                'discord': 'discord',
                'vlc': 'vlc',
                'gimp': 'gimp',
            },
            'Windows': {
                'chrome': 'chrome',
                'firefox': 'firefox',
                'notepad': 'notepad',
                'calculator': 'calc',
                'explorer': 'explorer',
                'cmd': 'cmd',
                'powershell': 'powershell',
            },
            'Darwin': {  # macOS
                'chrome': 'open -a "Google Chrome"',
                'safari': 'open -a Safari',
                'finder': 'open -a Finder',
                'terminal': 'open -a Terminal',
            }
        }
    
    def launch_app(self, app_name: str) -> Dict[str, any]:
        """Launch an application by name"""
        app_name = app_name.lower().strip()
        
        # Get the command for this app on current platform
        platform_apps = self.app_commands.get(self.system, {})
        command = platform_apps.get(app_name)
        
        if not command:
            # Try to launch directly
            command = app_name
        
        try:
            logger.info(f"Launching {app_name} with command: {command}")
            
            if self.system == 'Darwin':
                process = subprocess.Popen(command, shell=True)
            else:
                process = subprocess.Popen(command.split())
            
            self.running_apps[app_name] = process.pid
            
            return {
                'success': True,
                'message': f"Successfully launched {app_name}",
                'pid': process.pid
            }
            
        except FileNotFoundError:
            logger.error(f"Application {app_name} not found")
            return {
                'success': False,
                'message': f"Application {app_name} not found on this system",
                'error': 'not_found'
            }
        except Exception as e:
            logger.error(f"Error launching {app_name}: {e}")
            return {
                'success': False,
                'message': f"Error launching {app_name}: {str(e)}",
                'error': str(e)
            }
    
    def close_app(self, app_name: str) -> Dict[str, any]:
        """Close an application by name"""
        app_name = app_name.lower().strip()
        
        if app_name not in self.running_apps:
            return {
                'success': False,
                'message': f"{app_name} is not running or was not launched by Friday"
            }
        
        try:
            pid = self.running_apps[app_name]
            process = psutil.Process(pid)
            process.terminate()
            del self.running_apps[app_name]
            
            return {
                'success': True,
                'message': f"Successfully closed {app_name}"
            }
        except psutil.NoSuchProcess:
            del self.running_apps[app_name]
            return {
                'success': False,
                'message': f"{app_name} is no longer running"
            }
        except Exception as e:
            logger.error(f"Error closing {app_name}: {e}")
            return {
                'success': False,
                'message': f"Error closing {app_name}: {str(e)}"
            }
    
    def list_running_apps(self) -> List[str]:
        """List apps launched by Friday that are still running"""
        running = []
        for app_name, pid in list(self.running_apps.items()):
            try:
                if psutil.pid_exists(pid):
                    running.append(app_name)
                else:
                    del self.running_apps[app_name]
            except:
                del self.running_apps[app_name]
        
        return running
    
    def get_available_apps(self) -> List[str]:
        """Get list of available apps for current platform"""
        return list(self.app_commands.get(self.system, {}).keys())
