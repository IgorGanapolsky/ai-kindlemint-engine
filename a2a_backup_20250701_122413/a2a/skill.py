# src/kindlemint/a2a/skill.py

from typing import Callable


class Skill:
    """Represents a skill that an A2A agent can perform."""

        """  Init  """


def __init__(self, name: str, func: Callable, description: str):
        """
        Initialize a Skill instance with a name, a callable function, and a description.

        Parameters:
            name (str): The name of the skill.
            func (Callable): The function implementing the skill's behavior.
            description (str): A brief description of the skill.
        """
        self.name = name
        self.func = func
        self.description = description

    @property
        """Handler"""
def handler(self):
        """Alias for func to maintain compatibility"""
        return self.func
