#!/usr/bin/env python3
"""Tests for agent_types module - quick coverage boost"""

import pytest

from kindlemint.agents.agent_types import AgentCapability


class TestAgentTypes:
    """Test agent type definitions"""

    def test_agent_capability_enum(self):
        """Test AgentCapability enum values"""
        assert AgentCapability.CONTENT_GENERATION.value == "content_generation"
        assert AgentCapability.PUZZLE_CREATION.value == "puzzle_creation"
        assert AgentCapability.PDF_LAYOUT.value == "pdf_layout"
        assert AgentCapability.COVER_DESIGN.value == "cover_design"

    def test_all_capabilities(self):
        """Test all capability values are unique"""
        values = [cap.value for cap in AgentCapability]
        assert len(values) == len(set(values))  # All unique

    def test_enum_members(self):
        """Test enum membership"""
        assert len(AgentCapability) >= 10  # Should have many capabilities

    def test_enum_iteration(self):
        """Test we can iterate over enums"""
        capabilities = list(AgentCapability)
        assert len(capabilities) > 0
        assert AgentCapability.TASK_COORDINATION in capabilities
