# File: src/kindlemint/agents/agent_types.py
from enum import Enum

class AgentStatus(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentCapability(Enum):
    DESIGN = "design"
    CREATE = "create"
    WRITE = "write"
    REFINE = "refine"
    ALIGN = "align"
