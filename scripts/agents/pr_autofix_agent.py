#!/usr/bin/env python3
"""
PR Auto-Fix Agent for MCP Server
Automatically fixes common issues in pull requests
"""

import os
import json
import re
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import tempfile
import shutil
from security import safe_requests, safe_command

class PRAutoFixAgent:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
        
    def get_pr_details(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """Get pull request details"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        
        response = safe_requests.get(url, headers=self.headers, timeout=60)
        if response.status_code == 200:
            return response.json()
        return None
        
    def get_pr_files(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/files"
        
        response = safe_requests.get(url, headers=self.headers, timeout=60)
        if response.status_code == 200:
            return response.json()
        return []
        
    def get_check_runs(self, ref: str) -> List[Dict[str, Any]]:
        """Get check runs for a specific ref"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits/{ref}/check-runs"
        
        response = safe_requests.get(url, headers=self.headers, timeout=60)
        if response.status_code == 200:
            return response.json()["check_runs"]
        return []
        
    def create_comment(self, pr_number: int, body: str) -> bool:
        """Create a comment on a pull request"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
        
        data = {"body": body}
        response = requests.post(url, headers=self.headers, json=data, timeout=60)
        return response.status_code == 201
        
    def update_file(self, file_path: str, content: str, message: str, branch: str, sha: str) -> bool:
        """Update a file in the repository"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        
        # Base64 encode the content
        import base64
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": branch
        }
        
        response = requests.put(url, headers=self.headers, json=data, timeout=60)
        return response.status_code == 200
        
    def fix_formatting_issues(self, pr_number: int) -> Dict[str, Any]:
        """Fix common formatting issues"""
        print(f"🔧 Checking PR #{pr_number} for formatting issues...")
        
        pr = self.get_pr_details(pr_number)
        if not pr:
            return {"status": "error", "message": "Could not fetch PR details"}
            
        branch = pr["head"]["ref"]
        files = self.get_pr_files(pr_number)
        fixes_applied = []
        
        for file in files:
            if file["status"] in ["modified", "added"]:
                file_path = file["filename"]
                
                # Check file extensions for formatting
                if file_path.endswith(('.py', '.js', '.ts', '.tsx', '.jsx')):
                    # Get file content
                    content_response = safe_requests.get(file["contents_url"], headers=self.headers, timeout=60)
                    if content_response.status_code == 200:
                        file_data = content_response.json()
                        import base64
                        content = base64.b64decode(file_data["content"]).decode()
                        
                        # Apply fixes
                        fixed_content, fixes = self.apply_formatting_fixes(content, file_path)
                        
                        if fixes:
                            # Update file
                            if self.update_file(file_path, fixed_content, 
                                              f"Auto-fix: Apply formatting to {file_path}", 
                                              branch, file_data["sha"]):
                                fixes_applied.extend(fixes)
                                
        if fixes_applied:
            # Comment on PR
            comment = "🤖 **Auto-fix applied:**\n\n"
            for fix in fixes_applied:
                comment += f"- {fix}\n"
            comment += "\nPlease review the changes."
            
            self.create_comment(pr_number, comment)
            
        return {
            "status": "success",
            "fixes_applied": len(fixes_applied),
            "details": fixes_applied
        }
        
    def apply_formatting_fixes(self, content: str, file_path: str) -> Tuple[str, List[str]]:
        """Apply formatting fixes to content"""
        fixes = []
        fixed_content = content
        
        if file_path.endswith('.py'):
            # Python fixes
            # Remove trailing whitespace
            if re.search(r'[ \t]+$', content, re.MULTILINE):
                fixed_content = re.sub(r'[ \t]+$', '', fixed_content, flags=re.MULTILINE)
                fixes.append("Removed trailing whitespace")
                
            # Fix multiple blank lines
            if re.search(r'\n{4,}', content):
                fixed_content = re.sub(r'\n{4,}', '\n\n\n', fixed_content)
                fixes.append("Fixed excessive blank lines")
                
            # Add newline at end of file if missing
            if not content.endswith('\n'):
                fixed_content += '\n'
                fixes.append("Added newline at end of file")
                
        elif file_path.endswith(('.js', '.ts', '.tsx', '.jsx')):
            # JavaScript/TypeScript fixes
            # Remove trailing whitespace
            if re.search(r'[ \t]+$', content, re.MULTILINE):
                fixed_content = re.sub(r'[ \t]+$', '', fixed_content, flags=re.MULTILINE)
                fixes.append("Removed trailing whitespace")
                
            # Fix semicolon consistency (add missing semicolons)
            lines = fixed_content.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()
                if (stripped and 
                    not stripped.endswith((';', '{', '}', ':', ',', '(', ')', '[', ']')) and
                    not stripped.startswith(('import', 'export', '//', '/*', '*')) and
                    re.match(r'^(const|let|var|return)\s+', stripped)):
                    lines[i] = line + ';'
                    fixes.append(f"Added missing semicolon on line {i+1}")
            fixed_content = '\n'.join(lines)
            
        return fixed_content, fixes
        
    def fix_merge_conflicts(self, pr_number: int) -> Dict[str, Any]:
        """Attempt to fix merge conflicts"""
        print(f"🔀 Checking PR #{pr_number} for merge conflicts...")
        
        pr = self.get_pr_details(pr_number)
        if not pr:
            return {"status": "error", "message": "Could not fetch PR details"}
            
        if pr["mergeable_state"] == "clean":
            return {"status": "success", "message": "No merge conflicts found"}
            
        # Clone and attempt to resolve conflicts
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            clone_cmd = f"git clone https://{self.github_token}@github.com/{self.repo_owner}/{self.repo_name}.git {temp_dir}"
            safe_command.run(subprocess.run, clone_cmd.split(), capture_output=True)
            
            os.chdir(temp_dir)
            
            # Fetch the PR branch
            subprocess.run(["git", "fetch", "origin", f"pull/{pr_number}/head:pr-{pr_number}"], capture_output=True)
            subprocess.run(["git", "checkout", f"pr-{pr_number}"], capture_output=True)
            
            # Try to merge main
            merge_result = subprocess.run(["git", "merge", "origin/main", "--no-commit"], capture_output=True)
            
            if merge_result.returncode != 0:
                # Attempt automatic resolution
                conflicts_resolved = self.auto_resolve_conflicts(temp_dir)
                
                if conflicts_resolved:
                    # Commit and push
                    subprocess.run(["git", "add", "."], capture_output=True)
                    subprocess.run(["git", "commit", "-m", "Auto-resolve merge conflicts"], capture_output=True)
                    subprocess.run(["git", "push", "origin", f"pr-{pr_number}:{pr['head']['ref']}"], capture_output=True)
                    
                    self.create_comment(pr_number, "🤖 **Auto-fix:** Resolved merge conflicts automatically. Please review the changes.")
                    
                    return {"status": "success", "conflicts_resolved": conflicts_resolved}
                    
        return {"status": "failed", "message": "Could not automatically resolve conflicts"}
        
    def auto_resolve_conflicts(self, repo_dir: str) -> int:
        """Attempt to automatically resolve conflicts"""
        conflicts_resolved = 0
        
        # Get list of conflicted files
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        
        for line in status_result.stdout.split('\n'):
            if line.startswith('UU '):
                file_path = line[3:]
                
                # Simple resolution strategies
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # For package-lock.json, regenerate it
                if file_path == 'package-lock.json':
                    os.remove(file_path)
                    subprocess.run(["npm", "install"], capture_output=True)
                    conflicts_resolved += 1
                    
                # For simple conflicts, try to merge both changes
                elif '<<<<<<< HEAD' in content:
                    # This is a simplified example - in reality, you'd want more sophisticated resolution
                    resolved = self.merge_both_changes(content)
                    if resolved:
                        with open(file_path, 'w') as f:
                            f.write(resolved)
                        conflicts_resolved += 1
                        
        return conflicts_resolved
        
    def merge_both_changes(self, content: str) -> Optional[str]:
        """Simple strategy to merge both changes for certain patterns"""
        # This is a very basic implementation
        # In production, you'd want more sophisticated conflict resolution
        
        # For now, return None to indicate we couldn't resolve it
        return None
        
    def fix_linting_errors(self, pr_number: int) -> Dict[str, Any]:
        """Fix common linting errors"""
        print(f"🔍 Checking PR #{pr_number} for linting errors...")
        
        pr = self.get_pr_details(pr_number)
        if not pr:
            return {"status": "error", "message": "Could not fetch PR details"}
            
        # Check for failed linting checks
        check_runs = self.get_check_runs(pr["head"]["sha"])
        linting_errors = []
        
        for check in check_runs:
            if "lint" in check["name"].lower() and check["conclusion"] == "failure":
                # Parse linting errors from check output
                if check.get("output", {}).get("text"):
                    errors = self.parse_linting_errors(check["output"]["text"])
                    linting_errors.extend(errors)
                    
        if linting_errors:
            # Apply fixes
            fixes_applied = self.apply_linting_fixes(pr_number, linting_errors)
            
            if fixes_applied:
                comment = "🤖 **Auto-fix applied for linting errors:**\n\n"
                for fix in fixes_applied:
                    comment += f"- {fix}\n"
                    
                self.create_comment(pr_number, comment)
                
            return {
                "status": "success",
                "errors_found": len(linting_errors),
                "fixes_applied": len(fixes_applied)
            }
            
        return {"status": "success", "message": "No linting errors found"}
        
    def parse_linting_errors(self, output: str) -> List[Dict[str, Any]]:
        """Parse linting errors from check output"""
        errors = []
        
        # Common ESLint pattern
        eslint_pattern = r'(.+):(\d+):(\d+):\s+error\s+(.+)\s+(.+)'
        for match in re.finditer(eslint_pattern, output):
            errors.append({
                "file": match.group(1),
                "line": int(match.group(2)),
                "column": int(match.group(3)),
                "message": match.group(4),
                "rule": match.group(5)
            })
            
        return errors
        
    def apply_linting_fixes(self, pr_number: int, errors: List[Dict[str, Any]]) -> List[str]:
        """Apply fixes for linting errors"""
        # This would implement specific fixes for common linting errors
        # For now, return empty list
        return []
        
    def process_pr(self, pr_number: int) -> Dict[str, Any]:
        """Process a PR and apply all available fixes"""
        print(f"🚀 Processing PR #{pr_number} for auto-fixes...")
        
        results = {
            "pr_number": pr_number,
            "timestamp": datetime.utcnow().isoformat(),
            "fixes": {}
        }
        
        # Apply various fixes
        results["fixes"]["formatting"] = self.fix_formatting_issues(pr_number)
        results["fixes"]["linting"] = self.fix_linting_errors(pr_number)
        results["fixes"]["merge_conflicts"] = self.fix_merge_conflicts(pr_number)
        
        # Summary
        total_fixes = sum(
            fix.get("fixes_applied", 0) 
            for fix in results["fixes"].values() 
            if isinstance(fix, dict)
        )
        
        if total_fixes > 0:
            self.create_comment(
                pr_number,
                f"✅ **Auto-fix Summary**: Applied {total_fixes} automatic fixes. "
                "Please review the changes and re-run CI checks."
            )
            
        return results

