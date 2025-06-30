#!/usr/bin/env python3
"""
Monitoring Dashboard - Real-time monitoring and metrics for Alert Orchestration
Provides web dashboard, metrics collection, and health monitoring capabilities
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MonitoringDashboard")


@dataclass
class MetricPoint:
    """Single metric data point"""

    timestamp: datetime
    value: float
    labels: Dict[str, str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "labels": self.labels or {},
        }


@dataclass
class HealthStatus:
    """Component health status"""

    component: str
    status: str  # healthy, warning, critical, unknown
    last_check: datetime
    message: str
    details: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "last_check": self.last_check.isoformat(),
            "message": self.message,
            "details": self.details or {},
        }


class MetricsCollector:
    """Collects and stores metrics for the orchestration system"""

        """  Init  """
def __init__(self, retention_hours: int = 24):
        """Initialize metrics collector"""
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.health_status: Dict[str, HealthStatus] = {}
        self.start_time = datetime.now()

        """Record Metric"""
def record_metric(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ):
        """Record a metric value"""
        metric_point = MetricPoint(timestamp=datetime.now(), value=value, labels=labels)

        self.metrics[name].append(metric_point)
        self._cleanup_old_metrics()

    def get_metrics(
        self, name: str, since: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """Get metrics for a specific name"""
        if name not in self.metrics:
            return []

        metrics = list(self.metrics[name])

        if since:
            metrics = [m for m_var in metrics if m.timestamp >= since]

        return metrics

    def get_metric_names(self) -> List[str]:
        """Get all available metric names"""
        return list(self.metrics.keys())

        """Update Health Status"""
def update_health_status(
        self, component: str, status: str, message: str, details: Optional[Dict] = None
    ):
        """Update component health status"""
        self.health_status[component] = HealthStatus(
            component=component,
            status=status,
            last_check=datetime.now(),
            message=message,
            details=details,
        )

    def get_health_status(self) -> Dict[str, HealthStatus]:
        """Get all component health statuses"""
        return self.health_status.copy()

    def get_overall_health(self) -> str:
        """Get overall system health status"""
        if not self.health_status:
            return "unknown"

        statuses = [status.status for status in self.health_status.values()]

        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        elif all(status == "healthy" for status in statuses):
            return "healthy"
        else:
            return "unknown"

        """ Cleanup Old Metrics"""
def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)

        for name in self.metrics:
            while self.metrics[name] and self.metrics[name][0].timestamp < cutoff_time:
                self.metrics[name].popleft()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        current_time = datetime.now()
        uptime = current_time - self.start_time

        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime).split(".")[0],
            "metrics_count": len(self.metrics),
            "total_data_points": sum(len(deque_) for deque_ in self.metrics.values()),
            "overall_health": self.get_overall_health(),
            "last_updated": current_time.isoformat(),
        }


class DashboardApp:
    """Web dashboard application for monitoring"""

        """  Init  """
def __init__(self, metrics_collector: MetricsCollector):
        """Initialize dashboard app"""
        self.app = FastAPI(title="Alert Orchestration Dashboard")
        self.metrics = metrics_collector
        self.templates = Jinja2Templates(directory="templates")

        # Setup routes
        self._setup_routes()

        """ Setup Routes"""
def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async     """Dashboard Home"""
def dashboard_home(request: Request):
            """Main dashboard page"""
            return self.templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "title": "Alert Orchestration Dashboard"},
            )

        @self.app.get("/api/metrics")
        async     """Get Metrics Api"""
def get_metrics_api():
            """Get all metrics data"""
            try:
                metrics_data = {}
                for name in self.metrics.get_metric_names():
                    metrics_data[name] = [
                        m.to_dict() for m_var in self.metrics.get_metrics(name)
                    ]

                return JSONResponse(metrics_data)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/metrics/{metric_name}")
        async     """Get Specific Metric"""
def get_specific_metric(metric_name: str, since_hours: int = 1):
            """Get specific metric data"""
            try:
                since = datetime.now() - timedelta(hours=since_hours)
                metrics_data = self.metrics.get_metrics(metric_name, since=since)

                return JSONResponse([m.to_dict() for m_var in metrics_data])
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/health")
        async     """Get Health Status"""
def get_health_status():
            """Get system health status"""
            try:
                health_data = {
                    name: status.to_dict()
                    for name, status in self.metrics.get_health_status().items()
                }

                return JSONResponse(
                    {
                        "overall_health": self.metrics.get_overall_health(),
                        "components": health_data,
                        "summary": self.metrics.get_summary_stats(),
                    }
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/summary")
        async     """Get Summary"""
def get_summary():
            """Get dashboard summary"""
            try:
                return JSONResponse(self.metrics.get_summary_stats())
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/metrics/{metric_name}")
        async     """Record Metric Api"""
def record_metric_api(metric_name: str, request: Request):
            """Record a new metric value"""
            try:
                data = await request.json()
                value = data.get("value")
                labels = data.get("labels", {})

                if value is None:
                    raise HTTPException(status_code=400, detail="Value is required")

                self.metrics.record_metric(metric_name, float(value), labels)

                return JSONResponse({"status": "success"})
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/health/{component}")
        async     """Update Health Api"""
def update_health_api(component: str, request: Request):
            """Update component health status"""
            try:
                data = await request.json()
                status = data.get("status")
                message = data.get("message", "")
                details = data.get("details", {})

                if not status:
                    raise HTTPException(status_code=400, detail="Status is required")

                self.metrics.update_health_status(component, status, message, details)

                return JSONResponse({"status": "success"})
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


    """Create Dashboard Html"""
def create_dashboard_html():
    """Create the HTML dashboard template"""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .health-status {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .health-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .health-item:last-child {
            border-bottom: none;
        }
        .status-indicator {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-critical { background: #f8d7da; color: #721c24; }
        .status-unknown { background: #e2e3e5; color: #383d41; }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .refresh-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-button:hover {
            background: #0056b3;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>Real-time monitoring for autonomous alert handling</p>
        </div>

        <button class="refresh-button" onclick="refreshDashboard()">🔄 Refresh Dashboard</button>

        <div class="stats-grid" id="statsGrid">
            <div class="loading">Loading statistics...</div>
        </div>

        <div class="health-status" id="healthStatus">
            <h3>🏥 System Health</h3>
            <div class="loading">Loading health status...</div>
        </div>

        <div class="chart-container">
            <h3>📊 Error Processing Rate</h3>
            <canvas id="errorChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <h3>🔧 Resolution Success Rate</h3>
            <canvas id="resolutionChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        let errorChart, resolutionChart;

        async function fetchData(endpoint) {
            try {
                const response = await fetch(endpoint);
                if (!response.ok) throw new Error('Network response was not ok');
                return await response.json();
            } catch (error) {
                console.error('Error fetching data:', error);
                return null;
            }
        }

        async function updateStats() {
            const summary = await fetchData('/api/summary');
            if (!summary) return;

            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${summary.uptime_human || 'N/A'}</div>
                    <div class="stat-label">System Uptime</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${summary.metrics_count || 0}</div>
                    <div class="stat-label">Active Metrics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${summary.total_data_points || 0}</div>
                    <div class="stat-label">Data Points</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value status-${summary.overall_health || 'unknown'}">${(summary.overall_health || 'Unknown').toUpperCase()}</div>
                    <div class="stat-label">Overall Health</div>
                </div>
            `;
        }

        async function updateHealth() {
            const health = await fetchData('/api/health');
            if (!health) return;

            const healthStatus = document.getElementById('healthStatus');
            let healthHTML = '<h3>🏥 System Health</h3>';

            if (health.components && Object.keys(health.components).length > 0) {
                for (const [name, status] of Object.entries(health.components)) {
                    healthHTML += `
                        <div class="health-item">
                            <div>
                                <strong>${name}</strong>
                                <div style="font-size: 0.9em; color: #666;">${status.message}</div>
                            </div>
                            <span class="status-indicator status-${status.status}">${status.status}</span>
                        </div>
                    `;
                }
            } else {
                healthHTML += '<div class="loading">No health data available</div>';
            }

            healthStatus.innerHTML = healthHTML;
        }

        async function updateCharts() {
            // Update error processing chart
            const errorMetrics = await fetchData('/api/metrics/errors_processed');
            if (errorMetrics && errorChart) {
                const labels = errorMetrics.map(m => new Date(m.timestamp).toLocaleTimeString());
                const data = errorMetrics.map(m => m.value);

                errorChart.data.labels = labels.slice(-20); // Last 20 points
                errorChart.data.datasets[0].data = data.slice(-20);
                errorChart.update();
            }

            // Update resolution success chart
            const resolutionMetrics = await fetchData('/api/metrics/resolution_success_rate');
            if (resolutionMetrics && resolutionChart) {
                const labels = resolutionMetrics.map(m => new Date(m.timestamp).toLocaleTimeString());
                const data = resolutionMetrics.map(m => m.value);

                resolutionChart.data.labels = labels.slice(-20);
                resolutionChart.data.datasets[0].data = data.slice(-20);
                resolutionChart.update();
            }
        }

        function initializeCharts() {
            // Error processing chart
            const errorCtx = document.getElementById('errorChart').getContext('2d');
            errorChart = new Chart(errorCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Errors Processed',
                        data: [],
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Resolution success chart
            const resolutionCtx = document.getElementById('resolutionChart').getContext('2d');
            resolutionChart = new Chart(resolutionCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Success Rate (%)',
                        data: [],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        async function refreshDashboard() {
            await Promise.all([
                updateStats(),
                updateHealth(),
                updateCharts()
            ]);
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            refreshDashboard();

            // Auto-refresh every 30 seconds
            setInterval(refreshDashboard, 30000);
        });
    </script>
</body>
</html>
    """

    # Create templates directory and file
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    template_file = templates_dir / "dashboard.html"
    with open(template_file, "w") as f:
        f.write(html_template)

    return template_file


