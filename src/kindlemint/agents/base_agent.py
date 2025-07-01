"""
Base Agent Implementation for KindleMint Multi-Agent System

This module provides the foundation class for all specialized agents in the
KindleMint publishing automation system, implementing core agent behaviors,
communication protocols, and performance monitoring.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

from .agent_types import AgentCapability
from .health_monitoring import HealthStatus
from .message_protocol import AgentMessage, MessageType
from .task_system import Task, TaskResult, TaskStatus


class AgentStatus(Enum):
    """Agent operational status"""

    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class AgentMetrics:
    """Performance metrics for agent monitoring"""

    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    success_rate: float = 100.0
    last_activity: datetime = field(default_factory=datetime.now)
    errors_last_hour: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


class BaseAgent(ABC):
    """
    Foundation class for all KindleMint agents

    Provides core functionality including:
    - Task execution and lifecycle management
    - Inter-agent communication
    - Performance monitoring and health checks
    - Error handling and recovery
    - Dynamic capability registration
    """

        """  Init  """


def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: str = "base",
        capabilities: Optional[List[AgentCapability]] = None,
        max_concurrent_tasks: int = 1,
        heartbeat_interval: int = 30,
    ):
        """
        Initialize base agent

        Args:
            agent_id: Unique identifier (auto-generated if None)
            agent_type: Type classification for the agent
            capabilities: List of agent capabilities
            max_concurrent_tasks: Maximum concurrent task limit
            heartbeat_interval: Health check interval in seconds
        """
        self.agent_id = agent_id or f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.capabilities = set(capabilities or [])
        self.max_concurrent_tasks = max_concurrent_tasks
        self.heartbeat_interval = heartbeat_interval

        # Agent state
        self.status = AgentStatus.INITIALIZING
        self.current_tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.message_queue: asyncio.Queue = asyncio.Queue()

        # Performance tracking
        self.metrics = AgentMetrics()
        self.health_status = HealthStatus()
        self.start_time = datetime.now()

        # Communication
        self.message_handlers: Dict[MessageType, callable] = {}

        # Logging
        self.logger = logging.getLogger(f"agent.{self.agent_id}")

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()

        self.logger.info(
            f"Agent {self.agent_id} initialized with capabilities: {self.capabilities}"
        )

    async def start(self) -> None:
        """Start the agent and begin processing tasks"""
        try:
            self.status = AgentStatus.IDLE
            self.logger.info(f"Starting agent {self.agent_id}")

            # Start background tasks
            self._background_tasks.add(asyncio.create_task(self._task_processor()))
            self._background_tasks.add(asyncio.create_task(self._message_processor()))
            self._background_tasks.add(asyncio.create_task(self._health_monitor()))

            # Agent-specific initialization
            await self._initialize()

            self.logger.info(f"Agent {self.agent_id} started successfully")

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Failed to start agent {self.agent_id}: {e}")
            raise

    async def stop(self) -> None:
        """Gracefully stop the agent"""
        self.logger.info(f"Stopping agent {self.agent_id}")
        self.status = AgentStatus.SHUTDOWN
        self._shutdown_event.set()

        # Wait for current tasks to complete (with timeout)
        try:
            await asyncio.wait_for(self._wait_for_tasks_completion(), timeout=30.0)
        except asyncio.TimeoutError:
            self.logger.warning("Task completion timeout, forcing shutdown")

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Agent-specific cleanup
        await self._cleanup()

        self.logger.info(f"Agent {self.agent_id} stopped")

    async def assign_task(self, task: Task) -> bool:
        """
        Assign a task to this agent

        Args:
            task: Task to execute

        Returns:
            True if task was accepted, False otherwise
        """
        if not self._can_accept_task(task):
            return False

        try:
            await self.task_queue.put(task)
            self.logger.info(f"Task {task.task_id} assigned to agent {self.agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to assign task {task.task_id}: {e}")
            return False

    async def send_message(self, message: AgentMessage) -> bool:
        """
        Send message to another agent

        Args:
            message: Message to send

        Returns:
            True if message was sent successfully
        """
        try:
            if self.agent_registry:
                return await self.agent_registry.route_message(message)
            else:
                self.logger.warning("No agent registry available for message routing")
                return False
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False

    def register_capability(self, capability: AgentCapability) -> None:
        """Register a new capability for this agent"""
        self.capabilities.add(capability)
        self.logger.info(f"Registered capability: {capability}")

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def get_health_status(self) -> HealthStatus:
        """Get current health status of the agent"""
        self.health_status.agent_id = self.agent_id
        self.health_status.status = self.status.value
        self.health_status.uptime = (datetime.now() - self.start_time).total_seconds()
        self.health_status.active_tasks = len(self.current_tasks)
        self.health_status.success_rate = self.metrics.success_rate
        self.health_status.last_heartbeat = datetime.now()

        return self.health_status

    def get_metrics(self) -> AgentMetrics:
        """Get current performance metrics"""
        return self.metrics

    # Abstract methods for subclass implementation
    @abstractmethod
    async def _execute_task(self, task: Task) -> TaskResult:
        """
        Execute a specific task (implemented by subclasses)

        Args:
            task: Task to execute

        Returns:
            Task execution result
        """

    @abstractmethod
    async def _initialize(self) -> None:
        """Agent-specific initialization logic"""

    @abstractmethod
    async def _cleanup(self) -> None:
        """Agent-specific cleanup logic"""

    # Private methods
    def _can_accept_task(self, task: Task) -> bool:
        """Check if agent can accept a new task"""
        if self.status != AgentStatus.IDLE:
            return False

        if len(self.current_tasks) >= self.max_concurrent_tasks:
            return False

        # Check if agent has required capabilities
        if task.required_capabilities:
            if not all(cap in self.capabilities for cap in task.required_capabilities):
                return False

        return True

    async def _task_processor(self) -> None:
        """Background task processor"""
        while not self._shutdown_event.is_set():
            try:
                # Wait for task with timeout to allow for shutdown
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                # Process the task
                await self._process_task(task)

            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")

    async def _process_task(self, task: Task) -> None:
        """Process a single task"""
        task_start_time = time.time()

        try:
            self.status = AgentStatus.BUSY
            self.current_tasks[task.task_id] = task
            task.status = TaskStatus.RUNNING
            task.assigned_agent = self.agent_id
            task.start_time = datetime.now()

            self.logger.info(f"Processing task {task.task_id}")

            # Execute the task
            result = await self._execute_task(task)

            # Update task status
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            task.end_time = datetime.now()
            task.result = result

            # Update metrics
            processing_time = time.time() - task_start_time
            self._update_metrics(
                success=result.success, processing_time=processing_time
            )

            self.logger.info(
                f"Task {task.task_id} {'completed' if result.success else 'failed'} "
                f"in {processing_time:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"Task {task.task_id} execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.end_time = datetime.now()
            task.error = str(e)

            processing_time = time.time() - task_start_time
            self._update_metrics(success=False, processing_time=processing_time)

        finally:
            # Clean up
            self.current_tasks.pop(task.task_id, None)
            if not self.current_tasks:
                self.status = AgentStatus.IDLE

    async def _message_processor(self) -> None:
        """Background message processor"""
        while not self._shutdown_event.is_set():
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)

                await self._handle_message(message)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in message processor: {e}")

    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle incoming message"""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                await handler(message)
            except Exception as e:
                self.logger.error(f"Error handling message {message.message_id}: {e}")
        else:
            self.logger.warning(f"No handler for message type: {message.message_type}")

    async def _health_monitor(self) -> None:
        """Background health monitoring"""
        while not self._shutdown_event.is_set():
            try:
                # Update health metrics
                self.health_status.cpu_usage = self._get_cpu_usage()
                self.health_status.memory_usage = self._get_memory_usage()

                # Send heartbeat if registry is available
                if self.agent_registry:
                    await self.agent_registry.update_agent_health(
                        self.agent_id, self.get_health_status()
                    )

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")

    def _update_metrics(self, success: bool, processing_time: float) -> None:
        """Update agent performance metrics"""
        if success:
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1

        self.metrics.total_processing_time += processing_time
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed

        if total_tasks > 0:
            self.metrics.average_processing_time = (
                self.metrics.total_processing_time / total_tasks
            )
            self.metrics.success_rate = self.metrics.tasks_completed / total_tasks * 100

        self.metrics.last_activity = datetime.now()

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage (placeholder implementation)"""
        # TODO: Implement actual CPU monitoring
        return 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage (placeholder implementation)"""
        # TODO: Implement actual memory monitoring
        return 0.0

    async def _wait_for_tasks_completion(self) -> None:
        """Wait for all current tasks to complete"""
        while self.current_tasks:
            await asyncio.sleep(0.1)

    def __repr__(self) -> str:
        return (
            f"Agent(id={self.agent_id}, type={self.agent_type}, "
            f"status={self.status.value}, capabilities={len(self.capabilities)})"
        )
