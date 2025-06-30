#!/usr/bin/env python3
"""Fixed tests for A2A Protocol implementation"""

import asyncio
from datetime import datetime
from typing import List

import pytest

from scripts.a2a_protocol.base_agent import (
    A2AAgent,
    A2AMessage,
    A2ARegistry,
    AgentCapability,
    AgentCard,
)
from scripts.a2a_protocol.message_bus import A2AMessageBus, A2AOrchestrator
from scripts.a2a_protocol.puzzle_validator_agent import PuzzleValidatorAgent


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
            timestamp=datetime.now().isoformat(),
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
            timestamp=datetime.now().isoformat(),
            correlation_id="test-123",
        )
        assert msg.correlation_id == "test-123"

    def test_create_request(self):
        """Test creating a request message"""
        msg = A2AMessage.create_request(
            sender_id="agent-1",
            receiver_id="agent-2",
            action="validate",
            payload={"data": "test"},
        )
        assert msg.message_type == "request"
        assert msg.sender_id == "agent-1"
        assert msg.receiver_id == "agent-2"
        assert msg.action == "validate"


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
            agent_type="validator",
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            status="active",
            capabilities=[cap],
        )
        assert card.agent_id == "test-agent"
        assert card.agent_type == "validator"
        assert card.name == "Test Agent"
        assert card.version == "1.0.0"
        assert card.status == "active"
        assert len(card.capabilities) == 1
        assert card.capabilities[0].name == "test_cap"


class ConcreteTestAgent(A2AAgent):
    """Concrete implementation of A2AAgent for testing"""

    def _define_capabilities(self) -> List[AgentCapability]:
        """Define test capabilities"""
        return [
            AgentCapability(
                name="test_action",
                description="Test action",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        ]

    def _register_handlers(self) -> None:
        """Register test handlers"""
        self.handlers["test_action"] = self._handle_test_action

    async def _handle_test_action(self, message: A2AMessage) -> A2AMessage:
        """Handle test action"""
        return message.create_response(
            sender_id=self.agent_id,
            payload={"status": "success", "result": "test completed"},
        )


class TestA2AAgent:
    """Test base A2A Agent class"""

    def test_agent_initialization(self):
        """Test agent initialization with concrete implementation"""
        agent = ConcreteTestAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        assert agent.agent_id == "test-agent"
        assert agent.name == "Test Agent"
        assert agent.description == "Test agent for unit tests"

    def test_agent_card_generation(self):
        """Test agent card generation"""
        agent = ConcreteTestAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        card = agent.agent_card
        assert card.agent_id == "test-agent"
        assert card.name == "Test Agent"
        assert card.description == "Test agent for unit tests"
        assert card.version == "1.0.0"
        assert card.status == "active"

    @pytest.mark.asyncio
    async def test_handle_known_action(self):
        """Test handling a known action"""
        agent = ConcreteTestAgent(
            agent_id="test-agent",
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
            timestamp=datetime.now().isoformat(),
        )
        response = await agent.receive_message(msg)
        assert response.message_type == "response"
        assert response.payload["status"] == "success"

    @pytest.mark.asyncio
    async def test_handle_unknown_action(self):
        """Test handling an unknown action"""
        agent = ConcreteTestAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        msg = A2AMessage(
            message_id="test-124",
            sender_id="other-agent",
            receiver_id="test-agent",
            message_type="request",
            action="unknown_action",
            payload={},
            timestamp=datetime.now().isoformat(),
        )
        response = await agent.receive_message(msg)
        assert response.message_type == "error"
        assert "Unknown action" in response.payload["error"]


class TestPuzzleValidatorAgent:
    """Test Puzzle Validator Agent"""

    @pytest.fixture
    def validator_agent(self):
        """Create a puzzle validator agent"""
        return PuzzleValidatorAgent()

    def test_validator_initialization(self, validator_agent):
        """Test validator agent initialization"""
        assert validator_agent.agent_id == "puzzle-validator-001"
        assert validator_agent.name == "Puzzle Validator Agent"
        assert "sudoku puzzle" in validator_agent.description.lower()

    def test_validator_capabilities(self, validator_agent):
        """Test validator agent capabilities"""
        card = validator_agent.agent_card
        capability_names = [cap.name for cap in card.capabilities]
        assert "validate_puzzle" in capability_names
        assert "validate_batch" in capability_names

    @pytest.mark.asyncio
    async def test_validate_single_puzzle(self, validator_agent):
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
            payload={"puzzle": valid_puzzle, "puzzle_id": "test-puzzle-1"},
            timestamp=datetime.now().isoformat(),
        )

        response = await validator_agent.receive_message(msg)
        assert response is not None
        assert response.message_type == "response"
        assert response.payload["status"] == "success"
        assert response.payload["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_invalid_puzzle(self, validator_agent):
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
            payload={"puzzle": invalid_puzzle, "puzzle_id": "test-puzzle-2"},
            timestamp=datetime.now().isoformat(),
        )

        response = await validator_agent.receive_message(msg)
        assert response is not None
        assert response.message_type == "response"
        assert response.payload["status"] == "success"
        assert response.payload["valid"] is False
        assert "issues" in response.payload