def handle_webhook(event_type: str, payload: Dict[str, Any], agent: PRAutoFixAgent) -> Dict[str, Any]:
    """Handle incoming webhook events"""
    
    if event_type == "pull_request":
        if payload["action"] in ["opened", "synchronize"]:
            pr_number = payload["pull_request"]["number"]
            results = agent.process_pr(pr_number)
            return {"status": "success", "action": "processed_pr", "results": results}
            
    elif event_type == "check_run":
        if payload["action"] == "completed" and payload["check_run"]["conclusion"] == "failure":
            # Check if it's on a PR
            for pr in payload.get("check_run", {}).get("pull_requests", []):
                pr_number = pr["number"]
                results = agent.process_pr(pr_number)
                return {"status": "success", "action": "fixed_failed_check", "results": results}
                
    return {"status": "ignored", "reason": "not_applicable"}

# Example MCP agent registration
def register_agent():
    """Register this agent with the MCP server"""
    return {
        "name": "pr-autofix-agent",
        "description": "Automatically fix common PR issues",
        "version": "1.0.0",
        "triggers": [
            {"type": "webhook", "events": ["pull_request", "check_run"]}
        ],
        "actions": [
            "fix_formatting_issues",
            "fix_linting_errors",
            "fix_merge_conflicts",
            "process_pr"
        ]
    }

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python pr_autofix_agent.py <github_token> <repo_owner> <repo_name> <pr_number>")
        sys.exit(1)
        
    token = sys.argv[1]
    owner = sys.argv[2]
    repo = sys.argv[3]
    pr_number = int(sys.argv[4])
    
    agent = PRAutoFixAgent(token, owner, repo)
    results = agent.process_pr(pr_number)
    print(json.dumps(results, indent=2))
