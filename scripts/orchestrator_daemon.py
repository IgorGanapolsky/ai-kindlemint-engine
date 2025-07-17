#!/usr/bin/env python3
"""
Always-On Orchestration Daemon with Health Monitoring and Auto-Recovery

This daemon ensures the orchestration system runs 24/7 with:
- Automatic restart on failures
- Health checks every 60 seconds
- PR processing automation
- Slack/Email notifications on critical events
- Performance monitoring
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from src.kindlemint.orchestration_runner import OrchestrationSystem

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class OrchestrationDaemon:
    """Robust daemon for always-on orchestration"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.orchestration = None
        self.restart_count = 0
        self.last_health_check = datetime.now()
        self.running = True
        self.pr_processor_task = None

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("orchestration_daemon")
        logger.setLevel(logging.INFO)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # File handler with rotation
        from logging.handlers import RotatingFileHandler

        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            log_dir / "orchestration_daemon.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(file_handler)

        return logger

    async def start(self):
        """Start the daemon with all services"""
        self.logger.info("Starting KindleMint Always-On Orchestration Daemon")

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Start main orchestration loop
        await self._run_with_recovery()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(
            f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def _run_with_recovery(self):
        """Run orchestration with automatic recovery"""
        while self.running:
            try:
                # Start orchestration system
                self.logger.info(
                    f"Starting orchestration system (attempt #{self.restart_count + 1})"
                )
                self.orchestration = OrchestrationSystem()

                # Initialize the system
                await self.orchestration.initialize()

                # Start PR processor in background
                self.pr_processor_task = asyncio.create_task(
                    self._process_pr_backlog())

                # Start health monitoring
                asyncio.create_task(self._monitor_health())

                # Run the orchestration
                await self.orchestration.run()

            except Exception as e:
                self.logger.error(f"Orchestration crashed: {e}", exc_info=True)
                self.restart_count += 1

                # Send alert if too many restarts
                if self.restart_count > 5:
                    await self._send_critical_alert(
                        f"Orchestration has restarted {self.restart_count} times"
                    )

                # Wait before restart with exponential backoff
                wait_time = min(
                    60 * (2 ** min(self.restart_count - 1, 5)), 300)
                self.logger.info(
                    f"Waiting {wait_time} seconds before restart...")
                await asyncio.sleep(wait_time)

            finally:
                # Cleanup
                if self.pr_processor_task:
                    self.pr_processor_task.cancel()

    async def _monitor_health(self):
        """Monitor system health and take corrective actions"""
        while self.running:
            try:
                # Check orchestration health
                if self.orchestration:
                    agent_count = len(self.orchestration.agents)
                    active_agents = sum(
                        1
                        for agent in self.orchestration.agents
                        if agent.status.value == "running"
                    )

                    if active_agents < agent_count:
                        self.logger.warning(
                            f"Only {active_agents}/{agent_count} agents are running"
                        )

                        # Try to restart dead agents
                        for agent in self.orchestration.agents:
                            if agent.status.value != "running":
                                self.logger.info(
                                    f"Restarting agent: {agent.agent_id}")
                                await agent.start()

                    # Log health status
                    self.logger.info(
                        f"Health Check: {active_agents}/{agent_count} agents active, "
                        f"Uptime: {datetime.now() - self.last_health_check}"
                    )

                # Check system resources
                await self._check_system_resources()

                # Update last health check
                self.last_health_check = datetime.now()

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)

    async def _process_pr_backlog(self):
        """Process PR backlog automatically"""
        while self.running:
            try:
                self.logger.info("Checking for PR backlog...")

                # Get open PRs
                result = subprocess.run(
                    ["gh", "pr", "list", "--json", "number,title,labels,state"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    prs = json.loads(result.stdout)
                    open_prs = [pr for pr in prs if pr["state"] == "OPEN"]

                    self.logger.info(f"Found {len(open_prs)} open PRs")

                    # Process PRs that are ready
                    for pr in open_prs:
                        labels = [label["name"]
                                  for label in pr.get("labels", [])]

                        if (
                            "sentry-ai-completed" in labels
                            and "sentry-ai-reviewed" in labels
                        ):
                            self.logger.info(
                                f"Processing PR #{pr['number']}: {pr['title']}"
                            )

                            # Trigger PR processing
                            # This would integrate with your PR orchestrator
                            await self._trigger_pr_processing(pr["number"])

                            # Wait between PRs
                            await asyncio.sleep(30)

                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"PR processing error: {e}")
                await asyncio.sleep(300)

    async def _trigger_pr_processing(self, pr_number: int):
        """Trigger processing for a specific PR"""
        try:
            # Run PR validation
            subprocess.run(
                [
                    "gh",
                    "pr",
                    "comment",
                    str(pr_number),
                    "--body",
                    "🤖 Orchestrator processing PR...",
                ],
                check=True,
            )

            # Here you would integrate with your PR orchestrator
            # For now, just log it
            self.logger.info(f"Triggered processing for PR #{pr_number}")

        except Exception as e:
            self.logger.error(f"Failed to process PR #{pr_number}: {e}")

    async def _check_system_resources(self):
        """Check system resources and alert if issues"""
        try:
            # Check disk space
            import shutil

            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100

            if free_percent < 10:
                await self._send_critical_alert(
                    f"Low disk space: {free_percent:.1f}% free"
                )

            # Check memory (macOS specific)
            import psutil

            memory = psutil.virtual_memory()

            if memory.percent > 90:
                await self._send_critical_alert(f"High memory usage: {memory.percent}%")

        except Exception as e:
            self.logger.error(f"Resource check error: {e}")

    async def _send_critical_alert(self, message: str):
        """Send critical alerts via multiple channels"""
        self.logger.critical(f"ALERT: {message}")

        # Write to alert file
        alert_file = Path(__file__).parent.parent / \
            "logs" / "critical_alerts.log"
        with open(alert_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")

        # Here you would integrate with Slack/Email/PagerDuty
        # For now, just ensure it's logged prominently

        # Also try to send via gh CLI
        try:
            subprocess.run(
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    f"Critical Alert: {message}",
                    "--body",
                    f"Orchestration system alert:\n\n{message}\n\nTime: {datetime.now()}",
                    "--label",
                    "critical,orchestration",
                ],
                timeout=30,
            )
        except:
            pass


async def main():
    """Main entry point"""
    daemon = OrchestrationDaemon()
    await daemon.start()


if __name__ == "__main__":
    # Create PID file
    pid_file = Path(__file__).parent.parent / "orchestration.pid"
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    try:
        asyncio.run(main())
    finally:
        # Remove PID file
        if pid_file.exists():
            pid_file.unlink()
