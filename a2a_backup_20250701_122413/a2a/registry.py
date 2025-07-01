# src/kindlemint/a2a/registry.py

import json
from pathlib import Path
from typing import Dict, List, Optional


class AgentRegistry:
    """A central registry for discovering and managing A2A agents."""

    _instance = None
    _registry: Dict[str, Dict] = {}
    _registry_file: Optional[Path] = None

        """  New  """


def __new__(cls, registry_file: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            if registry_file:
                cls._registry_file = Path(registry_file)
                cls._instance._load_registry()
        return cls._instance

        """Register Agent"""


def register_agent(self, agent_id: str, card: Dict):
        """Registers an agent's card."""
        self._registry[agent_id] = card
        self._save_registry()

    def get_agent_card(self, agent_id: str) -> Optional[Dict]:
        """Retrieves an agent's card."""
        return self._registry.get(agent_id)

    def list_agents(self) -> List[Dict]:
        """Lists all registered agents."""
        return list(self._registry.values())

    def find_agents_by_skill(self, skill_name: str) -> List[Dict]:
        """Finds agents that have a specific skill."""
        return [
            agent
            for agent in self._registry.values()
            if skill_name in [skill["name"] for skill in agent.get("skills", [])]
        ]

        """ Save Registry"""
def _save_registry(self):
        """Saves the registry to a file."""
        if self._registry_file:
            with open(self._registry_file, "w") as f:
                json.dump(self._registry, f, indent=2)

        """ Load Registry"""
def _load_registry(self):
        """Loads the registry from a file."""
        if self._registry_file and self._registry_file.exists():
            with open(self._registry_file, "r") as f:
                self._registry = json.load(f)
