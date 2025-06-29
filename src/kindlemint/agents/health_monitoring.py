"""
Health Monitoring System for KindleMint Multi-Agent Architecture

This module provides comprehensive health monitoring, performance tracking,
and alerting capabilities for the multi-agent publishing automation system.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import psutil

from .message_protocol import AgentMessage, MessageType, Priority


class HealthLevel(Enum):
    """Agent health status levels"""

    HEALTHY = "healthy"  # Agent operating normally
    WARNING = "warning"  # Some issues detected, still functional
    CRITICAL = "critical"  # Serious issues, degraded performance
    UNHEALTHY = "unhealthy"  # Agent not functioning properly
    UNKNOWN = "unknown"  # Health status cannot be determined


@dataclass
class HealthMetrics:
    """Detailed health metrics for an agent"""

    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)

    # Task metrics
    tasks_per_minute: float = 0.0
    average_task_duration: float = 0.0
    success_rate: float = 100.0
    error_rate: float = 0.0

    # Response metrics
    response_time: float = 0.0
    queue_depth: int = 0
    throughput: float = 0.0

    # System metrics
    uptime: float = 0.0
    last_heartbeat: Optional[datetime] = None
    health_score: float = 100.0


@dataclass
class HealthStatus:
    """Complete health status for an agent"""

    agent_id: str = ""
    status: str = "unknown"
    health_level: HealthLevel = HealthLevel.UNKNOWN
    metrics: HealthMetrics = field(default_factory=HealthMetrics)

    # Status details
    active_tasks: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    # Timing information
    uptime: float = 0.0
    last_heartbeat: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    # Health checks
    health_checks: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Performance indicators
    success_rate: float = 100.0
    average_response_time: float = 0.0
    resource_utilization: float = 0.0

    def calculate_health_level(self) -> HealthLevel:
        """Calculate overall health level based on metrics"""

        # Critical conditions
        if (
            self.health_checks.get("responsive", True) == False
            or self.metrics.error_rate > 50
            or self.metrics.cpu_usage > 95
            or self.metrics.memory_usage > 95
        ):
            return HealthLevel.UNHEALTHY

        # Warning conditions
        warning_conditions = [
            self.metrics.error_rate > 20,
            self.metrics.cpu_usage > 80,
            self.metrics.memory_usage > 80,
            self.metrics.response_time > 30.0,
            self.success_rate < 80,
        ]

        if sum(warning_conditions) >= 2:
            return HealthLevel.CRITICAL
        elif any(warning_conditions):
            return HealthLevel.WARNING

        # Check for stale heartbeat
        if self.last_heartbeat:
            heartbeat_age = (datetime.now() - self.last_heartbeat).total_seconds()
            if heartbeat_age > 300:  # 5 minutes
                return HealthLevel.CRITICAL
            elif heartbeat_age > 120:  # 2 minutes
                return HealthLevel.WARNING

        return HealthLevel.HEALTHY

    def update_health_level(self) -> None:
        """Update the health level based on current metrics"""
        self.health_level = self.calculate_health_level()

    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        if message not in self.warnings:
            self.warnings.append(message)
            if len(self.warnings) > 10:  # Keep only recent warnings
                self.warnings.pop(0)

    def add_error(self, message: str) -> None:
        """Add an error message"""
        if message not in self.errors:
            self.errors.append(message)
            if len(self.errors) > 10:  # Keep only recent errors
                self.errors.pop(0)

    def clear_warnings(self) -> None:
        """Clear all warning messages"""
        self.warnings.clear()

    def clear_errors(self) -> None:
        """Clear all error messages"""
        self.errors.clear()


class HealthMonitor:
    """
    Centralized health monitoring system for all agents
    """

    def __init__(
        self,
        check_interval: int = 30,
        alert_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize health monitor

        Args:
            check_interval: Health check interval in seconds
            alert_thresholds: Custom thresholds for alerts
        """
        self.check_interval = check_interval
        self.alert_thresholds = alert_thresholds or self._default_thresholds()

        # Agent tracking
        self.agent_health: Dict[str, HealthStatus] = {}
        self.agent_last_seen: Dict[str, datetime] = {}

        # Monitoring state
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None

        # Alert tracking
        self.alert_history: List[Dict[str, Any]] = []
        self.alert_callbacks: List[callable] = []

        # Performance tracking
        self.system_metrics = HealthMetrics()

        self.logger = logging.getLogger("health_monitor")

    def _default_thresholds(self) -> Dict[str, float]:
        """Default alert thresholds"""
        return {
            "cpu_usage_warning": 70.0,
            "cpu_usage_critical": 85.0,
            "memory_usage_warning": 75.0,
            "memory_usage_critical": 90.0,
            "error_rate_warning": 10.0,
            "error_rate_critical": 25.0,
            "response_time_warning": 10.0,
            "response_time_critical": 30.0,
            "success_rate_warning": 90.0,
            "success_rate_critical": 75.0,
            "heartbeat_warning": 120.0,  # seconds
            "heartbeat_critical": 300.0,  # seconds
        }

    async def start_monitoring(self) -> None:
        """Start the health monitoring system"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Health monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop the health monitoring system"""
        self.monitoring_active = False

        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Health monitoring stopped")

    async def register_agent(self, agent_id: str) -> None:
        """Register an agent for monitoring"""
        self.agent_health[agent_id] = HealthStatus(agent_id=agent_id)
        self.agent_last_seen[agent_id] = datetime.now()
        self.logger.info(f"Registered agent for monitoring: {agent_id}")

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from monitoring"""
        self.agent_health.pop(agent_id, None)
        self.agent_last_seen.pop(agent_id, None)
        self.logger.info(f"Unregistered agent from monitoring: {agent_id}")

    async def update_agent_health(
        self, agent_id: str, health_status: HealthStatus
    ) -> None:
        """Update health status for an agent"""
        if agent_id not in self.agent_health:
            await self.register_agent(agent_id)

        # Update status
        previous_level = self.agent_health[agent_id].health_level
        self.agent_health[agent_id] = health_status
        self.agent_last_seen[agent_id] = datetime.now()

        # Update health level
        health_status.update_health_level()

        # Check for level changes and generate alerts
        if previous_level != health_status.health_level:
            await self._handle_health_level_change(
                agent_id, previous_level, health_status.health_level
            )

        # Check thresholds and generate alerts
        await self._check_alert_thresholds(agent_id, health_status)

    async def get_agent_health(self, agent_id: str) -> Optional[HealthStatus]:
        """Get health status for a specific agent"""
        return self.agent_health.get(agent_id)

    async def get_all_agent_health(self) -> Dict[str, HealthStatus]:
        """Get health status for all agents"""
        return self.agent_health.copy()

    async def get_unhealthy_agents(self) -> List[str]:
        """Get list of unhealthy agents"""
        unhealthy = []
        for agent_id, health in self.agent_health.items():
            if health.health_level in [HealthLevel.CRITICAL, HealthLevel.UNHEALTHY]:
                unhealthy.append(agent_id)
        return unhealthy

    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        total_agents = len(self.agent_health)
        if total_agents == 0:
            return {"status": "no_agents", "agents": 0}

        health_counts = {level.value: 0 for level in HealthLevel}
        for health in self.agent_health.values():
            health_counts[health.health_level.value] += 1

        # Calculate overall system health
        healthy_ratio = health_counts["healthy"] / total_agents
        if healthy_ratio >= 0.9:
            system_status = "healthy"
        elif healthy_ratio >= 0.7:
            system_status = "warning"
        else:
            system_status = "critical"

        return {
            "status": system_status,
            "total_agents": total_agents,
            "health_distribution": health_counts,
            "healthy_ratio": healthy_ratio,
            "alerts_last_hour": len(
                [
                    alert
                    for alert in self.alert_history
                    if (datetime.now() - alert["timestamp"]).total_seconds() < 3600
                ]
            ),
        }

    def add_alert_callback(self, callback: callable) -> None:
        """Add a callback function for health alerts"""
        self.alert_callbacks.append(callback)

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await self._update_system_metrics()
                await self._cleanup_stale_agents()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all agents"""
        for agent_id in list(self.agent_health.keys()):
            health = self.agent_health[agent_id]

            # Check heartbeat freshness
            if health.last_heartbeat:
                heartbeat_age = (datetime.now() - health.last_heartbeat).total_seconds()

                if heartbeat_age > self.alert_thresholds["heartbeat_critical"]:
                    health.add_error(f"No heartbeat for {heartbeat_age:.0f} seconds")
                elif heartbeat_age > self.alert_thresholds["heartbeat_warning"]:
                    health.add_warning(f"Stale heartbeat: {heartbeat_age:.0f} seconds")

            # Update health level
            health.update_health_level()

    async def _update_system_metrics(self) -> None:
        """Update overall system metrics"""
        try:
            # Get system resource usage
            self.system_metrics.cpu_usage = psutil.cpu_percent(interval=1)
            self.system_metrics.memory_usage = psutil.virtual_memory().percent
            self.system_metrics.disk_usage = psutil.disk_usage("/").percent

            # Calculate network I/O
            net_io = psutil.net_io_counters()
            self.system_metrics.network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
            }

        except Exception as e:
            self.logger.warning(f"Failed to update system metrics: {e}")

    async def _cleanup_stale_agents(self) -> None:
        """Remove agents that haven't been seen recently"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        stale_agents = [
            agent_id
            for agent_id, last_seen in self.agent_last_seen.items()
            if last_seen < cutoff_time
        ]

        for agent_id in stale_agents:
            self.logger.info(f"Removing stale agent: {agent_id}")
            await self.unregister_agent(agent_id)

    async def _handle_health_level_change(
        self, agent_id: str, old_level: HealthLevel, new_level: HealthLevel
    ) -> None:
        """Handle health level changes"""
        alert = {
            "timestamp": datetime.now(),
            "type": "health_level_change",
            "agent_id": agent_id,
            "old_level": old_level.value,
            "new_level": new_level.value,
            "severity": self._get_alert_severity(new_level),
        }

        self.alert_history.append(alert)
        self.logger.info(
            f"Agent {agent_id} health changed: {old_level.value} -> {new_level.value}"
        )

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

    async def _check_alert_thresholds(
        self, agent_id: str, health: HealthStatus
    ) -> None:
        """Check if any metrics exceed alert thresholds"""
        alerts = []

        # CPU usage alerts
        if health.metrics.cpu_usage > self.alert_thresholds["cpu_usage_critical"]:
            alerts.append(
                ("cpu_critical", f"CPU usage {health.metrics.cpu_usage:.1f}%")
            )
        elif health.metrics.cpu_usage > self.alert_thresholds["cpu_usage_warning"]:
            alerts.append(("cpu_warning", f"CPU usage {health.metrics.cpu_usage:.1f}%"))

        # Memory usage alerts
        if health.metrics.memory_usage > self.alert_thresholds["memory_usage_critical"]:
            alerts.append(
                ("memory_critical", f"Memory usage {health.metrics.memory_usage:.1f}%")
            )
        elif (
            health.metrics.memory_usage > self.alert_thresholds["memory_usage_warning"]
        ):
            alerts.append(
                ("memory_warning", f"Memory usage {health.metrics.memory_usage:.1f}%")
            )

        # Error rate alerts
        if health.metrics.error_rate > self.alert_thresholds["error_rate_critical"]:
            alerts.append(
                ("error_critical", f"Error rate {health.metrics.error_rate:.1f}%")
            )
        elif health.metrics.error_rate > self.alert_thresholds["error_rate_warning"]:
            alerts.append(
                ("error_warning", f"Error rate {health.metrics.error_rate:.1f}%")
            )

        # Success rate alerts
        if health.success_rate < self.alert_thresholds["success_rate_critical"]:
            alerts.append(
                ("success_critical", f"Success rate {health.success_rate:.1f}%")
            )
        elif health.success_rate < self.alert_thresholds["success_rate_warning"]:
            alerts.append(
                ("success_warning", f"Success rate {health.success_rate:.1f}%")
            )

        # Generate alert records
        for alert_type, message in alerts:
            alert = {
                "timestamp": datetime.now(),
                "type": alert_type,
                "agent_id": agent_id,
                "message": message,
                "severity": "critical" if "critical" in alert_type else "warning",
            }

            self.alert_history.append(alert)

            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {e}")

    def _get_alert_severity(self, health_level: HealthLevel) -> str:
        """Get alert severity based on health level"""
        severity_map = {
            HealthLevel.HEALTHY: "info",
            HealthLevel.WARNING: "warning",
            HealthLevel.CRITICAL: "critical",
            HealthLevel.UNHEALTHY: "critical",
            HealthLevel.UNKNOWN: "warning",
        }
        return severity_map.get(health_level, "warning")
