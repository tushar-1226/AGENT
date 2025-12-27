"""
Git Integration Manager
Complete Git workflow with AI-powered commit messages
"""
import os
from typing import List, Dict, Optional
from datetime import datetime

try:
    import git
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("GitPython not installed. Run: pip install gitpython")

class GitManager:
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
        self.repo = None
        
        if GIT_AVAILABLE:
            self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize Git repository"""
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            print(f"Not a git repository: {e}")
            self.repo = None
    
    def is_repo(self) -> bool:
        """Check if current directory is a git repo"""
        return self.repo is not None
    
    def get_status(self) -> Dict:
        """Get git status"""
        if not self.repo:
            return {'error': 'Not a git repository'}
        
        try:
            status = {
                'branch': self.repo.active_branch.name,
                'modified': [item.a_path for item in self.repo.index.diff(None)],
                'staged': [item.a_path for item in self.repo.index.diff('HEAD')],
                'untracked': self.repo.untracked_files,
                'ahead': 0,
                'behind': 0
            }
            
            # Get ahead/behind count
            try:
                tracking_branch = self.repo.active_branch.tracking_branch()
                if tracking_branch:
                    ahead_behind = self.repo.iter_commits(f'{tracking_branch}..{self.repo.active_branch}')
                    status['ahead'] = sum(1 for _ in ahead_behind)
                    
                    behind = self.repo.iter_commits(f'{self.repo.active_branch}..{tracking_branch}')
                    status['behind'] = sum(1 for _ in behind)
            except Exception:
                pass
            
            return status
        except Exception as e:
            return {'error': str(e)}
    
    def get_diff(self, staged: bool = False) -> str:
        """Get diff of changes"""
        if not self.repo:
            return "Not a git repository"
        
        try:
            if staged:
                diff = self.repo.index.diff('HEAD', create_patch=True)
            else:
                diff = self.repo.index.diff(None, create_patch=True)
            
            diff_text = ""
            for item in diff:
                diff_text += f"\n--- {item.a_path}\n+++ {item.b_path}\n"
                diff_text += item.diff.decode('utf-8', errors='replace')
            
            return diff_text if diff_text else "No changes"
        except Exception as e:
            return f"Error getting diff: {e}"
    
    def stage_files(self, files: List[str] = None) -> bool:
        """Stage files for commit"""
        if not self.repo:
            return False
        
        try:
            if files:
                self.repo.index.add(files)
            else:
                # Stage all changes
                self.repo.git.add(A=True)
            return True
        except Exception as e:
            print(f"Error staging files: {e}")
            return False
    
    def commit(self, message: str, author: str = None) -> Optional[str]:
        """Create a commit"""
        if not self.repo:
            return None
        
        try:
            if author:
                commit = self.repo.index.commit(message, author=author)
            else:
                commit = self.repo.index.commit(message)
            return commit.hexsha
        except Exception as e:
            print(f"Error committing: {e}")
            return None
    
    def generate_commit_message(self, diff: str = None) -> str:
        """Generate AI commit message from diff"""
        if not diff:
            diff = self.get_diff(staged=True)
        
        # Simple heuristic-based message generation
        # In production, use Gemini API for better messages
        
        if "def " in diff or "function " in diff or "class " in diff:
            return "feat: Add new functionality"
        elif "fix" in diff.lower() or "bug" in diff.lower():
            return "fix: Bug fixes"
        elif "test" in diff.lower():
            return "test: Add tests"
        elif "doc" in diff.lower() or "README" in diff:
            return "docs: Update documentation"
        elif "style" in diff.lower() or "css" in diff.lower():
            return "style: UI improvements"
        else:
            return "chore: Update code"
    
    def push(self, remote: str = 'origin', branch: str = None) -> bool:
        """Push commits to remote"""
        if not self.repo:
            return False
        
        try:
            if not branch:
                branch = self.repo.active_branch.name
            
            origin = self.repo.remote(remote)
            origin.push(branch)
            return True
        except Exception as e:
            print(f"Error pushing: {e}")
            return False
    
    def pull(self, remote: str = 'origin', branch: str = None) -> bool:
        """Pull changes from remote"""
        if not self.repo:
            return False
        
        try:
            if not branch:
                branch = self.repo.active_branch.name
            
            origin = self.repo.remote(remote)
            origin.pull(branch)
            return True
        except Exception as e:
            print(f"Error pulling: {e}")
            return False
    
    def get_log(self, max_count: int = 10) -> List[Dict]:
        """Get commit history"""
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append({
                    'hash': commit.hexsha[:7],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                    'files_changed': len(commit.stats.files)
                })
            return commits
        except Exception as e:
            print(f"Error getting log: {e}")
            return []
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch"""
        if not self.repo:
            return False
        
        try:
            self.repo.create_head(branch_name)
            return True
        except Exception as e:
            print(f"Error creating branch: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout a branch"""
        if not self.repo:
            return False
        
        try:
            self.repo.git.checkout(branch_name)
            return True
        except Exception as e:
            print(f"Error checking out branch: {e}")
            return False
    
    def list_branches(self) -> List[str]:
        """List all branches"""
        if not self.repo:
            return []
        
        try:
            return [branch.name for branch in self.repo.branches]
        except Exception as e:
            print(f"Error listing branches: {e}")
            return []
    
    def get_remote_url(self, remote: str = 'origin') -> Optional[str]:
        """Get remote URL"""
        if not self.repo:
            return None
        
        try:
            return self.repo.remote(remote).url
        except Exception:
            return None
    
    def stash(self, message: str = None) -> bool:
        """Stash current changes"""
        if not self.repo:
            return False
        
        try:
            if message:
                self.repo.git.stash('save', message)
            else:
                self.repo.git.stash()
            return True
        except Exception as e:
            print(f"Error stashing: {e}")
            return False
    
    def stash_pop(self) -> bool:
        """Pop stashed changes"""
        if not self.repo:
            return False
        
        try:
            self.repo.git.stash('pop')
            return True
        except Exception as e:
            print(f"Error popping stash: {e}")
            return False
