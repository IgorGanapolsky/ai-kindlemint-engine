"""
Unified Orchestrator - Integrates Claude Code and A2A orchestration systems
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..a2a.pdf_layout_agent import create_pdf_layout_agent
from ..a2a.puzzle_generator_agent import create_puzzle_generator_agent
from ..a2a.registry import AgentRegistry
from .claude_code_orchestrator import (
    ClaudeCodeOrchestrator,
    OrchestrationTask,
    TaskType,
)


class OrchestrationMode(Enum):
    """Orchestration execution modes"""

    CLAUDE_CODE_ONLY = "claude_code_only"
    A2A_ONLY = "a2a_only"
    HYBRID = "hybrid"
    AUTO = "auto"


@dataclass
class UnifiedTask:
    """Unified task that can be handled by either orchestration system"""

    id: str
    type: str
    description: str
    parameters: Dict[str, Any]
    mode: OrchestrationMode = OrchestrationMode.AUTO
    priority: int = 5
    status: str = "pending"
    claude_code_task: Optional[OrchestrationTask] = None
    a2a_tasks: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class UnifiedOrchestrator:
    """
    Unified orchestrator that coordinates between Claude Code and A2A systems
    """

        """  Init  """
def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize Claude Code orchestrator
        self.claude_code = ClaudeCodeOrchestrator()

        # Initialize A2A system
        self.a2a_registry = AgentRegistry()
        self.a2a_agents = {}

        # Initialize A2A agents
        self._initialize_a2a_agents()

        # Task management
        self.active_tasks = {}
        self.completed_tasks = {}

        # Routing configuration
        self.task_routing = {
            "puzzle_generation": OrchestrationMode.A2A_ONLY,
            "pdf_creation": OrchestrationMode.A2A_ONLY,
            "code_development": OrchestrationMode.CLAUDE_CODE_ONLY,
            "feature_creation": OrchestrationMode.CLAUDE_CODE_ONLY,
            "book_production": OrchestrationMode.HYBRID,
            "quality_assurance": OrchestrationMode.HYBRID,
        }

        """ Initialize A2A Agents"""
def _initialize_a2a_agents(self):
        """Initialize A2A agents"""
        try:
            # Create puzzle generator agent
            self.a2a_agents["puzzle_generator"] = create_puzzle_generator_agent(
                self.a2a_registry
            )

            # Create PDF layout agent
            self.a2a_agents["pdf_layout"] = create_pdf_layout_agent(self.a2a_registry)

            self.logger.info(f"Initialized {len(self.a2a_agents)} A2A agents")

        except Exception as e:
            self.logger.error(f"Error initializing A2A agents: {e}")
            raise

    async def execute_task(self, task: UnifiedTask) -> Dict[str, Any]:
        """Execute a unified task using the appropriate orchestration system"""
        try:
            self.logger.info(f"Executing task {task.id}: {task.description}")

            # Store task
            self.active_tasks[task.id] = task
            task.status = "running"

            # Determine execution mode
            execution_mode = self._determine_execution_mode(task)

            # Execute based on mode
            if execution_mode == OrchestrationMode.CLAUDE_CODE_ONLY:
                result = await self._execute_claude_code_task(task)
            elif execution_mode == OrchestrationMode.A2A_ONLY:
                result = await self._execute_a2a_task(task)
            elif execution_mode == OrchestrationMode.HYBRID:
                result = await self._execute_hybrid_task(task)
            else:
                raise ValueError(f"Unknown execution mode: {execution_mode}")

            # Update task status
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result

            # Move to completed tasks
            self.completed_tasks[task.id] = task
            del self.active_tasks[task.id]

            return {
                "success": True,
                "task_id": task.id,
                "execution_mode": execution_mode.value,
                "result": result,
            }

        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            task.status = "failed"
            task.error = str(e)

            return {"success": False, "task_id": task.id, "error": str(e)}

    def _determine_execution_mode(self, task: UnifiedTask) -> OrchestrationMode:
        """Determine which orchestration system should handle the task"""
        if task.mode != OrchestrationMode.AUTO:
            return task.mode

        # Check routing configuration
        if task.type in self.task_routing:
            return self.task_routing[task.type]

        # Default routing logic
        if task.type in ["puzzle_generation", "pdf_creation", "validation"]:
            return OrchestrationMode.A2A_ONLY
        elif task.type in ["code_development", "feature_creation", "optimization"]:
            return OrchestrationMode.CLAUDE_CODE_ONLY
        else:
            return OrchestrationMode.HYBRID

    async def _execute_claude_code_task(self, task: UnifiedTask) -> Dict[str, Any]:
        """Execute task using Claude Code orchestrator"""
        try:
            # Convert to Claude Code task
            claude_task = OrchestrationTask(
                task_id=f"cc_{task.id}",
                task_type=task.type,
                description=task.description,
                parameters=task.parameters,
            )

            task.claude_code_task = claude_task

            # Execute using Claude Code orchestrator
            result = await self.claude_code.execute_task(claude_task)

            return {"orchestrator": "claude_code", "claude_code_result": result}

        except Exception as e:
            self.logger.error(f"Error in Claude Code execution: {e}")
            raise

    async def _execute_a2a_task(self, task: UnifiedTask) -> Dict[str, Any]:
        """Execute task using A2A protocol"""
        try:
            # Route to appropriate A2A agent
            if task.type == "puzzle_generation":
                agent = self.a2a_agents["puzzle_generator"]
                capability = (
                    "generate_puzzle_batch"
                    if task.parameters.get("count", 1) > 1
                    else "generate_single_puzzle"
                )
            elif task.type == "pdf_creation":
                agent = self.a2a_agents["pdf_layout"]
                capability = "create_puzzle_book"
            else:
                raise ValueError(f"No A2A agent available for task type: {task.type}")

            # Execute A2A task
            result = await agent.skills[capability].handler(task.parameters)

            # Store A2A task info
            a2a_task_info = {
                "agent_id": agent.agent_id,
                "capability": capability,
                "parameters": task.parameters,
                "result": result,
            }
            task.a2a_tasks.append(a2a_task_info)

            return {
                "orchestrator": "a2a",
                "agent_id": agent.agent_id,
                "capability": capability,
                "a2a_result": result,
            }

        except Exception as e:
            self.logger.error(f"Error in A2A execution: {e}")
            raise

    async def _execute_hybrid_task(self, task: UnifiedTask) -> Dict[str, Any]:
        """Execute task using both orchestration systems"""
        try:
            results = {}

            # Special handling for book production workflow
            if task.type == "book_production":
                results = await self._execute_book_production_workflow(task)
            elif task.type == "quality_assurance":
                results = await self._execute_qa_workflow(task)
            else:
                # Default hybrid execution: run both systems
                claude_result = await self._execute_claude_code_task(task)
                a2a_result = await self._execute_a2a_task(task)

                results = {
                    "orchestrator": "hybrid",
                    "claude_code": claude_result,
                    "a2a": a2a_result,
                }

            return results

        except Exception as e:
            self.logger.error(f"Error in hybrid execution: {e}")
            raise

    async def _execute_book_production_workflow(
        self, task: UnifiedTask
    ) -> Dict[str, Any]:
        """Execute complete book production workflow using both systems"""
        try:
            workflow_results = {}

            # Step 1: Generate puzzles using A2A
            if "puzzle_count" in task.parameters:
                puzzle_task = UnifiedTask(
                    id=f"{task.id}_puzzles",
                    type="puzzle_generation",
                    description="Generate puzzles for book",
                    parameters={
                        "count": task.parameters["puzzle_count"],
                        "difficulty": task.parameters.get("difficulty", "medium"),
                        "format": "both",
                    },
                )
                puzzle_result = await self._execute_a2a_task(puzzle_task)
                workflow_results["puzzle_generation"] = puzzle_result

            # Step 2: Create PDF layout using A2A
            if (
                workflow_results.get("puzzle_generation", {})
                .get("a2a_result", {})
                .get("success")
            ):
                puzzles = workflow_results["puzzle_generation"]["a2a_result"]["puzzles"]

                pdf_task = UnifiedTask(
                    id=f"{task.id}_pdf",
                    type="pdf_creation",
                    description="Create PDF book layout",
                    parameters={
                        "puzzles": puzzles,
                        "book_title": task.parameters.get("book_title", "Puzzle Book"),
                        "book_format": task.parameters.get("book_format", "paperback"),
                        "include_solutions": True,
                    },
                )
                pdf_result = await self._execute_a2a_task(pdf_task)
                workflow_results["pdf_creation"] = pdf_result

            # Step 3: Quality assurance using Claude Code
            qa_task = UnifiedTask(
                id=f"{task.id}_qa",
                type="quality_assurance",
                description="Perform quality assurance on book",
                parameters={
                    "check_puzzles": True,
                    "check_pdf": True,
                    "check_metadata": True,
                },
            )
            qa_result = await self._execute_claude_code_task(qa_task)
            workflow_results["quality_assurance"] = qa_result

            return {
                "orchestrator": "hybrid",
                "workflow": "book_production",
                "steps": workflow_results,
                "success": all(
                    step.get("a2a_result", {}).get("success", True)
                    or step.get("claude_code_result", {}).get("success", True)
                    for step in workflow_results.values()
                ),
            }

        except Exception as e:
            self.logger.error(f"Error in book production workflow: {e}")
            raise

    async def _execute_qa_workflow(self, task: UnifiedTask) -> Dict[str, Any]:
        """Execute quality assurance workflow using both systems"""
        try:
            qa_results = {}

            # A2A validation tasks
            if task.parameters.get("check_puzzles"):
                # Use puzzle validator agent
                validation_result = (
                    await self.a2a_agents["puzzle_generator"]
                    .skills["validate_puzzle_request"]
                    .handler(task.parameters)
                )
                qa_results["puzzle_validation"] = validation_result

            # Claude Code QA tasks
            if task.parameters.get("check_code"):
                code_qa_task = UnifiedTask(
                    id=f"{task.id}_code_qa",
                    type="code_optimization",
                    description="Perform code quality analysis",
                    parameters=task.parameters,
                )
                code_qa_result = await self._execute_claude_code_task(code_qa_task)
                qa_results["code_qa"] = code_qa_result

            return {
                "orchestrator": "hybrid",
                "workflow": "quality_assurance",
                "results": qa_results,
            }

        except Exception as e:
            self.logger.error(f"Error in QA workflow: {e}")
            raise

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status,
                "type": task.type,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "active": True,
            }
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status,
                "type": task.type,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "completed_at": (
                    task.completed_at.isoformat() if task.completed_at else None
                ),
                "active": False,
                "success": task.error is None,
                "error": task.error,
            }
        else:
            return {"error": f"Task {task_id} not found"}

    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks"""
        return [
            {
                "task_id": task.id,
                "type": task.type,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
            }
            for task in self.active_tasks.values()
        ]

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of both orchestration systems"""
        return {
            "unified_orchestrator": {
                "active_tasks": len(self.active_tasks),
                "completed_tasks": len(self.completed_tasks),
                "a2a_agents": len(self.a2a_agents),
                "status": "running",
            },
            "claude_code": {
                "status": "running",
                "capabilities": [task_type.value for task_type in TaskType],
            },
            "a2a_system": {
                "agents": [
                    {
                        "agent_id": agent.agent_id,
                        "capabilities": list(agent.skills.keys()),
                    }
                    for agent in self.a2a_agents.values()
                ],
                "registry_size": (
                    len(self.a2a_registry.agents)
                    if hasattr(self.a2a_registry, "agents")
                    else 0
                ),
            },
        }


# Factory function for easy instantiation
    """Create Unified Orchestrator"""
def create_unified_orchestrator():
    """Create and return a configured UnifiedOrchestrator"""
    return UnifiedOrchestrator()
