"""
Task Management System for KindleMint Multi-Agent Architecture

This module defines the task structure, status, and results for inter-agent
communication and coordination within the KindleMint publishing automation system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Current status of a task"""

    PENDING = "pending"  # Task has been created but not yet started
    IN_PROGRESS = "in_progress"  # Task is currently being executed
    COMPLETED = "completed"  # Task finished successfully
    FAILED = "failed"  # Task encountered an error and could not complete
    CANCELLED = "cancelled"  # Task was explicitly stopped
    PAUSED = "paused"  # Task is temporarily suspended
    QUEUED = "queued"  # Task is waiting in a queue for processing
    RETRYING = "retrying"  # Task failed but will be retried


@dataclass
class Task:
    """
    Represents a single task within the multi-agent system
    """

    task_id: str  # Unique identifier for the task
    task_type: (
        # Category or type of task (e.g., "content_generation", "image_processing")
        str
    )
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )  # Input parameters for the task
    created_at: datetime = field(
        default_factory=datetime.now
    )  # Timestamp of task creation
    status: TaskStatus = TaskStatus.PENDING  # Current status of the task
    # ID of the agent currently assigned to the task
    assigned_to: Optional[str] = None
    priority: int = 5  # Task priority (1-10, 10 being highest)
    due_date: Optional[datetime] = None  # Optional deadline for the task
    dependencies: List[str] = field(
        default_factory=list
    )  # List of task_ids this task depends on
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )  # Additional task-specific metadata

    def update_status(
        self, new_status: TaskStatus, assigned_to: Optional[str] = None
    ) -> None:
        """
        Update the task's status and optionally assign it to a new agent.

        Parameters:
            new_status (TaskStatus): The new status to set for the task.
            assigned_to (Optional[str]): The agent ID to assign the task to, if provided.
        """
        self.status = new_status
        if assigned_to:
            self.assigned_to = assigned_to

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the Task instance into a dictionary suitable for storage or transmission.

        Returns:
            dict: A dictionary representation of the task, with datetime fields in ISO format and status as a string.
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Deserialize a dictionary into a Task instance, converting ISO-formatted date strings and status values as needed.

        Parameters:
            data (Dict[str, Any]): Dictionary containing task attributes, with date fields as ISO strings and status as a string.

        Returns:
            Task: A Task object populated with the provided data.
        """
        created_at = datetime.fromisoformat(data["created_at"])
        status = TaskStatus(data["status"])
        due_date = (
            datetime.fromisoformat(
                data["due_date"]) if data["due_date"] else None
        )

        return cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            parameters=data["parameters"],
            created_at=created_at,
            status=status,
            assigned_to=data.get("assigned_to"),
            priority=data["priority"],
            due_date=due_date,
            dependencies=data["dependencies"],
            metadata=data["metadata"],
        )


@dataclass
class TaskResult:
    """
    Represents the result of a completed or failed task
    """

    task_id: str  # ID of the task this result belongs to
    status: TaskStatus  # Final status of the task (COMPLETED or FAILED)
    timestamp: datetime = field(
        default_factory=datetime.now
    )  # Time of result generation
    output: Dict[str, Any] = field(
        default_factory=dict)  # Output data from the task
    error: Optional[str] = None  # Error message if task failed
    logs: List[str] = field(
        default_factory=list
    )  # Log messages generated during task execution
    metrics: Dict[str, Any] = field(
        default_factory=dict
    )  # Performance metrics (e.g., execution time)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the TaskResult instance into a dictionary with ISO-formatted timestamp and string status.

        Returns:
            dict: A dictionary representation of the task result suitable for serialization.
        """
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "output": self.output,
            "error": self.error,
            "logs": self.logs,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """
        Deserialize a dictionary into a TaskResult instance.

        Parameters:
            data (dict): Dictionary containing task result data, with status as a string and timestamp in ISO format.

        Returns:
            TaskResult: The deserialized TaskResult object.
        """
        status = TaskStatus(data["status"])
        timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            task_id=data["task_id"],
            status=status,
            timestamp=timestamp,
            output=data["output"],
            error=data.get("error"),
            logs=data["logs"],
            metrics=data["metrics"],
        )
