#!/usr/bin/env python3
"""Tests for A2A Protocol implementation"""

import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from scripts.a2a_protocol.base_agent import (
    A2AAgent,
    A2AMessage,
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
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
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
        agent = A2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        assert agent.agent_id == "test-agent"
        assert agent.name == "Test Agent"
        assert agent.description == "Test agent for unit tests"

    def test_agent_card_generation(self):
        """Test agent card generation"""
        agent = A2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        card = agent.get_agent_card()
        assert card.agent_id == "test-agent"
        assert card.name == "Test Agent"
        assert card.description == "Test agent for unit tests"
        assert card.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_handle_message_not_implemented(self):
        """Test that base agent raises NotImplementedError"""
        agent = A2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="Test agent for unit tests",
        )
        msg = A2AMessage(
            message_id="test-123",
            sender_id="other-agent",
            receiver_id="test-agent",
            message_type="request",
            action="test",
            payload={},
            timestamp=datetime.utcnow().isoformat(),
        )
        with pytest.raises(NotImplementedError):
            await agent.handle_message(msg)


class TestPuzzleValidatorAgent:
    """Test Puzzle Validator Agent"""

    @pytest.fixture
    def validator_agent(self):
        """Create a puzzle validator agent"""
        return PuzzleValidatorAgent()

    def test_validator_initialization(self, validator_agent):
        """Test validator agent initialization"""
        assert validator_agent.agent_id == "puzzle-validator"
        assert validator_agent.name == "Puzzle Validator Agent"
        assert "validation" in validator_agent.description.lower()

    def test_validator_capabilities(self, validator_agent):
        """Test validator agent capabilities"""
        card = validator_agent.get_agent_card()
        capability_names = [cap.name for cap in card.capabilities]
        assert "validate_puzzle" in capability_names
        assert "validate_batch" in capability_names
        assert "validate_collection" in capability_names

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
            receiver_id="puzzle-validator",
            message_type="request",
            action="validate_puzzle",
            payload={"puzzle": valid_puzzle, "puzzle_id": "test-puzzle-1"},
            timestamp=datetime.utcnow().isoformat(),
        )

        response = await validator_agent.handle_message(msg)
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
            receiver_id="puzzle-validator",
            message_type="request",
            action="validate_puzzle",
            payload={"puzzle": invalid_puzzle, "puzzle_id": "test-puzzle-2"},
            timestamp=datetime.utcnow().isoformat(),
        )

        response = await validator_agent.handle_message(msg)
        assert response is not None
        assert response.message_type == "response"
        assert response.payload["status"] == "success"
        assert response.payload["valid"] is False
        assert "errors" in response.payload


class TestA2AMessageBus:
    """Test A2A Message Bus"""

    @pytest.fixture
    def message_bus(self):
        """Create a message bus"""
        return A2AMessageBus()

    @pytest.mark.asyncio
    async def test_register_agent(self, message_bus):
        """Test registering an agent"""
        agent = PuzzleValidatorAgent()
        message_bus.register_agent(agent)
        assert "puzzle-validator" in message_bus.agents

    @pytest.mark.asyncio
    async def test_send_message(self, message_bus):
        """Test sending a message through the bus"""
        # Register an agent
        agent = PuzzleValidatorAgent()
        message_bus.register_agent(agent)

        # Start the message bus
        bus_task = asyncio.create_task(message_bus.start())

        # Send a message
        msg = A2AMessage(
            message_id="test-125",
            sender_id="test-sender",
            receiver_id="puzzle-validator",
            message_type="request",
            action="validate_puzzle",
            payload={
                "puzzle": [[0] * 9 for _ in range(9)],  # Empty puzzle
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
    async def test_agent_not_found(self, message_bus):
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
    """Test A2A Orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator"""
        bus = A2AMessageBus()
        return A2AOrchestrator(bus)

    @pytest.mark.asyncio
    async def test_orchestrator_puzzle_validation(self, orchestrator):
        """Test orchestrator puzzle validation workflow"""
        # Register validator agent
        validator = PuzzleValidatorAgent()
        orchestrator.message_bus.register_agent(validator)

        # Start the message bus
        bus_task = asyncio.create_task(orchestrator.message_bus.start())

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

        # Cleanup
        await orchestrator.message_bus.stop()
        bus_task.cancel()
        try:
            await bus_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
