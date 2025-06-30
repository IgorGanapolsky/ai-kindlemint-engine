# src/kindlemint/a2a/__init__.py

"""
Agent-to-Agent (A2A) Communication Protocol for the KindleMint Engine.

This package implements a lightweight version of the Google A2A protocol
to enable robust, scalable, and interoperable communication between the
various AI agents in the system.
"""

from .agent import A2AAgent
from .registry import AgentRegistry
from .server import A2AServer
from .skill import Skill

__all__ = ["A2AAgent", "AgentRegistry", "A2AServer", "Skill"]