class TestA2ARegistry:
    """Test A2A Registry"""

    def test_registry_creation(self):
        """Test creating a registry"""
        registry = A2ARegistry()
        assert registry.agents == {}

    def test_register_agent(self):
        """Test registering an agent"""
        registry = A2ARegistry()
        agent = ConcreteTestAgent("test-1", "Test Agent", "Test")
        registry.register_agent(agent.agent_card)
        assert "test-1" in registry.agents
        assert registry.agents["test-1"].name == "Test Agent"

    def test_get_agent(self):
        """Test getting an agent"""
        registry = A2ARegistry()
        agent = ConcreteTestAgent("test-1", "Test Agent", "Test")
        registry.register_agent(agent.agent_card)
        card = registry.get_agent("test-1")
        assert card is not None
        assert card.name == "Test Agent"

    def test_find_agents_by_capability(self):
        """Test finding agents by capability"""
        registry = A2ARegistry()
        agent = ConcreteTestAgent("test-1", "Test Agent", "Test")
        registry.register_agent(agent.agent_card)
        agents = registry.find_agents_by_capability("test_action")
        assert len(agents) == 1
        assert agents[0].agent_id == "test-1"


class TestA2AMessageBus:
    """Test A2A Message Bus"""

    @pytest.fixture
    def message_bus(self):
        """Create a message bus with registry"""
        registry = A2ARegistry()
        return A2AMessageBus(registry)

    @pytest.mark.asyncio
    async def test_register_agent(self, message_bus):
        """Test registering an agent"""
        agent = PuzzleValidatorAgent()
        message_bus.register_agent(agent)
        assert "puzzle-validator-001" in message_bus.agents

    @pytest.mark.asyncio
    async def test_send_message(self, message_bus):
        """Test sending a message through the bus"""
        # Register an agent
        agent = PuzzleValidatorAgent()
        message_bus.register_agent(agent)

        # Start the message bus
        bus_task = asyncio.create_task(message_bus.start())

        try:
            # Send a message
            msg = A2AMessage(
                message_id="test-125",
                sender_id="test-sender",
                receiver_id="puzzle-validator-001",
                message_type="request",
                action="validate_puzzle",
                payload={
                    "puzzle": [[0] * 9 for _ in range(9)],  # Empty puzzle
                    "puzzle_id": "test-puzzle-3",
                },
                timestamp=datetime.now().isoformat(),
            )

            response = await message_bus.send_message(msg)
            assert response is not None
            assert response.message_type == "response"

        finally:
            # Cleanup
            await message_bus.stop()
            bus_task.cancel()
            try:
                await bus_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_agent_not_found(self, message_bus):
        """Test sending message to non-existent agent"""
        # Start the message bus
        bus_task = asyncio.create_task(message_bus.start())

        try:
            # Send a message to non-existent agent
            msg = A2AMessage(
                message_id="test-126",
                sender_id="test-sender",
                receiver_id="non-existent-agent",
                message_type="request",
                action="test",
                payload={},
                timestamp=datetime.now().isoformat(),
            )

            response = await message_bus.send_message(msg)
            assert response is not None
            assert response.message_type == "error"
            assert "not found" in response.payload["error"].lower()

        finally:
            # Cleanup
            await message_bus.stop()
            bus_task.cancel()
            try:
                await bus_task
            except asyncio.CancelledError:
                pass


class TestA2AOrchestrator:
    """Test A2A Orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator"""
        registry = A2ARegistry()
        bus = A2AMessageBus(registry)
        return A2AOrchestrator(bus)

    @pytest.mark.asyncio
    async def test_orchestrator_puzzle_validation(self, orchestrator):
        """Test orchestrator puzzle validation workflow"""
        # Register validator agent
        validator = PuzzleValidatorAgent()
        orchestrator.message_bus.register_agent(validator)

        # Start the message bus
        bus_task = asyncio.create_task(orchestrator.message_bus.start())

        try:
            # Test validating puzzles
            puzzles = [
                {
                    "puzzle_id": "test-1",
                    "grid": [[0] * 9 for _ in range(9)],  # Empty puzzle
                }
            ]

            result = await orchestrator.validate_puzzles(puzzles)
            assert result["total_puzzles"] == 1
            assert result["valid_puzzles"] == 0  # Empty puzzle is invalid
            assert result["invalid_puzzles"] == 1

        finally:
            # Cleanup
            await orchestrator.message_bus.stop()
            bus_task.cancel()
            try:
                await bus_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
