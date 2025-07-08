#!/usr/bin/env python3
"""
Optimized Worktree Manager - Parallel execution with cost tracking
"""

import asyncio
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
from security import safe_command

class TokenCostTracker:
    """Track API token usage and costs"""
    
    def __init__(self):
        self.usage_file = Path('.worktree-cache/token_usage.json')
        self.usage_file.parent.mkdir(exist_ok=True)
        
        # Claude API pricing (approximate)
        self.cost_per_1k_tokens = {
            'input': 0.015,   # $15 per million input tokens
            'output': 0.075   # $75 per million output tokens
        }
        
    async def get_current_usage(self) -> int:
        """Get current token usage"""
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                data = json.load(f)
                return data.get('total_tokens', 0)
        return 0
    
    def calculate_cost(self, tokens: int) -> float:
        """Calculate cost for token usage"""
        # Assume 50/50 split between input and output
        input_tokens = tokens * 0.5
        output_tokens = tokens * 0.5
        
        input_cost = (input_tokens / 1000) * self.cost_per_1k_tokens['input']
        output_cost = (output_tokens / 1000) * self.cost_per_1k_tokens['output']
        
        return input_cost + output_cost

class OptimizedWorktreeManager:
    """
    Optimized worktree orchestration with cost tracking and parallelization
    """
    
    def __init__(self):
        self.max_concurrent = 6  # Optimal for most machines
        self.worktrees = {}
        self.cost_tracker = TokenCostTracker()
        self.cache_dir = Path(".worktree-cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    async def execute_parallel_tasks(self, tasks: List[Dict]) -> Dict:
        """Execute tasks in parallel with intelligent batching"""
        
        # Group tasks by type for better cache utilization
        grouped = self.group_tasks_by_type(tasks)
        results = []
        
        # Use semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def run_task_with_tracking(task):
            async with semaphore:
                start_tokens = await self.cost_tracker.get_current_usage()
                result = await self.execute_in_worktree(task)
                end_tokens = await self.cost_tracker.get_current_usage()
                
                # Track cost
                tokens_used = end_tokens - start_tokens
                cost = self.cost_tracker.calculate_cost(tokens_used)
                
                return {
                    "task": task,
                    "result": result,
                    "tokens_used": tokens_used,
                    "cost": cost
                }
        
        # Execute all tasks in parallel
        print(f"🚀 Executing {len(tasks)} tasks in parallel...")
        start_time = datetime.now()
        
        all_results = await asyncio.gather(
            *[run_task_with_tracking(task) for task in tasks],
            return_exceptions=True
        )
        
        # Handle results and exceptions
        for result in all_results:
            if isinstance(result, Exception):
                print(f"❌ Task failed: {result}")
            else:
                results.append(result)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Generate cost report
        total_cost = sum(r["cost"] for r in results if isinstance(r, dict))
        total_tokens = sum(r["tokens_used"] for r in results if isinstance(r, dict))
        
        self.generate_cost_report({
            "tasks_executed": len(tasks),
            "successful_tasks": len(results),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_cost_per_task": total_cost / len(tasks) if tasks else 0,
            "duration_seconds": duration
        })
        
        return {
            "results": results,
            "summary": {
                "total_tasks": len(tasks),
                "successful": len(results),
                "total_cost": total_cost,
                "duration": duration
            }
        }
    
    def group_tasks_by_type(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Group similar tasks for better performance"""
        grouped = {}
        for task in tasks:
            task_type = task.get("type", "general")
            if task_type not in grouped:
                grouped[task_type] = []
            grouped[task_type].append(task)
        return grouped
    
    async def execute_in_worktree(self, task: Dict) -> Dict:
        """Execute a task in an appropriate worktree"""
        # Get or create worktree for this task type
        worktree_name = f"{task['type']}-{task.get('branch', 'main')}"
        worktree_path = await self.get_or_create_worktree(worktree_name, task.get('branch', 'main'))
        
        # Check cache first
        cache_key = self.generate_cache_key(task)
        cached_result = self.get_cached_result(cache_key)
        if cached_result and not task.get('force_refresh', False):
            print(f"✅ Cache hit for {task['type']}")
            return cached_result
        
        # Execute the task
        print(f"🔧 Executing {task['type']} in {worktree_name}")
        result = await self.run_command_in_worktree(
            worktree_path, 
            task["command"]
        )
        
        # Cache the result
        self.cache_result(cache_key, result)
        
        return result
    
    async def get_or_create_worktree(self, name: str, branch: str = 'main') -> Path:
        """Get existing or create new worktree"""
        worktree_path = Path(f"../{name}")
        
        if not worktree_path.exists():
            print(f"📁 Creating worktree: {name}")
            cmd = ['git', 'worktree', 'add', str(worktree_path), branch]
            safe_command.run(subprocess.run, cmd, check=True, capture_output=True)
            
        self.worktrees[name] = worktree_path
        return worktree_path
    
    async def run_command_in_worktree(self, worktree_path: Path, command: str) -> Dict:
        """Run command in specific worktree"""
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=str(worktree_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode('utf-8'),
            "stderr": stderr.decode('utf-8'),
            "returncode": process.returncode
        }
    
    def generate_cache_key(self, task: Dict) -> str:
        """Generate cache key for task"""
        task_str = json.dumps(task, sort_keys=True)
        return hashlib.md5(task_str.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if available"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            # Check if cache is fresh (1 hour)
            if (datetime.now().timestamp() - cache_file.stat().st_mtime) < 3600:
                with open(cache_file, 'r') as f:
                    return json.load(f)
        return None
    
    def cache_result(self, cache_key: str, result: Dict):
        """Cache task result"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    
    def generate_cost_report(self, metrics: Dict):
        """Generate cost optimization report"""
        report_path = Path("reports/orchestration/cost_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "recommendations": self.generate_recommendations(metrics)
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"""
📊 Worktree Orchestration Summary
================================
Tasks executed: {metrics['tasks_executed']}
Successful: {metrics['successful_tasks']}
Total cost: ${metrics['total_cost']:.4f}
Average cost per task: ${metrics['average_cost_per_task']:.4f}
Duration: {metrics['duration_seconds']:.1f}s
""")
    
    def generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        if metrics["average_cost_per_task"] > 0.10:
            recommendations.append(
                "Consider batching smaller tasks together to reduce overhead"
            )
        
        if metrics["total_tokens"] > 50000:
            recommendations.append(
                "High token usage detected. Consider using more specific prompts"
            )
        
        if metrics["duration_seconds"] > 300:
            recommendations.append(
                "Long execution time. Consider increasing parallelization"
            )
        
        return recommendations
    
    async def cleanup_worktrees(self):
        """Clean up unused worktrees"""
        print("🧹 Cleaning up worktrees...")
        
        result = subprocess.run(
            ['git', 'worktree', 'list', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('worktree '):
                path = line.split(' ', 1)[1]
                if path != '.' and not Path(path).exists():
                    print(f"Removing stale worktree: {path}")
                    subprocess.run(['git', 'worktree', 'prune'], check=True)

# Usage example
async def main():
    manager = OptimizedWorktreeManager()
    
    # Example tasks
    tasks = [
        {
            "type": "test",
            "command": "python -m pytest tests/ -v",
            "branch": "feature/testing"
        },
        {
            "type": "build",
            "command": "python setup.py build",
            "branch": "main"
        },
        {
            "type": "lint",
            "command": "flake8 src/ --max-line-length=100",
            "branch": "feature/testing"
        },
        {
            "type": "security",
            "command": "bandit -r src/",
            "branch": "main"
        }
    ]
    
    # Execute tasks in parallel
    results = await manager.execute_parallel_tasks(tasks)
    
    # Cleanup
    await manager.cleanup_worktrees()
    
    print(f"\n✅ All tasks completed!")
    print(f"Total cost: ${results['summary']['total_cost']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
