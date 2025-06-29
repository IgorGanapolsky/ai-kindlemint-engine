"""
Multi-Agent Framework for KindleMint Engine

This package implements a scalable multi-agent architecture for automated
book publishing with specialized agents for different aspects of the pipeline.
"""

from .agent_registry import AgentRegistry
from .base_agent import AgentCapability, AgentStatus, BaseAgent
from .github_issues_agent import GitHubActionType, GitHubIssuesAgent
from .health_monitoring import HealthMonitor, HealthStatus
from .message_protocol import AgentMessage, MessageType, Priority
from .task_system import Task, TaskResult, TaskStatus

__all__ = [
    "BaseAgent",
    "AgentStatus",
    "AgentCapability",
    "AgentMessage",
    "MessageType",
    "Priority",
    "Task",
    "TaskResult",
    "TaskStatus",
    "AgentRegistry",
    "HealthStatus",
    "HealthMonitor",
    "GitHubIssuesAgent",
    "GitHubActionType",
]

__version__ = "1.0.0"
