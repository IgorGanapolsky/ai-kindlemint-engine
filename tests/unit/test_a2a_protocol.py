#!/usr/bin/env python3
"""Tests for A2A Protocol implementation"""

import asyncio
from datetime import datetime

import pytest

from scripts.a2a_protocol.base_agent import (
    A2AAgent,
    A2AMessage,
    A2ARegistry,
    AgentCapability,
    AgentCard,
)
from scripts.a2a_protocol.message_bus import A2AMessageBus
from scripts.a2a_protocol.puzzle_validator_agent import PuzzleValidatorAgent


class TestAgent(A2AAgent):
    """Concrete test agent for testing base functionality"""

    def _define_capabilities(self):
        return [
            AgentCapability(
                name="test_capability",
                description="Test capability",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        ]

    def _register_handlers(self):
        return {
            "test_action": self._handle_test_action,
        }

    def _handle_test_action(self, payload):
        return {"status": "success", "result": "test completed"}


class TestA2AMessage:
    """Test A2A Message data structure"""

    def test_message_creation(self):
        """Test creating an A2A message"""
        msg = A2AMessage(
            message_id="test-123",
            sender_id="agent-1",
            receiver_id="agent-2",
            message_type="request",
            action="validate",
            payload={"data": "test"},
            timestamp=datetime.utcnow().isoformat(),
        )
        assert msg.message_id == "test-123"
        assert msg.sender_id == "agent-1"
        assert msg.receiver_id == "agent-2"
        assert msg.message_type == "request"
        assert msg.action == "validate"
        assert msg.payload == {"data": "test"}

    def test_message_with_correlation(self):
        """Test message with correlation ID"""
        msg = A2AMessage(
            message_id="test-456",
            sender_id="agent-1",
            receiver_id="agent-2",
            message_type="response",
            action="validate",
            payload={"result": "success"},
            timestamp=datetime.utcnow().isoformat(),
            correlation_id="test-123",
        )
        assert msg.correlation_id == "test-123"


class TestAgentCapability:
    """Test Agent Capability structure"""

    def test_capability_creation(self):
        """Test creating an agent capability"""
        cap = AgentCapability(
            name="validate_puzzle",
            description="Validates Sudoku puzzles",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        assert cap.name == "validate_puzzle"
        assert cap.description == "Validates Sudoku puzzles"
        assert cap.input_schema == {"type": "object"}
        assert cap.output_schema == {"type": "object"}


class TestAgentCard:
    """Test Agent Card structure"""

    def test_agent_card_creation(self):
        """Test creating an agent card"""
        cap = AgentCapability(
            name="test_cap",
            description="Test capability",
            input_schema={},
            output_schema={},
        )
        card = AgentCard(
            agent_id="test-agent",
            agent_type="test",
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            status="active",
            capabilities=[cap],
        )
        assert card.agent_id == "test-agent"
        assert card.name == "Test Agent"
        assert card.version == "1.0.0"
        assert len(card.capabilities) == 1
        assert card.capabilities[0].name == "test_cap"


class TestA2AAgent:
    """Test base A2A Agent class"""

    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = TestAgent(
            agent_id="test-agent",
            agent_type="test",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        assert agent.agent_id == "test-agent"
        assert agent.agent_type == "test"
        assert agent.name == "Test Agent"
        assert agent.description == "Test agent for unit tests"

    def test_agent_card_generation(self):
        """Test agent card generation"""
        agent = TestAgent(
            agent_id="test-agent",
            agent_type="test",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        card_dict = agent.get_card()
        assert card_dict["agent_id"] == "test-agent"
        assert card_dict["agent_type"] == "test"
        assert card_dict["name"] == "Test Agent"
        assert card_dict["description"] == "Test agent for unit tests"
        assert card_dict["version"] == "1.0.0"

    def test_process_message_success(self):
        """Test successful message processing"""
        agent = TestAgent(
            agent_id="test-agent",
            agent_type="test",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        msg = A2AMessage(
            message_id="test-123",
            sender_id="other-agent",
            receiver_id="test-agent",
            message_type="request",
            action="test_action",
            payload={},
            timestamp=datetime.utcnow().isoformat(),
        )
        response = agent.process_message(msg)
        assert response.message_type == "response"
        assert response.payload["status"] == "success"


class TestPuzzleValidatorAgent:
    """Test Puzzle Validator Agent"""

    @pytest.fixture
    def validator_agent(self):
        """Create a puzzle validator agent"""
        return PuzzleValidatorAgent()

    def test_validator_initialization(self, validator_agent):
        """Test validator agent initialization"""
        assert validator_agent.agent_id == "puzzle-validator-001"
        assert validator_agent.name == "Puzzle Validator"
        assert "puzzle" in validator_agent.description.lower()

        """Test Validator Capabilities"""


def test_validator_capabilities(self, validator_agent):
        """Test validator agent capabilities"""
        card_dict = validator_agent.get_card()
        capability_names = [cap["name"] for cap in card_dict["capabilities"]]
        assert "validate_puzzle" in capability_names
        assert "validate_batch" in capability_names
        assert "check_puzzle_quality" in capability_names

        """Test Validate Single Puzzle"""


def test_validate_single_puzzle(self, validator_agent):
        """Test validating a single puzzle"""
        # Valid Sudoku puzzle
        valid_puzzle = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

        msg = A2AMessage(
            message_id="test-123",
            sender_id="test-sender",
            receiver_id="puzzle-validator-001",
            message_type="request",
            action="validate_puzzle",
            payload={"puzzle_grid": valid_puzzle,
                "solution_grid": valid_puzzle},
            timestamp=datetime.utcnow().isoformat(),
        )

        response = validator_agent.process_message(msg)
        assert response is not None
        assert response.message_type == "response"
        assert response.payload["valid"] is True

        """Test Validate Invalid Puzzle"""


def test_validate_invalid_puzzle(self, validator_agent):
        """Test validating an invalid puzzle"""
        # Invalid Sudoku puzzle (duplicate 5 in first row)
        invalid_puzzle = [
            [5, 5, 4, 6, 7, 8, 9, 1, 2],  # Duplicate 5
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

        msg = A2AMessage(
            message_id="test-124",
            sender_id="test-sender",
            receiver_id="puzzle-validator-001",
            message_type="request",
            action="validate_puzzle",
            payload={"puzzle_grid": invalid_puzzle,
                "solution_grid": invalid_puzzle},
            timestamp=datetime.utcnow().isoformat(),
        )

        response = validator_agent.process_message(msg)
        assert response is not None
        assert response.message_type == "response"
        assert response.payload["valid"] is False
        assert "errors" in response.payload


class TestA2AMessageBus:
    """Test A2A Message Bus"""

    @pytest.fixture
        """Message Bus"""


def message_bus(self):
        """Create a message bus"""
        registry = A2ARegistry()
        return A2AMessageBus(registry)

    @pytest.mark.asyncio
    async     """Test Register Agent"""
def test_register_agent(self, message_bus):
        """Test registering an agent"""
        agent = PuzzleValidatorAgent()
        message_bus.registry.register(agent)
        assert "puzzle-validator-001" in message_bus.registry.agents

    @pytest.mark.asyncio
    async     """Test Send Message"""
def test_send_message(self, message_bus):
        """Test sending a message through the bus"""
        # Register an agent
        agent = PuzzleValidatorAgent()
        message_bus.registry.register(agent)

        # Start the message bus
        bus_task = asyncio.create_task(message_bus.start())

        # Send a message
        msg = A2AMessage(
            message_id="test-125",
            sender_id="test-sender",
            receiver_id="puzzle-validator-001",
            message_type="request",
            action="validate_puzzle",
            payload={
                "puzzle": [[0] * 9 for __var in range(9)],  # Empty puzzle
                "puzzle_id": "test-puzzle-3",
            },
            timestamp=datetime.utcnow().isoformat(),
        )

        response = await message_bus.send_message(msg)
        assert response is not None
        assert response.message_type == "response"

        # Cleanup
        await message_bus.stop()
        bus_task.cancel()
        try:
            await bus_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async     """Test Agent Not Found"""
def test_agent_not_found(self, message_bus):
        """Test sending message to non-existent agent"""
        # Start the message bus
        bus_task = asyncio.create_task(message_bus.start())

        # Send a message to non-existent agent
        msg = A2AMessage(
            message_id="test-126",
            sender_id="test-sender",
            receiver_id="non-existent-agent",
            message_type="request",
            action="test",
            payload={},
            timestamp=datetime.utcnow().isoformat(),
        )

        response = await message_bus.send_message(msg)
        assert response is not None
        assert response.message_type == "error"
        assert "not found" in response.payload["error"].lower()

        # Cleanup
        await message_bus.stop()
        bus_task.cancel()
        try:
            await bus_task
        except asyncio.CancelledError:
            pass


class TestA2AOrchestrator:
    """Test A2A Message Bus with Registry"""

    @pytest.fixture
        """Orchestrator"""
def orchestrator(self):
        """Create a message bus with registry"""
        registry = A2ARegistry()
        bus = A2AMessageBus(registry)
        return bus

        """Test Message Bus With Registry"""
def test_message_bus_with_registry(self, orchestrator):
        """Test message bus with registry functionality"""
        # Register validator agent
        validator = PuzzleValidatorAgent()
        orchestrator.registry.register(validator)

        # Check agent registration
        assert "puzzle-validator-001" in orchestrator.registry.agents

        # Check registry can find agents by capability
        puzzle_validators = orchestrator.registry.find_agents_by_capability(
            "validate_puzzle"
        )
        assert "puzzle-validator-001" in puzzle_validators


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
