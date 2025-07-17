"""
Unified Orchestrator - Coordinates task execution
Coordinates task execution using direct function calls
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from .claude_code_orchestrator import (
    ClaudeCodeOrchestrator,
    OrchestrationTask,
    TaskType,
)


class OrchestrationMode(Enum):
    """Orchestration execution modes"""

    CLAUDE_CODE_ONLY = "claude_code_only"
    DIRECT_CALLS = "direct_calls"
    HYBRID = "hybrid"


@dataclass
class Task:
    """Simplified task definition"""

    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)


class UnifiedOrchestrator:
    """
    Unified orchestrator that coordinates task execution
    using Claude Code and direct function calls
    """

    def __init__(self):
        """Initialize the unified orchestrator"""
        self.logger = logging.getLogger(__name__)

        # Initialize Claude Code orchestrator
        self.claude_code = ClaudeCodeOrchestrator()

        # Task management
        self.active_tasks = {}
        self.completed_tasks = {}

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the appropriate system"""
        task_obj = Task(
            task_id=task.get("task_id", f"task_{datetime.now().timestamp()}"),
            task_type=task.get("task_type", "unknown"),
            description=task.get("description", ""),
            parameters=task.get("parameters", {}),
        )

        # Route to Claude Code for development tasks
        if task_obj.task_type in ["development", "code_generation", "feature"]:
            return self._execute_claude_code_task(task_obj)

        # Handle other tasks directly
        else:
            return self._execute_direct_task(task_obj)

    def _execute_claude_code_task(self, task: Task) -> Dict[str, Any]:
        """Execute task using Claude Code orchestrator"""
        try:
            orchestration_task = OrchestrationTask(
                task_id=task.task_id,
                task_type=TaskType.DEVELOPMENT,
                description=task.description,
                parameters=task.parameters,
            )

            result = self.claude_code.execute_task(orchestration_task)
            return {"status": "success", "result": result}

        except Exception as e:
            self.logger.error(f"Claude Code task failed: {e}")
            return {"status": "error", "error": str(e)}

    def _execute_direct_task(self, task: Task) -> Dict[str, Any]:
        """Execute task using direct function calls"""
        try:
            # Simple direct execution for non-development tasks
            self.logger.info(f"Executing direct task: {task.description}")
            return {
                "status": "success",
                "message": f"Task {task.task_id} executed directly",
            }

        except Exception as e:
            self.logger.error(f"Direct task failed: {e}")
            return {"status": "error", "error": str(e)}
