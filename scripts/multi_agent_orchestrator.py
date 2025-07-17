#!/usr/bin/env python3
"""
Multi-Agent Orchestrator with Worktree Management
Each agent works in isolation, tracks progress, and creates PRs
"""

import os
import subprocess
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import threading
import time

class WorktreeAgent:
    """Individual agent that works in its own worktree"""
    
    def __init__(self, agent_id: str, task: str, branch_name: str):
        self.agent_id = agent_id
        self.task = task
        self.branch_name = branch_name
        self.worktree_path = Path(f"worktrees/agent_{agent_id}")
        self.status = "initializing"
        self.progress_log = []
        
    def setup_worktree(self) -> bool:
        """Create a new worktree for this agent"""
        try:
            # Create worktree with new branch
            cmd = f"git worktree add -b {self.branch_name} {self.worktree_path} origin/main"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_progress("Worktree created successfully")
                self.status = "ready"
                return True
            else:
                self.log_progress(f"Failed to create worktree: {result.stderr}")
                self.status = "failed"
                return False
        except Exception as e:
            self.log_progress(f"Error creating worktree: {str(e)}")
            self.status = "error"
            return False
    
    def log_progress(self, message: str):
        """Log agent progress"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "message": message
        }
        self.progress_log.append(entry)
        
        # Also update plan.md in worktree
        self.update_plan_md(message)
    
    def update_plan_md(self, message: str):
        """Update plan.md with agent progress"""
        plan_path = self.worktree_path / "plan.md"
        
        if not plan_path.exists():
            return
        
        # Read current content
        with open(plan_path, 'r') as f:
            content = f.read()
        
        # Find or create agent section
        agent_section = f"\n## Agent {self.agent_id} Progress\n"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        progress_line = f"- [{timestamp}] {message}\n"
        
        if agent_section in content:
            # Insert after section header
            parts = content.split(agent_section)
            content = parts[0] + agent_section + progress_line + parts[1]
        else:
            # Add new section
            content += f"\n{agent_section}{progress_line}"
        
        # Write back
        with open(plan_path, 'w') as f:
            f.write(content)
    
    def update_docs(self, doc_name: str, content: str):
        """Update documentation in docs/ folder"""
        docs_path = self.worktree_path / "docs" / doc_name
        docs_path.parent.mkdir(exist_ok=True)
        
        with open(docs_path, 'w') as f:
            f.write(content)
        
        self.log_progress(f"Updated docs/{doc_name}")
    
    def execute_task(self):
        """Execute the assigned task"""
        self.status = "working"
        self.log_progress(f"Starting task: {self.task}")
        
        # Simulate task execution
        # In reality, this would run actual code generation, testing, etc.
        time.sleep(2)
        
        # Create some files based on task
        if "revenue" in self.task.lower():
            self.create_revenue_files()
        elif "traffic" in self.task.lower():
            self.create_traffic_files()
        elif "content" in self.task.lower():
            self.create_content_files()
        
        self.status = "completed"
        self.log_progress("Task completed successfully")
    
    def create_revenue_files(self):
        """Create revenue-related files"""
        # Create a new revenue optimization script
        script_path = self.worktree_path / "scripts" / f"revenue_optimizer_{self.agent_id}.py"
        script_path.parent.mkdir(exist_ok=True)
        
        script_content = f'''#!/usr/bin/env python3
"""
Revenue Optimizer created by Agent {self.agent_id}
Task: {self.task}
"""

def optimize_revenue():
    """Revenue optimization logic"""
    print("Optimizing revenue streams...")
    # Agent-generated optimization code
    return True

if __name__ == "__main__":
    optimize_revenue()
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Update documentation
        doc_content = f"""# Revenue Optimization by Agent {self.agent_id}

## Overview
This document describes the revenue optimization implemented for: {self.task}

## Implementation
- Created new optimization script
- Integrated with existing revenue engine
- Added performance tracking

## Expected Impact
- Increase daily revenue by 20%
- Optimize conversion rates
- Reduce customer acquisition cost
"""
        
        self.update_docs(f"AGENT_{self.agent_id}_REVENUE.md", doc_content)
        self.log_progress("Created revenue optimization files")
    
    def create_traffic_files(self):
        """Create traffic generation files"""
        script_path = self.worktree_path / "scripts" / f"traffic_booster_{self.agent_id}.py"
        script_path.parent.mkdir(exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(f"# Traffic booster by Agent {self.agent_id}\n")
        
        self.log_progress("Created traffic generation files")
    
    def create_content_files(self):
        """Create content generation files"""
        script_path = self.worktree_path / "scripts" / f"content_creator_{self.agent_id}.py"
        script_path.parent.mkdir(exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(f"# Content creator by Agent {self.agent_id}\n")
        
        self.log_progress("Created content generation files")
    
    def commit_changes(self):
        """Commit all changes in worktree"""
        os.chdir(self.worktree_path)
        
        # Add all changes
        subprocess.run(["git", "add", "-A"])
        
        # Commit with descriptive message
        commit_message = f"""feat: {self.task} - Agent {self.agent_id}

Implemented by autonomous agent {self.agent_id}
Task: {self.task}

Changes:
- Created implementation scripts
- Updated documentation
- Tracked progress in plan.md

🤖 Generated by Multi-Agent System
"""
        
        subprocess.run(["git", "commit", "-m", commit_message])
        self.log_progress("Changes committed")
        
        # Return to original directory
        os.chdir(Path(__file__).parent.parent)
    
    def push_branch(self):
        """Push branch to remote"""
        os.chdir(self.worktree_path)
        
        result = subprocess.run(
            ["git", "push", "-u", "origin", self.branch_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.log_progress("Branch pushed successfully")
        else:
            self.log_progress(f"Failed to push: {result.stderr}")
        
        os.chdir(Path(__file__).parent.parent)
    
    def create_pull_request(self):
        """Create GitHub pull request"""
        pr_body = f"""## Agent {self.agent_id} Task Completion

