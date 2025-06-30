# src/kindlemint/a2a/server.py

from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from .agent import A2AAgent
from .registry import AgentRegistry


class A2AServer:
    """A FastAPI-based server to expose A2A agents over HTTP."""

    def __init__(self, registry: AgentRegistry):
        self.app = FastAPI()
        self.registry = registry
        self.agents: Dict[str, A2AAgent] = {}

        @self.app.get("/")
        def list_agents():
            return {"agents": self.registry.list_agents()}

        @self.app.post("/{agent_id}")
        def handle_request(agent_id: str, request: Dict[str, Any]):
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")

            agent = self.agents[agent_id]
            return agent.handle_request(request)

    def register_agent(self, agent: A2AAgent):
        """Registers an agent with the server."""
        self.agents[agent.agent_id] = agent
        self.registry.register_agent(
            agent.agent_id,
            {
                "agent_id": agent.agent_id,
                "skills": [
                    {"name": name, "description": func.__doc__}
                    for name, func in agent.skills.items()
                ],
            },
        )


def create_a2a_server(registry: AgentRegistry) -> A2AServer:
    """Factory function to create an A2A server."""
    return A2AServer(registry)
