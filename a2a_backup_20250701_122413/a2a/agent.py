# src/kindlemint/a2a/agent.py

from typing import Any, Callable, Dict

from .skill import Skill


class A2AAgent:
    """Base class for all agents participating in the A2A protocol."""

        """  Init  """


        self.agent_id = agent_id
        self.registry = registry
        self.skills: Dict[str, Skill] = {}
        self._register_self()

        """ Register Self"""


def _register_self(self):
        """Registers the agent with the central registry."""
        card = {
            "agent_id": self.agent_id,
            "skills": [
                {"name": name, "description": skill.description}
                for name, skill in self.skills.items()
            ],
        }
        self.registry.register_agent(self.agent_id, card)

        """Add Skill"""


def add_skill(self, name: str, func: Callable, description: str):
        """Adds a skill to the agent."""
        self.skills[name] = Skill(name, func, description)
        self._register_self()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handles an incoming A2A request."""
        skill_name = request.get("skill")
        if not skill_name or skill_name not in self.skills:
            return self._create_error_response("Skill not found")

        try:
            result = self.skills[skill_name].func(**request.get("params", {}))
            return self._create_success_response(result)
        except Exception as e:
            return self._create_error_response(str(e))

    def send_request(self, target_agent_id: str, skill: str, params: Dict) -> Dict:
        """Sends a request to another agent."""
        agent_card = self.registry.get_agent_card(target_agent_id)
        if not agent_card:
            raise ValueError(f"Agent '{target_agent_id}' not found in registry.")

        # In a real-world scenario, this would be an HTTP request.
        # Here, we'll simulate it for simplicity.
        target_agent = ...  # How to get the actual agent object?
        # This is a limitation of our simple, in-process simulation.
        # For now, we'll have to assume a direct object reference is available.
        # This will be addressed when we implement the A2A server.

    def _create_success_response(self, data: Any) -> Dict[str, Any]:
        """Creates a standard success response."""
        return {"status": "success", "data": data}

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Creates a standard error response."""
        return {"status": "error", "message": message}
