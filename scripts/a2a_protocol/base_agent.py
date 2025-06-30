#!/usr/bin/env python3
"""
Base A2A Agent implementation for the KindleMint Engine
Following Google's Agent-to-Agent protocol principles
"""

import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class A2AMessage:
    """Standard A2A message format"""

    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str  # 'request', 'response', 'error', 'notification'
    action: str
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None  # For request-response tracking

    @classmethod
    def create_request(
        cls, sender_id: str, receiver_id: str, action: str, payload: Dict
    ) -> "A2AMessage":
        """Create a new request message"""
        return cls(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type="request",
            action=action,
            payload=payload,
            timestamp=datetime.utcnow().isoformat(),
            correlation_id=None,
        )

    def create_response(self, sender_id: str, payload: Dict) -> "A2AMessage":
        """Create a response to this request"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=self.sender_id,
            message_type="response",
            action=self.action,
            payload=payload,
            timestamp=datetime.utcnow().isoformat(),
            correlation_id=self.message_id,
        )

    def create_error(self, sender_id: str, error_message: str) -> "A2AMessage":
        """Create an error response"""
        return A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=self.sender_id,
            message_type="error",
            action=self.action,
            payload={"error": error_message},
            timestamp=datetime.utcnow().isoformat(),
            correlation_id=self.message_id,
        )

    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "A2AMessage":
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class AgentCapability:
    """Describes a capability/skill of an agent"""

    name: str
    description: str
    input_schema: Dict[str, Any]  # JSON Schema for input validation
    output_schema: Dict[str, Any]  # JSON Schema for output


@dataclass
class AgentCard:
    """Agent identity and capabilities card"""

    agent_id: str
    agent_type: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    version: str
    status: str  # 'active', 'inactive', 'maintenance'

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability"""
        return any(cap.name == capability_name for cap in self.capabilities)


class A2AAgent(ABC):
    """Base class for all A2A agents"""

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        description: str,
        version: str = "1.0.0",
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.version = version
        self.status = "active"
        self.capabilities = self._define_capabilities()

        # Message handling
        self.message_handlers = self._register_handlers()

        # Create agent card
        self.card = AgentCard(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            name=self.name,
            description=self.description,
            capabilities=self.capabilities,
            version=self.version,
            status=self.status,
        )

        logger.info(f"Initialized agent: {self.name} ({self.agent_id})")

    @abstractmethod
    def _define_capabilities(self) -> List[AgentCapability]:
        """Define agent capabilities - must be implemented by subclasses"""
        pass

    @abstractmethod
    def _register_handlers(self) -> Dict[str, Any]:
        """Register message handlers - must be implemented by subclasses"""
        pass

    def process_message(self, message: A2AMessage) -> A2AMessage:
        """Process an incoming A2A message"""
        logger.info(f"Agent {self.agent_id} processing message: {message.action}")

        # Validate message
        if message.receiver_id != self.agent_id:
            return message.create_error(
                self.agent_id,
                f"Message not intended for this agent "
                f"(expected {self.agent_id}, got {message.receiver_id})",
            )

        # Check if we can handle this action
        if message.action not in self.message_handlers:
            return message.create_error(
                self.agent_id, f"Unknown action: {message.action}"
            )

        # Process the message
        try:
            handler = self.message_handlers[message.action]
            result = handler(message.payload)
            return message.create_response(self.agent_id, result)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return message.create_error(self.agent_id, str(e))

    def send_message(
        self,
        receiver_id: str,
        action: str,
        payload: Dict[str, Any],
        message_bus: Optional[Any] = None,
    ) -> Optional[A2AMessage]:
        """Send a message to another agent"""
        message = A2AMessage.create_request(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            action=action,
            payload=payload,
        )

        if message_bus:
            # Send via message bus (to be implemented)
            return message_bus.send(message)
        else:
            # Direct send (for testing)
            logger.info(f"Direct message sent: {message.action} to {receiver_id}")
            return message

    def get_card(self) -> Dict[str, Any]:
        """Get agent card as dictionary"""
        return asdict(self.card)

    def shutdown(self):
        """Gracefully shutdown the agent"""
        self.status = "inactive"
        logger.info(f"Agent {self.name} shutting down")


class A2ARegistry:
    """Central registry for A2A agents"""

    def __init__(self):
        self.agents: Dict[str, A2AAgent] = {}
        self.capabilities_index: Dict[str, List[str]] = {}  # capability -> [agent_ids]
        logger.info("A2A Registry initialized")

    def register(self, agent: A2AAgent):
        """Register an agent"""
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent {agent.agent_id} already registered")

        self.agents[agent.agent_id] = agent

        # Index capabilities
        for capability in agent.capabilities:
            if capability.name not in self.capabilities_index:
                self.capabilities_index[capability.name] = []
            self.capabilities_index[capability.name].append(agent.agent_id)

        logger.info(
            f"Registered agent: {agent.name} with {len(agent.capabilities)} capabilities"
        )

    def unregister(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]

            # Remove from capabilities index
            for capability in agent.capabilities:
                if capability.name in self.capabilities_index:
                    self.capabilities_index[capability.name].remove(agent_id)

            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    def find_agents_by_capability(self, capability_name: str) -> List[str]:
        """Find all agents with a specific capability"""
        return self.capabilities_index.get(capability_name, [])

    def get_agent(self, agent_id: str) -> Optional[A2AAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [agent.get_card() for agent in self.agents.values()]
