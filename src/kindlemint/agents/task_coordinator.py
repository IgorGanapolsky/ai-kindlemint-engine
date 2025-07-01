"""
Task Coordination System for KindleMint Multi-Agent Architecture

This module provides intelligent task orchestration, workflow management,
and agent coordination for the multi-agent book publishing system.
"""

import asyncio
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .base_agent import AgentCapability
from .message_protocol import AgentMessage, MessageType, Priority, create_task_request
from .task_system import Task, TaskPriority, TaskResult, TaskStatus, TaskType


class WorkflowStatus(Enum):
    """Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class WorkflowStep:
    """Represents a step in a workflow"""

    step_id: str
    task_template: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    retry_policy: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None


@dataclass
class Workflow:
    """Represents a complete workflow definition"""

    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Represents an active workflow execution"""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, TaskResult] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TaskCoordinator:
    """
    Intelligent task coordination and workflow management system
    """

        """  Init  """


def __init__(
        self,
        max_concurrent_workflows: int = 10,
        task_timeout_default: int = 1800,  # 30 minutes
        retry_delay_base: float = 2.0,
    ):
        """
        Initializes the TaskCoordinator with workflow concurrency limits, default task timeout, and retry delay settings.
        
        Parameters:
            max_concurrent_workflows (int): Maximum number of workflows that can be executed concurrently.
            task_timeout_default (int): Default timeout for individual tasks, in seconds.
            retry_delay_base (float): Base value for exponential backoff when retrying failed tasks.
        """
        self.agent_registry = agent_registry
        self.max_concurrent_workflows = max_concurrent_workflows
        self.task_timeout_default = task_timeout_default
        self.retry_delay_base = retry_delay_base

        # Task management
        self.active_tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.completed_tasks: Dict[str, Task] = {}

        # Workflow management
        self.workflows: Dict[str, Workflow] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []

        # Coordination state
        self.coordinator_active = False
        self.coordination_tasks: Set[asyncio.Task] = set()

        # Performance tracking
        self.task_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.workflow_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Dependencies and scheduling
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.waiting_tasks: Dict[str, Set[str]] = defaultdict(
            set
        )  # task_id -> dependencies

        self.logger = logging.getLogger("task_coordinator")

    async def start(self) -> None:
        """Start the task coordination system"""
        if self.coordinator_active:
            return

        self.coordinator_active = True

        # Start coordination tasks
        self.coordination_tasks.add(asyncio.create_task(self._task_scheduler()))
        self.coordination_tasks.add(asyncio.create_task(self._task_monitor()))
        self.coordination_tasks.add(asyncio.create_task(self._workflow_executor()))

        self.logger.info("Task coordinator started")

    async def stop(self) -> None:
        """Stop the task coordination system"""
        self.coordinator_active = False

        # Cancel all coordination tasks
        for task in self.coordination_tasks:
            task.cancel()

        await asyncio.gather(*self.coordination_tasks, return_exceptions=True)
        self.coordination_tasks.clear()

        self.logger.info("Task coordinator stopped")

    async def submit_task(self, task: Task, priority_boost: int = 0) -> str:
        """
        Submit a task for execution

        Args:
            task: Task to execute
            priority_boost: Additional priority boost (0-10)

        Returns:
            Task ID
        """
        # Calculate task priority score
        priority_score = self._calculate_priority_score(task.priority) + priority_boost

        # Add to queue
        await self.task_queue.put((priority_score, datetime.now(), task))

        # Track in active tasks
        self.active_tasks[task.task_id] = task

        self.logger.info(
            f"Submitted task {task.task_id} with priority {priority_score}"
        )
        return task.task_id

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        if task_id not in self.active_tasks:
            return False

        task = self.active_tasks[task_id]

        # Cancel the task
        task.mark_cancelled("Cancelled by coordinator")

        # Notify assigned agent if applicable
        if task.assigned_agent:
            cancel_message = AgentMessage(
                sender_id="task_coordinator",
                recipient_id=task.assigned_agent,
                message_type=MessageType.TASK_ASSIGNMENT,
                priority=Priority.HIGH,
                subject=f"Cancel Task {task_id}",
                payload={"action": "cancel", "task_id": task_id},
            )
            await self.agent_registry.route_message(cancel_message)

        # Move to completed tasks
        self.completed_tasks[task_id] = task
        self.active_tasks.pop(task_id, None)

        self.logger.info(f"Cancelled task {task_id}")
        return True

    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get current status of a task"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        return None

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result of a completed task"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].result
        return None

    def register_workflow(self, workflow: Workflow) -> bool:
        """Register a workflow template"""
        try:
            self.workflows[workflow.workflow_id] = workflow
            self.logger.info(f"Registered workflow: {workflow.workflow_id}")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to register workflow {workflow.workflow_id}: {e}"
            )
            return False

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        execution_id: Optional[str] = None,
    ) -> str:
        """
        Execute a workflow

        Args:
            workflow_id: ID of workflow to execute
            input_data: Input data for workflow
            execution_id: Optional custom execution ID

        Returns:
            Execution ID
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        if len(self.active_executions) >= self.max_concurrent_workflows:
            raise RuntimeError("Maximum concurrent workflows reached")

        # Create execution
        execution_id = execution_id or str(uuid.uuid4())
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            input_data=input_data,
        )

        self.active_executions[execution_id] = execution

        self.logger.info(f"Started workflow execution: {execution_id}")
        return execution_id

    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowStatus]:
        """Get workflow execution status"""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id].status

        # Check history
        for execution in self.execution_history:
            if execution.execution_id == execution_id:
                return execution.status

        return None

    async def get_workflow_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution result"""
        execution = None

        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
        else:
            # Check history
            for hist_execution in self.execution_history:
                if hist_execution.execution_id == execution_id:
                    execution = hist_execution
                    break

        if execution and execution.status == WorkflowStatus.COMPLETED:
            return execution.output_data

        return None

    def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get coordination system metrics"""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "active_workflows": len(self.active_executions),
            "registered_workflows": len(self.workflows),
            "queue_size": self.task_queue.qsize(),
            "task_metrics": dict(self.task_metrics),
            "workflow_metrics": dict(self.workflow_metrics),
        }

    # Private methods

    def _calculate_priority_score(self, priority: TaskPriority) -> int:
        """Calculate numeric priority score for queue ordering"""
        priority_map = {
            TaskPriority.CRITICAL: 100,
            TaskPriority.HIGH: 80,
            TaskPriority.NORMAL: 50,
            TaskPriority.LOW: 30,
            TaskPriority.BACKGROUND: 10,
        }
        return priority_map.get(priority, 50)

    async def _task_scheduler(self) -> None:
        """Main task scheduling loop"""
        while self.coordinator_active:
            try:
                # Get next task from queue
                try:
                    priority_score, timestamp, task = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Check if task is still valid
                if task.status == TaskStatus.CANCELLED:
                    continue

                # Check dependencies
                if not await self._check_task_dependencies(task):
                    # Re-queue task with delay
                    await asyncio.sleep(5)
                    await self.task_queue.put((priority_score, timestamp, task))
                    continue

                # Find suitable agent
                agent_id = await self._find_agent_for_task(task)
                if not agent_id:
                    # No agent available, re-queue with delay
                    await asyncio.sleep(10)
                    await self.task_queue.put((priority_score, timestamp, task))
                    continue

                # Assign task to agent
                await self._assign_task_to_agent(task, agent_id)

            except Exception as e:
                self.logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(1)

    async def _task_monitor(self) -> None:
        """Monitor running tasks for timeouts and failures"""
        while self.coordinator_active:
            try:
                current_time = datetime.now()

                # Check for timed out tasks
                for task_id, task in list(self.active_tasks.items()):
                    if task.status == TaskStatus.RUNNING and task.is_expired:
                        await self._handle_task_timeout(task)

                    # Check for stale assigned tasks
                    elif (
                        task.status == TaskStatus.ASSIGNED
                        and task.assigned_at
                        and (current_time - task.assigned_at).total_seconds()
                        > 300  # 5 minutes
                    ):
                        await self._handle_stale_assignment(task)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Task monitor error: {e}")
                await asyncio.sleep(30)

    async def _workflow_executor(self) -> None:
        """Execute workflow steps"""
        while self.coordinator_active:
            try:
                # Process each active workflow execution
                for execution_id in list(self.active_executions.keys()):
                    execution = self.active_executions[execution_id]

                    if execution.status == WorkflowStatus.PENDING:
                        await self._start_workflow_execution(execution)
                    elif execution.status == WorkflowStatus.RUNNING:
                        await self._continue_workflow_execution(execution)

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                self.logger.error(f"Workflow executor error: {e}")
                await asyncio.sleep(5)

    async def _check_task_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        if not task.dependencies:
            return True

        for dependency in task.dependencies:
            dep_task_id = dependency.task_id

            # Check if dependency task exists and is completed
            if dep_task_id in self.completed_tasks:
                dep_task = self.completed_tasks[dep_task_id]
                if dep_task.status != TaskStatus.COMPLETED and not dependency.optional:
                    return False
            elif dep_task_id in self.active_tasks:
                # Dependency still running
                if not dependency.optional:
                    return False
            else:
                # Dependency task not found
                if not dependency.optional:
                    return False

        return True

    async def _find_agent_for_task(self, task: Task) -> Optional[str]:
        """Find the best agent for a task"""
        return self.agent_registry.find_best_agent_for_task(
            required_capabilities=task.required_capabilities,
            preferred_agents=task.constraints.preferred_agents,
            excluded_agents=task.constraints.excluded_agents,
            load_balancing=True,
        )

    async def _assign_task_to_agent(self, task: Task, agent_id: str) -> bool:
        """Assign a task to a specific agent"""
        try:
            # Mark task as assigned
            task.mark_assigned(agent_id)

            # Update agent load
            await self.agent_registry.update_agent_load(agent_id, 1)

            # Send task request to agent
            task_message = create_task_request(
                sender_id="task_coordinator",
                recipient_id=agent_id,
                task_data=task.to_dict(),
                priority=(
                    Priority.HIGH
                    if task.priority == TaskPriority.CRITICAL
                    else Priority.NORMAL
                ),
            )

            success = await self.agent_registry.route_message(task_message)

            if success:
                self.logger.info(f"Assigned task {task.task_id} to agent {agent_id}")
                return True
            else:
                # Assignment failed, reset task
                task.status = TaskStatus.PENDING
                task.assigned_agent = None
                task.assigned_at = None
                await self.agent_registry.update_agent_load(agent_id, -1)
                return False

        except Exception as e:
            self.logger.error(
                f"Failed to assign task {task.task_id} to {agent_id}: {e}"
            )
            return False

    async def _handle_task_timeout(self, task: Task) -> None:
        """Handle task timeout"""
        self.logger.warning(f"Task {task.task_id} timed out")

        # Mark task as timed out
        task.status = TaskStatus.TIMEOUT
        task.end_time = datetime.now()

        # Update agent load
        if task.assigned_agent:
            await self.agent_registry.update_agent_load(task.assigned_agent, -1)

        # Check if task can be retried
        if task.can_retry:
            task.prepare_retry()
            await self.submit_task(task)
        else:
            # Move to completed tasks
            self.completed_tasks[task.task_id] = task
            self.active_tasks.pop(task.task_id, None)

    async def _handle_stale_assignment(self, task: Task) -> None:
        """Handle stale task assignment"""
        self.logger.warning(f"Task {task.task_id} assignment is stale")

        # Reset task to pending
        task.status = TaskStatus.PENDING
        if task.assigned_agent:
            await self.agent_registry.update_agent_load(task.assigned_agent, -1)
        task.assigned_agent = None
        task.assigned_at = None

        # Re-queue task
        priority_score = self._calculate_priority_score(task.priority)
        await self.task_queue.put((priority_score, datetime.now(), task))

    async def _start_workflow_execution(self, execution: WorkflowExecution) -> None:
        """Start a workflow execution"""
        workflow = self.workflows[execution.workflow_id]

        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now()

        self.logger.info(f"Starting workflow execution {execution.execution_id}")

        # Create tasks for initial steps (no dependencies)
        for step in workflow.steps:
            if not step.dependencies:
                await self._create_workflow_task(execution, step)

    async def _continue_workflow_execution(self, execution: WorkflowExecution) -> None:
        """Continue a running workflow execution"""
        workflow = self.workflows[execution.workflow_id]

        # Check if any new steps can be started
        for step in workflow.steps:
            if step.step_id not in execution.step_results:
                # Check if dependencies are satisfied
                dependencies_satisfied = all(
                    dep_id in execution.step_results
                    and execution.step_results[dep_id].success
                    for dep_id in step.dependencies
                )

                if dependencies_satisfied:
                    await self._create_workflow_task(execution, step)

        # Check if workflow is complete
        if len(execution.step_results) == len(workflow.steps):
            all_successful = all(
                result.success for result in execution.step_results.values()
            )

            if all_successful:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()

                # Collect output data from steps
                execution.output_data = {
                    step_id: result.output_data
                    for step_id, result in execution.step_results.items()
                }

                self.logger.info(
                    f"Workflow execution {
                        execution.execution_id} completed successfully"
                )
            else:
                execution.status = WorkflowStatus.FAILED
                execution.completed_at = datetime.now()
                execution.error_message = "One or more workflow steps failed"

                self.logger.error(f"Workflow execution {execution.execution_id} failed")

            # Move to history
            self.execution_history.append(execution)
            self.active_executions.pop(execution.execution_id, None)

    async def _create_workflow_task(
        self, execution: WorkflowExecution, step: WorkflowStep
    ) -> None:
        """Create a task for a workflow step"""
        # Build task from template
        task_data = step.task_template.copy()
        task_data.update(
            {
                "task_id": f"{execution.execution_id}_{step.step_id}",
                "workflow_id": execution.workflow_id,
                "parent_task_id": execution.execution_id,
                "context": {
                    "workflow_execution": execution.execution_id,
                    "step_id": step.step_id,
                    "input_data": execution.input_data,
                },
            }
        )

        # Create task
        task = Task(**task_data)

        # Set timeout if specified
        if step.timeout_seconds:
            task.constraints.max_execution_time = step.timeout_seconds

        # Submit task
        await self.submit_task(task)

        self.logger.info(
            f"Created workflow task {task.task_id} for step {step.step_id}"
        )


# Utility functions for creating common workflows


def create_book_generation_workflow() -> Workflow:
    """Create a standard book generation workflow"""
    steps = [
        WorkflowStep(
            step_id="generate_puzzles",
            task_template={
                "task_type": TaskType.GENERATE_PUZZLES,
                "name": "Generate puzzles",
                "priority": TaskPriority.NORMAL,
                "constraints": {
                    "required_capabilities": [AgentCapability.PUZZLE_CREATION],
                    "max_execution_time": 1800,
                },
            },
        ),
        WorkflowStep(
            step_id="create_pdf_layout",
            task_template={
                "task_type": TaskType.CREATE_PDF_LAYOUT,
                "name": "Create PDF layout",
                "priority": TaskPriority.NORMAL,
                "constraints": {
                    "required_capabilities": [AgentCapability.PDF_LAYOUT],
                    "max_execution_time": 900,
                },
            },
            dependencies=["generate_puzzles"],
        ),
        WorkflowStep(
            step_id="generate_epub",
            task_template={
                "task_type": TaskType.GENERATE_EPUB,
                "name": "Generate EPUB",
                "priority": TaskPriority.NORMAL,
                "constraints": {
                    "required_capabilities": [AgentCapability.EPUB_GENERATION],
                    "max_execution_time": 600,
                },
            },
            dependencies=["create_pdf_layout"],
        ),
        WorkflowStep(
            step_id="run_qa_validation",
            task_template={
                "task_type": TaskType.RUN_QA_TESTS,
                "name": "QA validation",
                "priority": TaskPriority.HIGH,
                "constraints": {
                    "required_capabilities": [AgentCapability.QUALITY_ASSURANCE],
                    "max_execution_time": 600,
                },
            },
            dependencies=["create_pdf_layout", "generate_epub"],
        ),
    ]

    return Workflow(
        workflow_id="book_generation_standard",
        name="Standard Book Generation",
        description="Complete book generation workflow with puzzles, PDF, EPUB, and QA",
        steps=steps,
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "puzzle_type": {"type": "string"},
                "puzzle_count": {"type": "integer"},
                "difficulty": {"type": "string"},
            },
            "required": ["title", "puzzle_type", "puzzle_count"],
        },
    )
