#!/usr/bin/env python3
"""
Worktree Assignment Checker
Determines which worktree should be used for a given task
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

class WorktreeAssignmentChecker:
    def __init__(self):
        self.base_path = Path.cwd()
        self.config_file = self.base_path / ".worktree_orchestration_config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load orchestration configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def check_assignment(self, task_description: str) -> Tuple[str, str]:
        """
        Determine which worktree to use based on task description
        Returns: (worktree_name, reason)
        """
        task_lower = task_description.lower()
        assignments = self.config.get('worktree_assignments', {})
        
        # Check each worktree's keywords
        for worktree, keywords in assignments.items():
            for keyword in keywords:
                if keyword.lower() in task_lower:
                    return worktree, f"Task contains '{keyword}'"
                    
        # Default assignments based on commit patterns
        if task_lower.startswith('feat:'):
            if 'puzzle' in task_lower:
                return 'puzzle-gen', "Feature related to puzzle generation"
            elif 'pdf' in task_lower or 'book' in task_lower:
                return 'pdf-gen', "Feature related to PDF/book generation"
            elif 'test' in task_lower or 'qa' in task_lower:
                return 'qa-validation', "Feature related to testing/QA"
                
        elif task_lower.startswith('fix:'):
            if 'ci' in task_lower or 'build' in task_lower:
                return 'ci-fixes', "Fix related to CI/build issues"
            else:
                return 'ci-fixes', "General fix (using ci-fixes worktree)"
                
        elif task_lower.startswith('docs:'):
            return 'main', "Documentation changes (low token usage)"
            
        # Market/business related
        if any(word in task_lower for word in ['market', 'kdp', 'category', 'competitor']):
            return 'market-research', "Market/business research task"
            
        # Default to main for simple tasks
        return 'main', "Default assignment (no specific worktree match)"
        
    def print_assignment(self, task: str):
        """Print worktree assignment recommendation"""
        worktree, reason = self.check_assignment(task)
        
        print(f"📋 Task: {task}")
        print(f"🌳 Recommended Worktree: {worktree}")
        print(f"📝 Reason: {reason}")
        
        if worktree != 'main':
            print(f"\n💻 To use this worktree:")
            print(f"cd worktrees/{worktree}")
            print(f"# Make your changes")
            print(f"git add .")
            print(f"git commit -m \"{task}\"")
            print(f"git push")
            
        print(f"\n💰 Token Savings: Using worktrees reduces token usage by ~60%")
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_worktree_assignment.py \"commit message or task description\"")
        sys.exit(1)
        
    task = " ".join(sys.argv[1:])
    checker = WorktreeAssignmentChecker()
    checker.print_assignment(task)