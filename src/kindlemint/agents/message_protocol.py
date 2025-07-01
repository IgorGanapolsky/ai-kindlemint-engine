"""
Agent Communication Protocol for KindleMint Multi-Agent System

This module defines the message structure and communication protocols
used for inter-agent communication within the KindleMint publishing
automation system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class MessageType(Enum):
    """Types of messages that can be sent between agents"""

    # Task-related messages
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_STATUS_UPDATE = "task_status_update"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"

    # Coordination messages
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_ALLOCATION = "resource_allocation"

    # Health and monitoring
    HEALTH_CHECK = "health_check"
    HEALTH_RESPONSE = "health_response"
    HEARTBEAT = "heartbeat"
    STATUS_UPDATE = "status_update"

    # Data and intelligence
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    INTELLIGENCE_SHARING = "intelligence_sharing"
    MARKET_UPDATE = "market_update"

    # Error handling
    ERROR_NOTIFICATION = "error_notification"
    RECOVERY_REQUEST = "recovery_request"
    FAILOVER_NOTIFICATION = "failover_notification"

    # System control
    SHUTDOWN_REQUEST = "shutdown_request"
    RESTART_REQUEST = "restart_request"
    CONFIG_UPDATE = "config_update"

    # General communication
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    REPLY = "reply"


class Priority(Enum):
    """Message priority levels"""

    CRITICAL = "critical"  # System-critical messages (failures, security)
    HIGH = "high"  # Important operational messages
    NORMAL = "normal"  # Standard communication
    LOW = "low"  # Background/informational messages


@dataclass
class AgentMessage:
    """
    Standard message structure for inter-agent communication
    """

    # Message identification
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""  # Can be specific agent ID or "broadcast"

    # Message metadata
    message_type: MessageType = MessageType.NOTIFICATION
    priority: Priority = Priority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # For request/response correlation

    # Message content
    subject: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

    # Delivery metadata
    ttl_seconds: int = 300  # Time to live in seconds
    retry_count: int = 0
    max_retries: int = 3
    requires_acknowledgment: bool = False

    # Routing information
    routing_key: Optional[str] = None
    target_capabilities: Optional[list] = (
        None  # Route to agents with these capabilities
    )

    def __post_init__(self):
        """Validate message after initialization"""
        if not self.sender_id:
            raise ValueError("sender_id is required")

        if not self.recipient_id:
            raise ValueError("recipient_id is required")

    @property
    def is_expired(self) -> bool:
        """Check if message has exceeded its TTL"""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl_seconds

    @property
    def can_retry(self) -> bool:
        """Check if message can be retried"""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment retry counter"""
        self.retry_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "subject": self.subject,
            "payload": self.payload,
            "ttl_seconds": self.ttl_seconds,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "requires_acknowledgment": self.requires_acknowledgment,
            "routing_key": self.routing_key,
            "target_capabilities": self.target_capabilities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        # Convert string timestamp back to datetime
        timestamp = datetime.fromisoformat(data["timestamp"])

        # Convert enum strings back to enums
        message_type = MessageType(data["message_type"])
        priority = Priority(data["priority"])

        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=message_type,
            priority=priority,
            timestamp=timestamp,
            correlation_id=data.get("correlation_id"),
            subject=data["subject"],
            payload=data["payload"],
            ttl_seconds=data["ttl_seconds"],
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
            requires_acknowledgment=data["requires_acknowledgment"],
            routing_key=data.get("routing_key"),
            target_capabilities=data.get("target_capabilities"),
        )

    def create_reply(
        self,
        sender_id: str,
        message_type: MessageType = MessageType.REPLY,
        payload: Optional[Dict[str, Any]] = None,
    ) -> "AgentMessage":
        """Create a reply message to this message"""
        return AgentMessage(
            sender_id=sender_id,
            recipient_id=self.sender_id,
            message_type=message_type,
            priority=self.priority,
            correlation_id=self.message_id,  # Link reply to original message
            subject=f"Re: {self.subject}",
            payload=payload or {},
            requires_acknowledgment=False,
        )

    def create_acknowledgment(self, sender_id: str) -> "AgentMessage":
        """Create an acknowledgment message"""
        return AgentMessage(
            sender_id=sender_id,
            recipient_id=self.sender_id,
            message_type=MessageType.REPLY,
            priority=Priority.LOW,
            correlation_id=self.message_id,
            subject=f"ACK: {self.subject}",
            payload={"acknowledged": True, "original_message_id": self.message_id},
            requires_acknowledgment=False,
        )

    def __repr__(self) -> str:
        return (
            f"AgentMessage(id={self.message_id[:8]}, "
            f"from={self.sender_id}, to={self.recipient_id}, "
            f"type={self.message_type.value}, priority={self.priority.value})"
        )


# Utility functions for creating common message types


def create_task_request(
    sender_id: str,
    recipient_id: str,
    task_data: Dict[str, Any],
    priority: Priority = Priority.NORMAL,
) -> AgentMessage:
    """Create a task request message"""
    return AgentMessage(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_type=MessageType.TASK_REQUEST,
        priority=priority,
        subject="Task Request",
        payload=task_data,
        requires_acknowledgment=True,
    )


def create_task_completion(
    sender_id: str,
    recipient_id: str,
    task_id: str,
    result_data: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> AgentMessage:
    """Create a task completion message"""
    return AgentMessage(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_type=MessageType.TASK_COMPLETION,
        priority=Priority.HIGH,
        correlation_id=correlation_id,
        subject=f"Task Completed: {task_id}",
        payload={"task_id": task_id, "result": result_data},
        requires_acknowledgment=True,
    )


def create_error_notification(
    sender_id: str,
    recipient_id: str,
    error_message: str,
    error_data: Optional[Dict[str, Any]] = None,
    priority: Priority = Priority.CRITICAL,
) -> AgentMessage:
    """Create an error notification message"""
    return AgentMessage(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_type=MessageType.ERROR_NOTIFICATION,
        priority=priority,
        subject=f"Error: {error_message}",
        payload={"error": error_message, "data": error_data or {}},
        requires_acknowledgment=True,
    )


def create_heartbeat(sender_id: str, health_data: Dict[str, Any]) -> AgentMessage:
    """Create a heartbeat message"""
    return AgentMessage(
        sender_id=sender_id,
        recipient_id="broadcast",  # Heartbeats are typically broadcast
        message_type=MessageType.HEARTBEAT,
        priority=Priority.LOW,
        subject="Heartbeat",
        payload=health_data,
        requires_acknowledgment=False,
        ttl_seconds=60,  # Short TTL for heartbeats
    )


def create_broadcast(
    sender_id: str,
    subject: str,
    payload: Dict[str, Any],
    priority: Priority = Priority.NORMAL,
    target_capabilities: Optional[list] = None,
) -> AgentMessage:
    """Create a broadcast message"""
    return AgentMessage(
        sender_id=sender_id,
        recipient_id="broadcast",
        message_type=MessageType.BROADCAST,
        priority=priority,
        subject=subject,
        payload=payload,
        target_capabilities=target_capabilities,
        requires_acknowledgment=False,
    )