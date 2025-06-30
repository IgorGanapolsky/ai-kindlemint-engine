"""
Agent Registry and Discovery System for KindleMint Multi-Agent Architecture

This module provides centralized agent registration, discovery, and
communication routing for the multi-agent book publishing system.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .base_agent import AgentCapability, AgentStatus
from .health_monitoring import HealthMonitor, HealthStatus
from .message_protocol import AgentMessage


class AgentRegistry:
    """
    Centralized registry for agent discovery and communication routing
    """

    def __init__(self, health_monitor: Optional[HealthMonitor] = None):
        """
        Initialize agent registry

        Args:
            health_monitor: Health monitoring system instance
        """
        self.health_monitor = health_monitor or HealthMonitor()

        # Agent tracking
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, Set[AgentCapability]] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}

        # Capability-based routing
        self.capability_map: Dict[AgentCapability, Set[str]] = defaultdict(set)

        # Message routing
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.broadcast_subscribers: Set[str] = set()

        # Load balancing
        self.agent_load: Dict[str, int] = defaultdict(int)  # Current task count
        self.agent_performance: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Registry state
        self.registry_active = False
        self.cleanup_task: Optional[asyncio.Task] = None

        self.logger = logging.getLogger("agent_registry")

    async def start(self) -> None:
        """Start the agent registry system"""
        if self.registry_active:
            return

        self.registry_active = True

        # Start health monitoring
        await self.health_monitor.start_monitoring()

        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        self.logger.info("Agent registry started")

    async def stop(self) -> None:
        """Stop the agent registry system"""
        self.registry_active = False

        # Stop health monitoring
        await self.health_monitor.stop_monitoring()

        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Agent registry stopped")

    async def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[AgentCapability],
        metadata: Optional[Dict[str, Any]] = None,
        max_concurrent_tasks: int = 1,
    ) -> bool:
        """
        Register an agent with the registry

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent
            capabilities: List of agent capabilities
            metadata: Additional agent metadata
            max_concurrent_tasks: Maximum concurrent task capacity

        Returns:
            True if registration successful
        """
        try:
            # Check for duplicate registration
            if agent_id in self.agents:
                self.logger.warning(f"Agent {agent_id} already registered")
                return False

            # Register agent
            self.agents[agent_id] = {
                "agent_type": agent_type,
                "registered_at": datetime.now(),
                "last_heartbeat": datetime.now(),
                "max_concurrent_tasks": max_concurrent_tasks,
            }

            # Store capabilities
            self.agent_capabilities[agent_id] = set(capabilities)
            for capability in capabilities:
                self.capability_map[capability].add(agent_id)

            # Initialize status and metadata
            self.agent_status[agent_id] = AgentStatus.IDLE
            self.agent_metadata[agent_id] = metadata or {}

            # Create message queue
            self.message_queues[agent_id] = asyncio.Queue()

            # Initialize performance tracking
            self.agent_load[agent_id] = 0
            self.agent_performance[agent_id] = {
                "success_rate": 100.0,
                "avg_response_time": 0.0,
                "tasks_completed": 0,
                "tasks_failed": 0,
            }

            # Register with health monitor
            await self.health_monitor.register_agent(agent_id)

            self.logger.info(
                f"Registered agent {agent_id} (type: {agent_type}, "
                f"capabilities: {[cap.value for cap in capabilities]})"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry

        Args:
            agent_id: Agent identifier to unregister

        Returns:
            True if unregistration successful
        """
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found for unregistration")
                return False

            # Remove from capability mappings
            capabilities = self.agent_capabilities.get(agent_id, set())
            for capability in capabilities:
                self.capability_map[capability].discard(agent_id)
                if not self.capability_map[capability]:
                    del self.capability_map[capability]

            # Clean up all tracking data
            self.agents.pop(agent_id, None)
            self.agent_capabilities.pop(agent_id, None)
            self.agent_status.pop(agent_id, None)
            self.agent_metadata.pop(agent_id, None)
            self.message_queues.pop(agent_id, None)
            self.agent_load.pop(agent_id, None)
            self.agent_performance.pop(agent_id, None)

            # Remove from broadcast subscribers
            self.broadcast_subscribers.discard(agent_id)

            # Unregister from health monitor
            await self.health_monitor.unregister_agent(agent_id)

            self.logger.info(f"Unregistered agent {agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False

    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status"""
        if agent_id not in self.agents:
            return False

        old_status = self.agent_status.get(agent_id)
        self.agent_status[agent_id] = status

        if old_status != status:
            self.logger.debug(f"Agent {agent_id} status: {old_status} -> {status}")

        return True

    async def update_agent_health(
        self, agent_id: str, health_status: HealthStatus
    ) -> bool:
        """Update agent health status"""
        if agent_id not in self.agents:
            return False

        # Update last heartbeat
        self.agents[agent_id]["last_heartbeat"] = datetime.now()

        # Forward to health monitor
        await self.health_monitor.update_agent_health(agent_id, health_status)

        return True

    async def update_agent_load(self, agent_id: str, load_delta: int) -> bool:
        """Update agent task load"""
        if agent_id not in self.agents:
            return False

        self.agent_load[agent_id] = max(0, self.agent_load[agent_id] + load_delta)
        return True

    async def update_agent_performance(
        self, agent_id: str, task_success: bool, response_time: float
    ) -> bool:
        """Update agent performance metrics"""
        if agent_id not in self.agents:
            return False

        perf = self.agent_performance[agent_id]

        # Update task counters
        if task_success:
            perf["tasks_completed"] += 1
        else:
            perf["tasks_failed"] += 1

        # Calculate success rate
        total_tasks = perf["tasks_completed"] + perf["tasks_failed"]
        if total_tasks > 0:
            perf["success_rate"] = (perf["tasks_completed"] / total_tasks) * 100

        # Update average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        if perf["avg_response_time"] == 0:
            perf["avg_response_time"] = response_time
        else:
            perf["avg_response_time"] = (
                alpha * response_time + (1 - alpha) * perf["avg_response_time"]
            )

        return True

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get complete information about an agent"""
        if agent_id not in self.agents:
            return None

        return {
            "agent_id": agent_id,
            "agent_type": self.agents[agent_id]["agent_type"],
            "capabilities": [cap.value for cap in self.agent_capabilities[agent_id]],
            "status": self.agent_status[agent_id].value,
            "load": self.agent_load[agent_id],
            "max_concurrent_tasks": self.agents[agent_id]["max_concurrent_tasks"],
            "performance": self.agent_performance[agent_id].copy(),
            "metadata": self.agent_metadata[agent_id].copy(),
            "registered_at": self.agents[agent_id]["registered_at"],
            "last_heartbeat": self.agents[agent_id]["last_heartbeat"],
        }

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get information about all registered agents"""
        return [self.get_agent_info(agent_id) for agent_id in self.agents.keys()]

    def find_agents_by_capability(
        self,
        capability: AgentCapability,
        status_filter: Optional[List[AgentStatus]] = None,
    ) -> List[str]:
        """
        Find agents with a specific capability

        Args:
            capability: Required capability
            status_filter: Optional list of acceptable agent statuses

        Returns:
            List of agent IDs with the capability
        """
        candidates = self.capability_map.get(capability, set()).copy()

        if status_filter:
            candidates = {
                agent_id
                for agent_id in candidates
                if self.agent_status.get(agent_id) in status_filter
            }

        return list(candidates)

    def find_best_agent_for_task(
        self,
        required_capabilities: List[AgentCapability],
        preferred_agents: Optional[List[str]] = None,
        excluded_agents: Optional[List[str]] = None,
        load_balancing: bool = True,
    ) -> Optional[str]:
        """
        Find the best agent for a task based on capabilities and load

        Args:
            required_capabilities: List of required capabilities
            preferred_agents: Optional list of preferred agent IDs
            excluded_agents: Optional list of excluded agent IDs
            load_balancing: Whether to consider load balancing

        Returns:
            Best agent ID or None if no suitable agent found
        """
        # Find agents with all required capabilities
        candidates = None
        for capability in required_capabilities:
            capable_agents = set(
                self.find_agents_by_capability(
                    capability, [AgentStatus.IDLE, AgentStatus.BUSY]
                )
            )

            if candidates is None:
                candidates = capable_agents
            else:
                candidates &= capable_agents

        if not candidates:
            return None

        # Apply agent filters
        if preferred_agents:
            preferred_set = set(preferred_agents) & candidates
            if preferred_set:
                candidates = preferred_set

        if excluded_agents:
            candidates -= set(excluded_agents)

        if not candidates:
            return None

        # Filter agents that can accept more tasks
        available_agents = []
        for agent_id in candidates:
            max_tasks = self.agents[agent_id]["max_concurrent_tasks"]
            current_load = self.agent_load[agent_id]

            if current_load < max_tasks:
                available_agents.append(agent_id)

        if not available_agents:
            return None

        # Select best agent based on criteria
        if not load_balancing:
            return available_agents[0]

        # Load balancing: prefer agents with lower load and better performance
        def agent_score(agent_id: str) -> float:
            load_ratio = (
                self.agent_load[agent_id]
                / self.agents[agent_id]["max_concurrent_tasks"]
            )
            success_rate = self.agent_performance[agent_id]["success_rate"] / 100.0
            response_time = self.agent_performance[agent_id]["avg_response_time"]

            # Lower is better for load and response time, higher is better for success
            # rate
            score = (
                (1 - load_ratio) * 0.4
                + success_rate * 0.4
                + (1 / (1 + response_time)) * 0.2
            )
            return score

        best_agent = max(available_agents, key=agent_score)
        return best_agent

    async def route_message(self, message: AgentMessage) -> bool:
        """
        Route a message to the appropriate agent(s)

        Args:
            message: Message to route

        Returns:
            True if message was successfully routed
        """
        try:
            if message.recipient_id == "broadcast":
                return await self._handle_broadcast_message(message)
            else:
                return await self._handle_direct_message(message)
        except Exception as e:
            self.logger.error(f"Message routing failed: {e}")
            return False

    async def _handle_direct_message(self, message: AgentMessage) -> bool:
        """Handle direct message to specific agent"""
        recipient_id = message.recipient_id

        if recipient_id not in self.message_queues:
            self.logger.warning(f"Agent {recipient_id} not found for message routing")
            return False

        try:
            await self.message_queues[recipient_id].put(message)
            self.logger.debug(f"Routed message {message.message_id} to {recipient_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to route message to {recipient_id}: {e}")
            return False

    async def _handle_broadcast_message(self, message: AgentMessage) -> bool:
        """Handle broadcast message to multiple agents"""
        target_agents = set()

        # Route based on target capabilities if specified
        if message.target_capabilities:
            for capability_name in message.target_capabilities:
                try:
                    capability = AgentCapability(capability_name)
                    target_agents.update(self.capability_map.get(capability, set()))
                except ValueError:
                    self.logger.warning(f"Unknown capability: {capability_name}")
        else:
            # Broadcast to all agents
            target_agents = set(self.agents.keys())

        # Route to all target agents
        success_count = 0
        for agent_id in target_agents:
            if agent_id in self.message_queues:
                try:
                    await self.message_queues[agent_id].put(message)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to broadcast to {agent_id}: {e}")

        self.logger.debug(
            f"Broadcast message {message.message_id} to {
                success_count}/{len(target_agents)} agents"
        )

        return success_count > 0

    async def get_agent_message(
        self, agent_id: str, timeout: Optional[float] = None
    ) -> Optional[AgentMessage]:
        """
        Get next message for an agent

        Args:
            agent_id: Agent identifier
            timeout: Optional timeout in seconds

        Returns:
            Next message or None if timeout/no messages
        """
        if agent_id not in self.message_queues:
            return None

        try:
            if timeout is None:
                return await self.message_queues[agent_id].get()
            else:
                return await asyncio.wait_for(
                    self.message_queues[agent_id].get(), timeout=timeout
                )
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.error(f"Error getting message for {agent_id}: {e}")
            return None

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status_counts = defaultdict(int)
        for status in self.agent_status.values():
            status_counts[status.value] += 1

        total_load = sum(self.agent_load.values())
        total_capacity = sum(
            agent["max_concurrent_tasks"] for agent in self.agents.values()
        )

        return {
            "total_agents": len(self.agents),
            "agent_status_distribution": dict(status_counts),
            "total_load": total_load,
            "total_capacity": total_capacity,
            "utilization": (
                (total_load / total_capacity * 100) if total_capacity > 0 else 0
            ),
            "capabilities": {
                cap.value: len(agents) for cap, agents in self.capability_map.items()
            },
        }

    async def _cleanup_loop(self) -> None:
        """Background cleanup of stale agents and old messages"""
        while self.registry_active:
            try:
                await self._cleanup_stale_agents()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")

    async def _cleanup_stale_agents(self) -> None:
        """Remove agents that haven't sent heartbeats recently"""
        cutoff_time = datetime.now() - timedelta(minutes=10)
        stale_agents = []

        for agent_id, agent_info in self.agents.items():
            if agent_info["last_heartbeat"] < cutoff_time:
                stale_agents.append(agent_id)

        for agent_id in stale_agents:
            self.logger.warning(f"Removing stale agent: {agent_id}")
            await self.unregister_agent(agent_id)
