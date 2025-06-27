"""
Multi-Agent Framework for KindleMint Engine

This package implements a scalable multi-agent architecture for automated
book publishing with specialized agents for different aspects of the pipeline.
"""

from .base_agent import BaseAgent, AgentStatus, AgentCapability
from .message_protocol import AgentMessage, MessageType, Priority
from .task_system import Task, TaskResult, TaskStatus
from .agent_registry import AgentRegistry
from .health_monitoring import HealthStatus, HealthMonitor

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
]

__version__ = "1.0.0"