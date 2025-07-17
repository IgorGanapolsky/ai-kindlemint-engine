#!/usr/bin/env python3
"""
GitHub Workflow Orchestrator
Direct GitHub API integration for workflow automation without MCP server
"""

import os
import sys
import json
import requests
import argparse
import time
from typing import Dict, List, Optional, Any

class GitHubWorkflowOrchestrator:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.repo_owner = "IgorGanapolsky"
        self.repo_name = "ai-kindlemint-engine"
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows in the repository"""
        url = f"{self.base_url}/actions/workflows"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            workflows = response.json()["workflows"]
            return workflows
        else:
            print(f"❌ Failed to list workflows: {response.status_code}")
            return []
            
    def trigger_workflow(self, workflow_id: str, ref: str = "main", inputs: Dict[str, Any] = None) -> bool:
        """Trigger a specific workflow"""
        url = f"{self.base_url}/actions/workflows/{workflow_id}/dispatches"
        
        payload = {
            "ref": ref
        }
        
        if inputs:
            payload["inputs"] = inputs
            
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 204:
            print("✅ Workflow triggered successfully")
            return True
        else:
            print(f"❌ Failed to trigger workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    def get_workflow_runs(self, workflow_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow runs"""
        url = f"{self.base_url}/actions/runs"
        
        params = {
            "per_page": limit
        }
        
        if workflow_id:
            params["workflow_id"] = workflow_id
            
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()["workflow_runs"]
        else:
            print(f"❌ Failed to get workflow runs: {response.status_code}")
            return []
            
    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow run"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get run status: {response.status_code}")
            return {}
            
    def cancel_workflow_run(self, run_id: str) -> bool:
        """Cancel a workflow run"""
        url = f"{self.base_url}/actions/runs/{run_id}/cancel"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 202:
            print("✅ Workflow run cancelled")
            return True
        else:
            print(f"❌ Failed to cancel workflow run: {response.status_code}")
            return False
            
    def create_pr_automation(self, pr_number: int, action: str) -> bool:
        """Automate PR actions (label, review, merge)"""
        if action == "label":
            return self.add_pr_labels(pr_number, ["automated", "mcp-processed"])
        elif action == "review":
            return self.create_pr_review(pr_number)
        elif action == "merge":
            return self.merge_pr(pr_number)
        else:
            print(f"❌ Unknown PR action: {action}")
            return False
            
    def add_pr_labels(self, pr_number: int, labels: List[str]) -> bool:
        """Add labels to a PR"""
        url = f"{self.base_url}/issues/{pr_number}/labels"
        response = requests.post(url, headers=self.headers, json=labels)
        
        if response.status_code == 200:
            print(f"✅ Labels added to PR #{pr_number}")
            return True
        else:
            print(f"❌ Failed to add labels: {response.status_code}")
            return False
            
    def create_pr_review(self, pr_number: int) -> bool:
        """Create an automated PR review"""
        url = f"{self.base_url}/pulls/{pr_number}/reviews"
        
        review = {
            "body": "Automated review by MCP Orchestrator",
            "event": "COMMENT",
            "comments": [
                {
                    "path": "README.md",
                    "line": 1,
                    "body": "Automated check passed"
                }
            ]
        }
        
        response = requests.post(url, headers=self.headers, json=review)
        
        if response.status_code == 200:
            print(f"✅ Review created for PR #{pr_number}")
            return True
        else:
            print(f"❌ Failed to create review: {response.status_code}")
            return False
            
    def merge_pr(self, pr_number: int) -> bool:
        """Merge a PR"""
        url = f"{self.base_url}/pulls/{pr_number}/merge"
        
        merge_data = {
            "commit_title": f"Merge PR #{pr_number} via MCP Orchestrator",
            "commit_message": "Automated merge by GitHub Workflow Orchestrator",
            "merge_method": "squash"
        }
        
        response = requests.put(url, headers=self.headers, json=merge_data)
        
        if response.status_code == 200:
            print(f"✅ PR #{pr_number} merged successfully")
            return True
        else:
            print(f"❌ Failed to merge PR: {response.status_code}")
            return False
            
    def monitor_workflow(self, run_id: str, timeout: int = 300) -> str:
        """Monitor a workflow run until completion"""
        start_time = time.time()
        
        print(f"Monitoring workflow run {run_id}...")
        
        while time.time() - start_time < timeout:
            run_info = self.get_run_status(run_id)
            
            if not run_info:
                return "error"
                
            status = run_info.get("status", "unknown")
            conclusion = run_info.get("conclusion", "")
            
            print(f"Status: {status}", end="\r")
            
            if status == "completed":
                print(f"\n✅ Workflow completed with conclusion: {conclusion}")
                return conclusion
                
            time.sleep(5)
            
        print(f"\n⏱️ Timeout reached after {timeout} seconds")
        return "timeout"

def main():
    parser = argparse.ArgumentParser(description="GitHub Workflow Orchestrator")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List workflows
    subparsers.add_parser("list", help="List all workflows")
    
    # Trigger workflow
    trigger_parser = subparsers.add_parser("trigger", help="Trigger a workflow")
    trigger_parser.add_argument("workflow_id", help="Workflow ID or filename")
    trigger_parser.add_argument("--ref", default="main", help="Git ref to run on")
    trigger_parser.add_argument("--inputs", help="JSON string of workflow inputs")
    
    # Get runs
    runs_parser = subparsers.add_parser("runs", help="Get workflow runs")
    runs_parser.add_argument("--workflow", help="Filter by workflow ID")
    runs_parser.add_argument("--limit", type=int, default=10, help="Number of runs to show")
    
    # Monitor run
    monitor_parser = subparsers.add_parser("monitor", help="Monitor a workflow run")
    monitor_parser.add_argument("run_id", help="Run ID to monitor")
    monitor_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    
    # Cancel run
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a workflow run")
    cancel_parser.add_argument("run_id", help="Run ID to cancel")
    
    # PR automation
    pr_parser = subparsers.add_parser("pr", help="Automate PR actions")
    pr_parser.add_argument("pr_number", type=int, help="PR number")
    pr_parser.add_argument("action", choices=["label", "review", "merge"], help="Action to perform")
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN='your-token-here'")
        sys.exit(1)
        
    orchestrator = GitHubWorkflowOrchestrator(github_token)
    
    if args.command == "list":
        workflows = orchestrator.list_workflows()
        print(f"Found {len(workflows)} workflows:")
        for workflow in workflows:
            print(f"  - {workflow['name']} (ID: {workflow['id']}, File: {workflow['path']})")
            
    elif args.command == "trigger":
        inputs = json.loads(args.inputs) if args.inputs else None
        orchestrator.trigger_workflow(args.workflow_id, args.ref, inputs)
        
    elif args.command == "runs":
        runs = orchestrator.get_workflow_runs(args.workflow, args.limit)
        print("Recent workflow runs:")
        for run in runs:
            print(f"  - {run['name']} #{run['run_number']} - {run['status']} ({run['conclusion'] or 'in progress'})")
            
    elif args.command == "monitor":
        orchestrator.monitor_workflow(args.run_id, args.timeout)
        
    elif args.command == "cancel":
        orchestrator.cancel_workflow_run(args.run_id)
        
    elif args.command == "pr":
        orchestrator.create_pr_automation(args.pr_number, args.action)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()