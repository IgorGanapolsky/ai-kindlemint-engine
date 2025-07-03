"""
Orchestrator Monitoring System - Health checks and metrics for orchestration systems
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional


class HealthStatus(Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


@dataclass
class HealthCheck:
    """Individual health check result"""

    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System performance metrics"""

    timestamp: datetime
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_task_duration_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    uptime_seconds: float


class OrchestrationMonitor:
    """Monitors health and performance of orchestration systems"""

    def __init__(self, unified_orchestrator):
        self.orchestrator = unified_orchestrator
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()

        # Health check configuration
        self.health_checks = {
            "unified_orchestrator": self._check_unified_orchestrator_health,
            "claude_code": self._check_claude_code_health,
            "puzzle_generator": self._check_puzzle_generator_health,
            "pdf_layout": self._check_pdf_layout_health,
        }

        # Metrics storage
        self.metrics_history = []
        self.max_history_size = 1000

        # Alert thresholds
        self.alert_thresholds = {
            "max_task_duration_ms": 30000,  # 30 seconds
            "max_failed_task_rate": 0.1,  # 10%
            "max_memory_usage_mb": 1000,  # 1GB
            "max_response_time_ms": 5000,  # 5 seconds
        }

        # Health check intervals
        self.health_check_interval = 60  # seconds
        self.metrics_collection_interval = 30  # seconds

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None

    async def start_monitoring(self):
        """Start the monitoring system"""
        if self.is_monitoring:
            self.logger.warning("Monitoring already started")
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("🔍 Orchestration monitoring started")

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("🛑 Orchestration monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        health_check_next = time.time()
        metrics_next = time.time()

        try:
            while self.is_monitoring:
                current_time = time.time()

                # Run health checks
                if current_time >= health_check_next:
                    await self._run_health_checks()
                    health_check_next = current_time + self.health_check_interval

                # Collect metrics
                if current_time >= metrics_next:
                    await self._collect_metrics()
                    metrics_next = current_time + self.metrics_collection_interval

                # Sleep for a short interval
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")

    async def run_health_check(
        self, check_name: Optional[str] = None
    ) -> Dict[str, HealthCheck]:
        """Run health checks (specific check or all)"""
        if check_name:
            if check_name not in self.health_checks:
                raise ValueError(f"Unknown health check: {check_name}")
            checks_to_run = {check_name: self.health_checks[check_name]}
        else:
            checks_to_run = self.health_checks

        results = {}
        for name, check_func in checks_to_run.items():
            try:
                start_time = time.time()
                result = await check_func()
                duration_ms = (time.time() - start_time) * 1000

                # Create health check result
                results[name] = HealthCheck(
                    name=name,
                    status=result.get("status", HealthStatus.DOWN),
                    message=result.get("message", "No message"),
                    duration_ms=duration_ms,
                    metadata=result.get("metadata", {}),
                )

            except Exception as e:
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    duration_ms=0,
                )
                self.logger.error(f"Health check {name} failed: {e}")

        return results

    async def _run_health_checks(self):
        """Run all health checks"""
        results = await self.run_health_check()

        # Check for alerts
        for name, result in results.items():
            if result.status in [HealthStatus.CRITICAL, HealthStatus.DOWN]:
                await self._send_alert(f"CRITICAL: {name} health check failed", result)
            elif result.status == HealthStatus.WARNING:
                await self._send_alert(f"WARNING: {name} health check warning", result)

    async def _collect_metrics(self):
        """Collect system metrics"""
        try:
            # Get orchestrator status
            status = self.orchestrator.get_system_status()
            unified = status["unified_orchestrator"]

            # Calculate metrics
            unified["completed_tasks"]
            uptime = (datetime.now() - self.start_time).total_seconds()

            # Get system resources (simplified)
            import psutil

            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_usage = psutil.Process().cpu_percent()

            metrics = SystemMetrics(
                timestamp=datetime.now(),
                active_tasks=unified["active_tasks"],
                completed_tasks=unified["completed_tasks"],
                failed_tasks=0,  # Would track from orchestrator
                avg_task_duration_ms=0,  # Would calculate from task history
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                uptime_seconds=uptime,
            )

            # Store metrics
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)

            # Check for metric alerts
            await self._check_metric_alerts(metrics)

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")

    async def _check_unified_orchestrator_health(self) -> Dict[str, Any]:
        """Check unified orchestrator health"""
        try:
            status = self.orchestrator.get_system_status()

            if status and "unified_orchestrator" in status:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Unified orchestrator is operational",
                    "metadata": status["unified_orchestrator"],
                }
            else:
                return {
                    "status": HealthStatus.CRITICAL,
                    "message": "Unable to get orchestrator status",
                }

        except Exception as e:
            return {
                "status": HealthStatus.DOWN,
                "message": f"Orchestrator health check failed: {str(e)}",
            }

    async def _check_claude_code_health(self) -> Dict[str, Any]:
        """Check Claude Code orchestrator health"""
        try:
            # Test Claude Code functionality
            if hasattr(self.orchestrator, "claude_code"):
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Claude Code orchestrator is operational",
                    "metadata": {"available": True},
                }
            else:
                return {
                    "status": HealthStatus.DOWN,
                    "message": "Claude Code orchestrator not available",
                }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Claude Code health check failed: {str(e)}",
            }


    async def _check_puzzle_generator_health(self) -> Dict[str, Any]:
        """Check puzzle generator agent health"""
        try:
            if hasattr(self.orchestrator, "puzzle_generator"):
                agent = self.orchestrator.puzzle_generator

                # Test puzzle generation with a simple request
                test_request = {"difficulty": "easy", "count": 1, "format": "json"}

                # Validate request (doesn't generate, just validates)
                validation_result = await agent.skills[
                    "validate_puzzle_request"
                ].handler(test_request)

                if validation_result.get("valid"):
                    return {
                        "status": HealthStatus.HEALTHY,
                        "message": "Puzzle generator agent is operational",
                        "metadata": {"skills": list(agent.skills.keys())},
                    }
                else:
                    return {
                        "status": HealthStatus.WARNING,
                        "message": f"Puzzle generator validation failed: {validation_result.get('error')}",
                    }
            else:
                return {
                    "status": HealthStatus.DOWN,
                    "message": "Puzzle generator agent not found",
                }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Puzzle generator health check failed: {str(e)}",
            }

    async def _check_pdf_layout_health(self) -> Dict[str, Any]:
        """Check PDF layout agent health"""
        try:
            if hasattr(self.orchestrator, "pdf_layout"):
                agent = self.orchestrator.pdf_layout

                # Test PDF layout validation
                test_request = {
                    "puzzles": [{"puzzle": [[0] * 9 for __var in range(9)]}],
                    "book_title": "Test Book",
                }

                validation_result = await agent.skills["validate_pdf_layout"].handler(
                    test_request
                )

                if validation_result.get("valid"):
                    return {
                        "status": HealthStatus.HEALTHY,
                        "message": "PDF layout agent is operational",
                        "metadata": {"skills": list(agent.skills.keys())},
                    }
                else:
                    return {
                        "status": HealthStatus.WARNING,
                        "message": f"PDF layout validation failed: {validation_result.get('error')}",
                    }
            else:
                return {
                    "status": HealthStatus.DOWN,
                    "message": "PDF layout agent not found",
                }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"PDF layout health check failed: {str(e)}",
            }

    async def _check_metric_alerts(self, metrics: SystemMetrics):
        """Check metrics against alert thresholds"""
        alerts = []

        # Memory usage alert
        if metrics.memory_usage_mb > self.alert_thresholds["max_memory_usage_mb"]:
            alerts.append(f"High memory usage: {metrics.memory_usage_mb:.1f}MB")

        # Task duration alert (would need task history to implement)
        # CPU usage alert (if we had historical data)

        # Send alerts
        for alert in alerts:
            await self._send_alert("METRIC ALERT", alert)

    async def _send_alert(self, title: str, details: Any):
        """Send alert (placeholder for real alerting system)"""
        alert_message = f"[{datetime.now().isoformat()}] {title}: {details}"
        self.logger.warning(f"🚨 ALERT: {alert_message}")

        # In a real system, this would send to Slack, email, etc.
        # For now, just log the alert

    def get_health_summary(self) -> Dict[str, Any]:
        """Get current health summary"""
        # Run health checks synchronously for summary
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.run_health_check())
        finally:
            loop.close()

        # Calculate overall health
        statuses = [result.status for result in results.values()]

        if any(s == HealthStatus.DOWN for s_var in statuses):
            overall_status = HealthStatus.DOWN
        elif any(s == HealthStatus.CRITICAL for s_var in statuses):
            overall_status = HealthStatus.CRITICAL
        elif any(s == HealthStatus.WARNING for s_var in statuses):
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "duration_ms": result.duration_ms,
                }
                for name, result in results.items()
            },
        }

    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m_var in self.metrics_history if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return {"error": "No metrics available for the specified time period"}

        # Calculate averages
        avg_active_tasks = sum(m.active_tasks for m_var in recent_metrics) / len(
            recent_metrics
        )
        avg_memory = sum(m.memory_usage_mb for m_var in recent_metrics) / len(
            recent_metrics
        )
        avg_cpu = sum(m.cpu_usage_percent for m_var in recent_metrics) / len(recent_metrics)

        return {
            "time_period_hours": hours,
            "metrics_count": len(recent_metrics),
            "averages": {
                "active_tasks": round(avg_active_tasks, 1),
                "memory_usage_mb": round(avg_memory, 1),
                "cpu_usage_percent": round(avg_cpu, 1),
            },
            "current": {
                "active_tasks": recent_metrics[-1].active_tasks,
                "completed_tasks": recent_metrics[-1].completed_tasks,
                "memory_usage_mb": round(recent_metrics[-1].memory_usage_mb, 1),
                "uptime_seconds": recent_metrics[-1].uptime_seconds,
            },
        }

    def export_metrics(self, filepath: str):
        """Export metrics to file"""
        try:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics_count": len(self.metrics_history),
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "active_tasks": m.active_tasks,
                        "completed_tasks": m.completed_tasks,
                        "failed_tasks": m.failed_tasks,
                        "memory_usage_mb": m.memory_usage_mb,
                        "cpu_usage_percent": m.cpu_usage_percent,
                        "uptime_seconds": m.uptime_seconds,
                    }
                    for m_var in self.metrics_history
                ],
            }

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"📊 Metrics exported to: {filepath}")

        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            raise


# Factory function
def create_monitor(unified_orchestrator):
    """Create and return a configured OrchestrationMonitor"""
    return OrchestrationMonitor(unified_orchestrator)
