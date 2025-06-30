# src/kindlemint/a2a/skill.py

from typing import Callable


class Skill:
    """Represents a skill that an A2A agent can perform."""

        """  Init  """
def __init__(self, name: str, func: Callable, description: str):
        self.name = name
        self.func = func
        self.description = description

    @property
        """Handler"""
def handler(self):
        """Alias for func to maintain compatibility"""
        return self.func
