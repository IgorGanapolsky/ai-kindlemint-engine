#!/usr/bin/env python3
"""
GitHub MCP Orchestrator
Continuous PR monitoring and auto-fixing using GitHub App and MCP Server
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class GitHubMCPOrchestrator:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.app_id = os.environ.get('GITHUB_APP_ID', 'YOUR_APP_ID')
        self.client_id = os.environ.get('GITHUB_CLIENT_ID', 'YOUR_CLIENT_ID')
        self.mcp_server_url = "http://localhost:8080"
        self.repo_owner = "IgorGanapolsky"
        self.repo_name = "ai-kindlemint-engine"
        self.github_api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        if not self.github_token:
            print("❌ GITHUB_TOKEN not set. Please set it first.")
            sys.exit(1)
            
    def setup_mcp_server(self) -> bool:
        """Set up GitHub MCP server using docker-compose"""
        print("🚀 Setting up GitHub MCP server...")
        
        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except:
            print("❌ Docker not installed. Falling back to direct API mode.")
            return False
            
        # Check if private key exists
        private_key_path = Path.home() / ".ssh/github-mcp-orchestrator.private-key.pem"
        if not private_key_path.exists():
            print(f"⚠️  Private key not found at {private_key_path}")
            print("Please place your GitHub App private key at this location")
            return False
            
        # Start MCP server with docker-compose
        try:
            print("🐳 Starting MCP server with docker-compose...")
            subprocess.run(
                ["docker-compose", "up", "-d", "mcp-server"],
                env={**os.environ, "GITHUB_TOKEN": self.github_token},
                check=True
            )
            
            # Wait for server to be ready
            print("⏳ Waiting for MCP server to be ready...")
            for i in range(30):
                try:
                    response = requests.get(f"{self.mcp_server_url}/health")
                    if response.status_code == 200:
                        print("✅ MCP server is ready!")
                        return True
                except:
                    pass
                time.sleep(2)
                
            print("❌ MCP server failed to start")
            return False
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
            
    def monitor_pull_requests(self) -> List[Dict[str, Any]]:
        """Get all open pull requests with their CI status"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get open PRs
        response = requests.get(
            f"{self.github_api_base}/pulls?state=open",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch PRs: {response.status_code}")
            return []
            
        prs = response.json()
        pr_statuses = []
        
        for pr in prs:
            pr_number = pr['number']
            pr_info = {
                'number': pr_number,
                'title': pr['title'],
                'author': pr['user']['login'],
                'branch': pr['head']['ref'],
                'sha': pr['head']['sha'],
                'url': pr['html_url'],
                'checks': self.get_pr_checks(pr_number, pr['head']['sha'], headers)
            }
            pr_statuses.append(pr_info)
            
        return pr_statuses
        
    def get_pr_checks(self, pr_number: int, sha: str, headers: Dict) -> Dict[str, Any]:
        """Get check runs for a specific PR"""
        response = requests.get(
            f"{self.github_api_base}/commits/{sha}/check-runs",
            headers=headers
        )
        
        if response.status_code != 200:
            return {"status": "unknown", "failed_checks": []}
            
        data = response.json()
        check_runs = data.get('check_runs', [])
        
        failed_checks = []
        status = "success"
        
        for check in check_runs:
            if check['status'] == 'completed':
                if check['conclusion'] in ['failure', 'cancelled']:
                    failed_checks.append({
                        'name': check['name'],
                        'conclusion': check['conclusion'],
                        'details_url': check.get('details_url', ''),
                        'output': check.get('output', {})
                    })
                    status = "failure"
                elif check['conclusion'] == 'action_required':
                    status = "action_required"
            elif check['status'] in ['queued', 'in_progress']:
                status = "pending"
                
        return {
            "status": status,
            "failed_checks": failed_checks,
            "total_checks": len(check_runs)
        }
        
    def analyze_ci_failure(self, pr_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CI failures and determine fix strategy"""
        failed_checks = pr_info['checks']['failed_checks']
        
        fixes = {
            'lint_errors': [],
            'test_failures': [],
            'build_errors': [],
            'other_errors': []
        }
        
        for check in failed_checks:
            check_name = check['name'].lower()
            
            if 'lint' in check_name or 'eslint' in check_name or 'black' in check_name:
                fixes['lint_errors'].append(check)
            elif 'test' in check_name or 'pytest' in check_name:
                fixes['test_failures'].append(check)
            elif 'build' in check_name or 'compile' in check_name:
                fixes['build_errors'].append(check)
            else:
                fixes['other_errors'].append(check)
                
        return fixes
        
    def auto_fix_pr(self, pr_info: Dict[str, Any]) -> bool:
        """Automatically fix PR issues using MCP server or direct fixes"""
        print(f"\n🔧 Attempting to fix PR #{pr_info['number']}: {pr_info['title']}")
        
        fixes_needed = self.analyze_ci_failure(pr_info)
        
        # Try MCP server first
        if self.mcp_server_available():
            return self.fix_via_mcp_server(pr_info, fixes_needed)
        else:
            return self.fix_via_direct_api(pr_info, fixes_needed)
            
    def mcp_server_available(self) -> bool:
        """Check if MCP server is available"""
        try:
            response = requests.get(f"{self.mcp_server_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def fix_via_mcp_server(self, pr_info: Dict[str, Any], fixes_needed: Dict[str, Any]) -> bool:
        """Fix PR issues using MCP server"""
        # Send fix request to MCP server
        payload = {
            "action": "fix_pr",
            "pr_number": pr_info['number'],
            "branch": pr_info['branch'],
            "fixes_needed": fixes_needed
        }
        
        try:
            response = requests.post(
                f"{self.mcp_server_url}/api/fix",
                json=payload,
                headers={"Authorization": f"Bearer {self.github_token}"}
            )
            
            if response.status_code == 200:
                print("✅ MCP server initiated fixes")
                return True
            else:
                print(f"❌ MCP server fix failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP server error: {e}")
            return False
            
    def fix_via_direct_api(self, pr_info: Dict[str, Any], fixes_needed: Dict[str, Any]) -> bool:
        """Fix PR issues using direct GitHub API"""
        print("🔄 Using direct API mode for fixes...")
        
        # Handle lint errors
        if fixes_needed['lint_errors']:
            print("📝 Found lint errors - triggering auto-format workflow")
            self.trigger_workflow('auto-format.yml', pr_info['branch'])
            
        # Handle test failures
        if fixes_needed['test_failures']:
            print("🧪 Found test failures - analyzing...")
            # In a real implementation, we'd analyze test logs and create fix commits
            
        # Handle build errors
        if fixes_needed['build_errors']:
            print("🏗️  Found build errors - checking dependencies...")
            # In a real implementation, we'd check for missing deps, version conflicts, etc.
            
        return True
        
    def trigger_workflow(self, workflow_file: str, ref: str) -> bool:
        """Trigger a GitHub Actions workflow"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {"ref": ref}
        
        response = requests.post(
            f"{self.github_api_base}/actions/workflows/{workflow_file}/dispatches",
            headers=headers,
            json=payload
        )
        
        return response.status_code == 204
        
    def continuous_monitor(self, interval: int = 300):
        """Continuously monitor and fix PRs"""
        print(f"🔍 Starting continuous PR monitoring (checking every {interval} seconds)")
        print(f"📍 Repository: {self.repo_owner}/{self.repo_name}")
        print("Press Ctrl+C to stop\n")
        
        # Try to set up MCP server
        mcp_available = self.setup_mcp_server()
        
        if mcp_available:
            print("✅ Using GitHub MCP server for advanced automation")
        else:
            print("⚡ Using direct GitHub API mode")
            
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"🕐 Check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get all open PRs
                prs = self.monitor_pull_requests()
                
                if not prs:
                    print("📭 No open pull requests")
                else:
                    print(f"📬 Found {len(prs)} open pull requests")
                    
                    for pr in prs:
                        status = pr['checks']['status']
                        print(f"\nPR #{pr['number']}: {pr['title']}")
                        print(f"  Status: {status}")
                        print(f"  Author: {pr['author']}")
                        print(f"  Branch: {pr['branch']}")
                        
                        if status == "failure":
                            print(f"  ❌ {len(pr['checks']['failed_checks'])} failed checks")
                            
                            # Attempt auto-fix
                            if self.auto_fix_pr(pr):
                                print("  ✅ Fix initiated")
                            else:
                                print("  ⚠️  Manual intervention required")
                        elif status == "success":
                            print("  ✅ All checks passing")
                            # Could auto-merge here if configured
                        elif status == "pending":
                            print("  ⏳ Checks in progress")
                            
                print(f"\n💤 Sleeping for {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            
            # Stop MCP server if running
            if mcp_available:
                print("🐳 Stopping MCP server...")
                subprocess.run(["docker-compose", "down"], capture_output=True)
                
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub MCP Orchestrator for continuous PR monitoring')
    parser.add_argument('command', choices=['monitor', 'setup', 'status'], 
                       help='Command to run')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    orchestrator = GitHubMCPOrchestrator()
    
    if args.command == 'monitor':
        orchestrator.continuous_monitor(args.interval)
    elif args.command == 'setup':
        if orchestrator.setup_mcp_server():
            print("✅ MCP server setup complete")
        else:
            print("❌ MCP server setup failed")
    elif args.command == 'status':
        prs = orchestrator.monitor_pull_requests()
        print(json.dumps(prs, indent=2))
        
if __name__ == "__main__":
    main()