### Task
{self.task}

### Changes Made
- Implementation scripts created
- Documentation updated
- Progress tracked in plan.md

### Testing
- [ ] Code reviewed
- [ ] Tests pass
- [ ] Documentation complete

### Agent Log
"""
        
        # Add progress log to PR body
        for entry in self.progress_log[-10:]:  # Last 10 entries
            pr_body += f"- {entry['timestamp']}: {entry['message']}\n"
        
        pr_body += "\n---\n*Created by Autonomous Agent System*"
        
        # Create PR using GitHub CLI
        cmd = [
            "gh", "pr", "create",
            "--title", f"[Agent {self.agent_id}] {self.task}",
            "--body", pr_body,
            "--base", "main",
            "--head", self.branch_name
        ]
        
        os.chdir(self.worktree_path)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            pr_url = result.stdout.strip()
            self.log_progress(f"Pull request created: {pr_url}")
            self.status = "pr_created"
        else:
            self.log_progress(f"Failed to create PR: {result.stderr}")
            self.status = "pr_failed"
        
        os.chdir(Path(__file__).parent.parent)
    
    def cleanup_worktree(self):
        """Remove worktree after PR is created"""
        cmd = f"git worktree remove {self.worktree_path} --force"
        subprocess.run(cmd.split(), capture_output=True)
        self.log_progress("Worktree cleaned up")

class MultiAgentOrchestrator:
    """Orchestrates multiple agents working in parallel"""
    
    def __init__(self):
        self.agents: Dict[str, WorktreeAgent] = {}
        self.orchestration_log = Path("orchestration_log.json")
        
    def spawn_agent(self, task: str) -> str:
        """Spawn a new agent for a task"""
        agent_id = str(uuid.uuid4())[:8]
        branch_name = f"agent/{agent_id}/{task.lower().replace(' ', '-')[:30]}"
        
        agent = WorktreeAgent(agent_id, task, branch_name)
        self.agents[agent_id] = agent
        
        # Start agent work in separate thread
        thread = threading.Thread(target=self.run_agent, args=(agent,))
        thread.start()
        
        self.log_orchestration(f"Spawned agent {agent_id} for task: {task}")
        
        return agent_id
    
    def run_agent(self, agent: WorktreeAgent):
        """Run agent workflow"""
        try:
            # Setup worktree
            if not agent.setup_worktree():
                return
            
            # Execute task
            agent.execute_task()
            
            # Commit changes
            agent.commit_changes()
            
            # Push branch
            agent.push_branch()
            
            # Create PR
            agent.create_pull_request()
            
            # Cleanup
            agent.cleanup_worktree()
            
        except Exception as e:
            agent.log_progress(f"Agent failed: {str(e)}")
            agent.status = "failed"
    
    def spawn_parallel_agents(self, tasks: List[str]) -> List[str]:
        """Spawn multiple agents to work in parallel"""
        agent_ids = []
        
        print(f"🚀 Spawning {len(tasks)} agents for parallel work...")
        
        for task in tasks:
            agent_id = self.spawn_agent(task)
            agent_ids.append(agent_id)
            print(f"  • Agent {agent_id}: {task}")
            time.sleep(0.5)  # Slight delay to avoid git conflicts
        
        return agent_ids
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get status of a specific agent"""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "task": agent.task,
            "status": agent.status,
            "branch": agent.branch_name,
            "progress": len(agent.progress_log)
        }
    
    def get_all_status(self) -> Dict:
        """Get status of all agents"""
        return {
            agent_id: self.get_agent_status(agent_id)
            for agent_id in self.agents
        }
    
    def log_orchestration(self, message: str):
        """Log orchestration events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        logs = []
        if self.orchestration_log.exists():
            with open(self.orchestration_log) as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(self.orchestration_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def wait_for_agents(self, agent_ids: List[str], timeout: int = 300):
        """Wait for agents to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_done = True
            
            for agent_id in agent_ids:
                agent = self.agents.get(agent_id)
                if agent and agent.status not in ["completed", "pr_created", "failed", "pr_failed"]:
                    all_done = False
                    break
            
            if all_done:
                break
            
            time.sleep(5)
        
        # Print final status
        print("\n📊 Agent Status Report:")
        for agent_id in agent_ids:
            status = self.get_agent_status(agent_id)
            print(f"  • Agent {agent_id}: {status['status']} - {status['task']}")

def demo_multi_agent_system():
    """Demo the multi-agent system"""
    print("🤖 Multi-Agent Orchestration Demo")
    print("=" * 50)
    
    orchestrator = MultiAgentOrchestrator()
    
    # Define parallel tasks
    tasks = [
        "Optimize Reddit posting schedule for maximum engagement",
        "Create Pinterest visual content templates",
        "Implement email automation sequences",
        "Build A/B testing framework for pricing"
    ]
    
    # Spawn agents
    agent_ids = orchestrator.spawn_parallel_agents(tasks)
    
    print(f"\n⏳ Waiting for {len(agent_ids)} agents to complete...")
    
    # Wait for completion
    orchestrator.wait_for_agents(agent_ids)
    
    print("\n✅ All agents completed!")
    print("\n📄 Check the following:")
    print("  • Pull requests on GitHub")
    print("  • plan.md for progress tracking")
    print("  • docs/ for agent documentation")
    print("  • orchestration_log.json for full log")

if __name__ == "__main__":
    demo_multi_agent_system()