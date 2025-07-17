#!/usr/bin/env python3
"""
CI/CD Cleanup Agent for MCP Server
Automates cleanup of failed CI/CD workflows and stale checks
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

class CICDCleanupAgent:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
        
    def get_workflow_runs(self, status: str = "failure", per_page: int = 100) -> List[Dict[str, Any]]:
        """Get workflow runs with specific status"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs"
        params = {
            "status": status,
            "per_page": per_page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()["workflow_runs"]
        else:
            print(f"Error fetching workflow runs: {response.status_code}")
            return []
            
    def cancel_workflow_run(self, run_id: int) -> bool:
        """Cancel a specific workflow run"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/cancel"
        
        response = requests.post(url, headers=self.headers)
        return response.status_code == 202
        
    def delete_workflow_run(self, run_id: int) -> bool:
        """Delete a specific workflow run"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}"
        
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204
        
    def cleanup_failed_runs(self, older_than_hours: int = 24) -> Dict[str, int]:
        """Cleanup failed workflow runs older than specified hours"""
        print(f"Starting cleanup of failed workflow runs older than {older_than_hours} hours...")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        stats = {
            "cancelled": 0,
            "deleted": 0,
            "failed": 0
        }
        
        # Get failed runs
        failed_runs = self.get_workflow_runs(status="failure")
        
        for run in failed_runs:
            run_time = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            
            if run_time < cutoff_time:
                run_id = run["id"]
                run_name = run["name"]
                
                # Try to cancel if still running
                if run["status"] == "in_progress":
                    if self.cancel_workflow_run(run_id):
                        print(f"✅ Cancelled workflow run: {run_name} (ID: {run_id})")
                        stats["cancelled"] += 1
                    else:
                        stats["failed"] += 1
                        
                # Delete old failed runs
                if self.delete_workflow_run(run_id):
                    print(f"🗑️ Deleted workflow run: {run_name} (ID: {run_id})")
                    stats["deleted"] += 1
                else:
                    stats["failed"] += 1
                    
        return stats
        
    def get_pull_requests(self, state: str = "open") -> List[Dict[str, Any]]:
        """Get pull requests with specific state"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls"
        params = {
            "state": state,
            "per_page": 100
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching pull requests: {response.status_code}")
            return []
            
    def get_check_runs(self, ref: str) -> List[Dict[str, Any]]:
        """Get check runs for a specific ref"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits/{ref}/check-runs"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()["check_runs"]
        else:
            return []
            
    def cleanup_stale_checks(self, older_than_hours: int = 48) -> Dict[str, int]:
        """Cleanup stale checks on PRs"""
        print(f"Starting cleanup of stale checks older than {older_than_hours} hours...")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        stats = {
            "cleaned": 0,
            "failed": 0
        }
        
        # Get open PRs
        prs = self.get_pull_requests(state="open")
        
        for pr in prs:
            head_sha = pr["head"]["sha"]
            check_runs = self.get_check_runs(head_sha)
            
            for check in check_runs:
                if check["status"] == "queued" or check["status"] == "in_progress":
                    check_time = datetime.fromisoformat(check["started_at"].replace("Z", "+00:00"))
                    
                    if check_time < cutoff_time:
                        # Mark stale check as cancelled
                        self._update_check_run(check["id"], "completed", "cancelled")
                        print(f"✅ Cancelled stale check: {check['name']} on PR #{pr['number']}")
                        stats["cleaned"] += 1
                        
        return stats
        
    def _update_check_run(self, check_run_id: int, status: str, conclusion: str) -> bool:
        """Update a check run status"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/check-runs/{check_run_id}"
        
        data = {
            "status": status,
            "conclusion": conclusion,
            "completed_at": datetime.utcnow().isoformat() + "Z"
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        return response.status_code == 200
        
    def cleanup_all(self) -> Dict[str, Any]:
        """Run all cleanup tasks"""
        print("🧹 Starting comprehensive CI/CD cleanup...")
        
        results = {
            "workflow_runs": self.cleanup_failed_runs(older_than_hours=24),
            "stale_checks": self.cleanup_stale_checks(older_than_hours=48),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print("\n📊 Cleanup Summary:")
        print(f"  Workflow Runs - Cancelled: {results['workflow_runs']['cancelled']}, "
              f"Deleted: {results['workflow_runs']['deleted']}")
        print(f"  Stale Checks - Cleaned: {results['stale_checks']['cleaned']}")
        
        return results
        
def handle_webhook(event_type: str, payload: Dict[str, Any], agent: CICDCleanupAgent) -> Dict[str, Any]:
    """Handle incoming webhook events"""
    
    if event_type == "workflow_run":
        if payload["action"] == "completed" and payload["workflow_run"]["conclusion"] == "failure":
            # Cleanup failed runs immediately
            run_id = payload["workflow_run"]["id"]
            if agent.delete_workflow_run(run_id):
                return {"status": "success", "action": "deleted_failed_run", "run_id": run_id}
                
    elif event_type == "check_suite":
        if payload["action"] == "completed" and payload["check_suite"]["conclusion"] == "failure":
            # Mark for cleanup
            return {"status": "noted", "action": "marked_for_cleanup"}
            
    elif event_type == "schedule":
        # Run periodic cleanup
        results = agent.cleanup_all()
        return {"status": "success", "action": "periodic_cleanup", "results": results}
        
    return {"status": "ignored", "reason": "not_applicable"}

# Example MCP agent registration
def register_agent():
    """Register this agent with the MCP server"""
    return {
        "name": "cicd-cleanup-agent",
        "description": "Automated CI/CD workflow and check cleanup",
        "version": "1.0.0",
        "triggers": [
            {"type": "webhook", "events": ["workflow_run", "check_suite"]},
            {"type": "schedule", "cron": "0 */6 * * *"}  # Every 6 hours
        ],
        "actions": [
            "cleanup_failed_runs",
            "cleanup_stale_checks",
            "cancel_workflow_run",
            "delete_workflow_run"
        ]
    }

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python cicd_cleanup_agent.py <github_token> <repo_owner> <repo_name>")
        sys.exit(1)
        
    token = sys.argv[1]
    owner = sys.argv[2]
    repo = sys.argv[3]
    
    agent = CICDCleanupAgent(token, owner, repo)
    agent.cleanup_all()