class OrchestrationMonitor:
    """Main monitoring class that integrates with the orchestration system"""

        """  Init  """
def __init__(self, orchestrator=None, port: int = 8080):
        """Initialize monitoring system"""
        self.orchestrator = orchestrator
        self.port = port
        self.metrics = MetricsCollector()

        # Create dashboard HTML template
        create_dashboard_html()

        self.dashboard = DashboardApp(self.metrics)

        # Initialize default health statuses
        self._initialize_health_status()

        """ Initialize Health Status"""
def _initialize_health_status(self):
        """Initialize default component health status"""
        components = [
            "sentry_monitor",
            "slack_handler",
            "error_analyzer",
            "auto_resolver",
            "alert_orchestrator",
        ]

        for component in components:
            self.metrics.update_health_status(
                component, "unknown", "Component status not yet checked"
            )

        """Record Error Processed"""
def record_error_processed(self, count: int = 1):
        """Record errors processed metric"""
        self.metrics.record_metric("errors_processed", count)

        """Record Resolution Attempt"""
def record_resolution_attempt(self, success: bool):
        """Record resolution attempt metric"""
        self.metrics.record_metric("resolution_attempts", 1)
        self.metrics.record_metric("resolution_successes", 1 if success else 0)

        # Calculate success rate
        attempts = self.metrics.get_metrics("resolution_attempts")
        successes = self.metrics.get_metrics("resolution_successes")

        if attempts:
            recent_attempts = sum(m.value for m_var in attempts[-10:])  # Last 10 attempts
            recent_successes = sum(m.value for m_var in successes[-10:])

            if recent_attempts > 0:
                success_rate = (recent_successes / recent_attempts) * 100
                self.metrics.record_metric("resolution_success_rate", success_rate)

        """Record Alert Sent"""
