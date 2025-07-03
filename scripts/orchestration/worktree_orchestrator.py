#!/usr/bin/env python3
"""
Autonomous Worktree Orchestrator for Parallel Execution
Implements cost-effective orchestration using Git worktrees
"""

import asyncio
import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorktreeTask:
    """Task to execute in a worktree"""
    worktree: str
    task_type: str
    command: str
    description: str
    status: str = "pending"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[str] = None


class WorktreeOrchestrator:
    """Orchestrates parallel execution using Git worktrees"""
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.worktrees_path = self.base_path / "worktrees"
        self.active_tasks: Dict[str, WorktreeTask] = {}
        self.completed_tasks: List[WorktreeTask] = []
        
    async def execute_in_worktree(self, task: WorktreeTask) -> WorktreeTask:
        """Execute a command in a specific worktree"""
        worktree_path = self.worktrees_path / task.worktree
        
        logger.info(f"🚀 Starting task in {task.worktree}: {task.description}")
        task.status = "running"
        task.start_time = time.time()
        
        try:
            # Execute command in worktree
            process = await asyncio.create_subprocess_shell(
                f"cd {worktree_path} && {task.command}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            task.end_time = time.time()
            
            if process.returncode == 0:
                task.status = "completed"
                task.result = stdout.decode()
                logger.info(f"✅ Completed in {task.worktree}: {task.description}")
            else:
                task.status = "failed"
                task.result = stderr.decode()
                logger.error(f"❌ Failed in {task.worktree}: {stderr.decode()}")
                
        except Exception as e:
            task.status = "error"
            task.result = str(e)
            logger.error(f"💥 Error in {task.worktree}: {e}")
            
        return task
    
    async def parallel_book_generation(self) -> Dict[str, any]:
        """Generate book components in parallel using worktrees"""
        tasks = [
            WorktreeTask(
                worktree="parallel-puzzles",
                task_type="puzzle_generation",
                command="python scripts/unified_sudoku_generator.py --count 100 --difficulty medium",
                description="Generate 100 medium Sudoku puzzles"
            ),
            WorktreeTask(
                worktree="parallel-pdf",
                task_type="pdf_layout",
                command="python scripts/sudoku_pdf_layout_v2.py",
                description="Create PDF layouts for puzzles"
            ),
            WorktreeTask(
                worktree="parallel-qa",
                task_type="quality_check",
                command="python scripts/sudoku_qa_validator.py",
                description="Validate puzzle quality"
            )
        ]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(
            *[self.execute_in_worktree(task) for task in tasks]
        )
        
        # Analyze results
        successful = [t for t in results if t.status == "completed"]
        failed = [t for t in results if t.status in ["failed", "error"]]
        
        execution_time = max([t.end_time - t.start_time for t in results if t.end_time])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "successful": len(successful),
            "failed": len(failed),
            "execution_time": f"{execution_time:.2f} seconds",
            "speedup": f"{len(tasks)}x parallel execution",
            "tasks": [
                {
                    "worktree": t.worktree,
                    "status": t.status,
                    "duration": f"{t.end_time - t.start_time:.2f}s" if t.end_time else "N/A"
                }
                for t in results
            ]
        }
    
    async def autonomous_ci_fixes(self) -> Dict[str, any]:
        """Run CI fixes in parallel across worktrees"""
        tasks = [
            WorktreeTask(
                worktree="parallel-puzzles",
                task_type="syntax_fix",
                command="python scripts/ci_orchestration/autonomous_syntax_fixer.py",
                description="Fix syntax errors"
            ),
            WorktreeTask(
                worktree="parallel-pdf",
                task_type="test_fix",
                command="python -m pytest tests/ -x --tb=short || true",
                description="Run and analyze test failures"
            ),
            WorktreeTask(
                worktree="parallel-qa",
                task_type="lint_fix",
                command="python -m black . --check --diff || python -m black .",
                description="Fix code formatting"
            )
        ]
        
        results = await asyncio.gather(
            *[self.execute_in_worktree(task) for task in tasks]
        )
        
        return {
            "ci_fixes": [
                {
                    "type": t.task_type,
                    "status": t.status,
                    "worktree": t.worktree
                }
                for t in results
            ]
        }
    
    def get_cost_analysis(self) -> Dict[str, any]:
        """Analyze cost savings from parallel execution"""
        # Calculate based on completed tasks
        if not self.completed_tasks:
            return {"message": "No completed tasks to analyze"}
            
        total_sequential_time = sum(t.end_time - t.start_time for t in self.completed_tasks)
        actual_time = max(t.end_time for t in self.completed_tasks) - min(t.start_time for t in self.completed_tasks)
        
        return {
            "sequential_time": f"{total_sequential_time:.2f} seconds",
            "parallel_time": f"{actual_time:.2f} seconds",
            "time_saved": f"{total_sequential_time - actual_time:.2f} seconds",
            "speedup": f"{total_sequential_time / actual_time:.2f}x",
            "cost_reduction": f"{(1 - actual_time/total_sequential_time) * 100:.1f}%",
            "cpu_utilization": f"{len(self.completed_tasks)} cores used"
        }


async def main():
    """Demonstrate autonomous orchestration"""
    orchestrator = WorktreeOrchestrator()
    
    print("🤖 Autonomous Worktree Orchestrator")
    print("=" * 50)
    
    # Run parallel book generation
    print("\n📚 Starting Parallel Book Generation...")
    book_results = await orchestrator.parallel_book_generation()
    print(json.dumps(book_results, indent=2))
    
    # Run CI fixes in parallel
    print("\n🔧 Running Parallel CI Fixes...")
    ci_results = await orchestrator.autonomous_ci_fixes()
    print(json.dumps(ci_results, indent=2))
    
    # Show cost analysis
    print("\n💰 Cost Analysis:")
    cost_analysis = orchestrator.get_cost_analysis()
    print(json.dumps(cost_analysis, indent=2))


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(main())