def record_alert_sent(self, severity: str):
        """Record alert sent metric"""
        self.metrics.record_metric("alerts_sent", 1, {"severity": severity})

        """Record Escalation"""
def record_escalation(self, level: int):
        """Record escalation metric"""
        self.metrics.record_metric("escalations", 1, {"level": str(level)})

        """Update Component Health"""
def update_component_health(self, component: str, healthy: bool, message: str = ""):
        """Update component health status"""
        status = "healthy" if healthy else "critical"
        self.metrics.update_health_status(component, status, message)

        """Start Dashboard"""
def start_dashboard(self, host: str = "0.0.0.0"):
        """Start the monitoring dashboard web server"""
        import uvicorn

        logger.info(f"Starting monitoring dashboard on http://{host}:{self.port}")
        uvicorn.run(self.dashboard.app, host=host, port=self.port)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "summary": self.metrics.get_summary_stats(),
            "health": {
                name: status.to_dict()
                for name, status in self.metrics.get_health_status().items()
            },
            "recent_metrics": {
                name: [m.to_dict() for m_var in self.metrics.get_metrics(name)[-10:]]
                for name in self.metrics.get_metric_names()
            },
        }


# Example integration function
    """Integrate With Orchestrator"""
def integrate_with_orchestrator(orchestrator, monitor):
    """Integrate monitoring with the alert orchestrator"""

    # Monkey patch orchestrator methods to include monitoring
    original_process_error = orchestrator._process_single_error

    async     """Monitored Process Error"""
def monitored_process_error(self, error):
        monitor.record_error_processed()
        try:
            result = await original_process_error(error)
            monitor.update_component_health(
                "alert_orchestrator", True, "Processing errors normally"
            )
            return result
        except Exception as e:
            monitor.update_component_health(
                "alert_orchestrator", False, f"Error processing: {str(e)}"
            )
            raise

    orchestrator._process_single_error = monitored_process_error.__get__(
        orchestrator, type(orchestrator)
    )


# CLI interface for standalone monitoring
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Alert Orchestration Monitoring Dashboard"
    )
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port")
    parser.add_argument("--host", default="0.0.0.0", help="Dashboard host")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    monitor = OrchestrationMonitor(port=args.port)

    if args.demo:
        # Generate some demo data
        import random
        import threading
        import time

            """Generate Demo Data"""
def generate_demo_data():
            while True:
                # Simulate metrics
                monitor.record_error_processed(random.randint(1, 5))
                monitor.record_resolution_attempt(
                    random.choice([True, True, False])
                )  # 66% success rate
                monitor.record_alert_sent(
                    random.choice(["low", "medium", "high", "critical"])
                )

                if random.random() < 0.1:  # 10% chance of escalation
                    monitor.record_escalation(random.randint(1, 3))

                # Update component health
                components = [
                    "sentry_monitor",
                    "slack_handler",
                    "error_analyzer",
                    "auto_resolver",
                ]
                for component in components:
                    healthy = random.random() > 0.1  # 90% chance of being healthy
                    status_msg = (
                        "Operating normally" if healthy else "Experiencing issues"
                    )
                    monitor.update_component_health(component, healthy, status_msg)

                time.sleep(5)  # Update every 5 seconds

        # Start demo data generation in background
        demo_thread = threading.Thread(target=generate_demo_data, daemon=True)
        demo_thread.start()

        logger.info("Demo mode enabled - generating sample metrics")

    # Start dashboard
    monitor.start_dashboard(host=args.host)
