#!/usr/bin/env python3
"""
Claude Cost Scheduler
Manages automated Claude cost notifications and reports
"""

from scripts.claude_cost_tracker import ClaudeCostTracker
from scripts.claude_cost_slack_notifier import ClaudeCostSlackNotifier
import argparse
import json
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Optional

import schedule

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ClaudeCostScheduler")


class ClaudeCostScheduler:
    """Manages scheduled Claude cost notifications"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the scheduler"""
        self.config_file = config_file or os.path.join(
            Path.home(), ".claude-cost-scheduler.json"
        )
        self.config = self._load_config()
        self.notifier = ClaudeCostSlackNotifier()
        self.tracker = ClaudeCostTracker()
        self.running = False

    def _load_config(self) -> Dict:
        """Load scheduler configuration"""
        default_config = {
            "daily_summary": {"enabled": True, "time": "09:00", "timezone": "local"},
            "weekly_summary": {"enabled": True, "day": "monday", "time": "09:00"},
            "budget_alerts": {
                "enabled": True,
                "daily_limit": 5.00,
                "weekly_limit": 25.00,
                "monthly_limit": 100.00,
                "check_interval": 60,  # minutes
            },
            "efficiency_reports": {
                "enabled": True,
                "frequency": "weekly",
                "day": "friday",
                "time": "15:00",
            },
            "realtime_commits": {
                "enabled": True,
                "min_cost_threshold": 0.10,  # Only notify for commits above this cost
            },
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in loaded_config:
                            default_config[key].update(loaded_config[key])
                    return default_config
            except Exception as e:
                logger.error(f"Error loading config: {e}")

        return default_config

    def save_config(self) -> None:
        """Save current configuration"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def setup_schedules(self) -> None:
        """Set up all scheduled jobs"""
        logger.info("Setting up scheduled jobs...")

        # Daily summary
        if self.config["daily_summary"]["enabled"]:
            schedule.every().day.at(self.config["daily_summary"]["time"]).do(
                self._run_daily_summary
            )
            logger.info(
                f"Daily summary scheduled at {self.config['daily_summary']['time']}"
            )

        # Weekly summary
        if self.config["weekly_summary"]["enabled"]:
            day = self.config["weekly_summary"]["day"].lower()
            time_str = self.config["weekly_summary"]["time"]

            if day == "monday":
                schedule.every().monday.at(time_str).do(self._run_weekly_summary)
            elif day == "tuesday":
                schedule.every().tuesday.at(time_str).do(self._run_weekly_summary)
            elif day == "wednesday":
                schedule.every().wednesday.at(time_str).do(self._run_weekly_summary)
            elif day == "thursday":
                schedule.every().thursday.at(time_str).do(self._run_weekly_summary)
            elif day == "friday":
                schedule.every().friday.at(time_str).do(self._run_weekly_summary)
            elif day == "saturday":
                schedule.every().saturday.at(time_str).do(self._run_weekly_summary)
            elif day == "sunday":
                schedule.every().sunday.at(time_str).do(self._run_weekly_summary)

            logger.info(f"Weekly summary scheduled for {day}s at {time_str}")

        # Budget alerts
        if self.config["budget_alerts"]["enabled"]:
            interval = self.config["budget_alerts"]["check_interval"]
            schedule.every(interval).minutes.do(self._check_budgets)
            logger.info(f"Budget checks scheduled every {interval} minutes")

        # Efficiency reports
        if self.config["efficiency_reports"]["enabled"]:
            freq = self.config["efficiency_reports"]["frequency"]
            if freq == "weekly":
                day = self.config["efficiency_reports"]["day"].lower()
                time_str = self.config["efficiency_reports"]["time"]

                if day == "monday":
                    schedule.every().monday.at(time_str).do(self._run_efficiency_report)
                elif day == "tuesday":
                    schedule.every().tuesday.at(time_str).do(
                        self._run_efficiency_report
                    )
                elif day == "wednesday":
                    schedule.every().wednesday.at(time_str).do(
                        self._run_efficiency_report
                    )
                elif day == "thursday":
                    schedule.every().thursday.at(time_str).do(
                        self._run_efficiency_report
                    )
                elif day == "friday":
                    schedule.every().friday.at(time_str).do(self._run_efficiency_report)
                elif day == "saturday":
                    schedule.every().saturday.at(time_str).do(
                        self._run_efficiency_report
                    )
                elif day == "sunday":
                    schedule.every().sunday.at(time_str).do(self._run_efficiency_report)

                logger.info(f"Efficiency reports scheduled for {day}s at {time_str}")
            elif freq == "daily":
                schedule.every().day.at(self.config["efficiency_reports"]["time"]).do(
                    self._run_efficiency_report
                )
                logger.info(
                    f"Daily efficiency reports scheduled at {
                        self.config['efficiency_reports']['time']}"
                )

    def _run_daily_summary(self) -> None:
        """Run daily summary notification"""
        logger.info("Running daily summary...")
        try:
            if self.notifier.send_daily_summary():
                logger.info("Daily summary sent successfully")
            else:
                logger.warning("Failed to send daily summary")
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

    def _run_weekly_summary(self) -> None:
        """Run weekly summary notification"""
        logger.info("Running weekly summary...")
        try:
            if self.notifier.send_weekly_summary():
                logger.info("Weekly summary sent successfully")
            else:
                logger.warning("Failed to send weekly summary")
        except Exception as e:
            logger.error(f"Error sending weekly summary: {e}")

    def _run_efficiency_report(self) -> None:
        """Run efficiency report notification"""
        logger.info("Running efficiency report...")
        try:
            if self.notifier.send_efficiency_report():
                logger.info("Efficiency report sent successfully")
            else:
                logger.warning("Failed to send efficiency report")
        except Exception as e:
            logger.error(f"Error sending efficiency report: {e}")

    def _check_budgets(self) -> None:
        """Check budget limits and send alerts if exceeded"""
        logger.info("Checking budget limits...")
        try:
            config = self.config["budget_alerts"]

            # Check daily budget
            if config.get("daily_limit"):
                self.notifier.send_budget_alert(config["daily_limit"], "daily")

            # Check weekly budget
            if config.get("weekly_limit"):
                self.notifier.send_budget_alert(config["weekly_limit"], "weekly")

            # Check monthly budget
            if config.get("monthly_limit"):
                self.notifier.send_budget_alert(config["monthly_limit"], "monthly")

        except Exception as e:
            logger.error(f"Error checking budgets: {e}")

    def monitor_git_commits(self) -> None:
        """Monitor git repository for new commits"""
        if not self.config["realtime_commits"]["enabled"]:
            return

        logger.info("Starting git commit monitoring...")
        last_commit_hash = self._get_latest_commit_hash()

        while self.running:
            try:
                time.sleep(10)  # Check every 10 seconds
                current_hash = self._get_latest_commit_hash()

                if current_hash and current_hash != last_commit_hash:
                    logger.info(f"New commit detected: {current_hash}")

                    # Check commit cost
                    commit_costs = self.tracker.load_commit_costs()
                    for commit in commit_costs.get("commits", []):
                        if commit["hash"] == current_hash[:8]:
                            cost = commit["cost"]
                            threshold = self.config["realtime_commits"][
                                "min_cost_threshold"
                            ]

                            if cost >= threshold:
                                logger.info(
                                    f"Commit cost ${
                                        cost:.4f} exceeds threshold ${threshold}"
                                )
                                self.notifier.send_commit_notification(current_hash)
                            break

                    last_commit_hash = current_hash

            except Exception as e:
                logger.error(f"Error monitoring commits: {e}")

    def _get_latest_commit_hash(self) -> Optional[str]:
        """Get the latest commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except BaseException:
            return None

    def run(self) -> None:
        """Run the scheduler"""
        self.running = True

        # Start git monitoring in separate thread
        git_thread = threading.Thread(target=self.monitor_git_commits)
        git_thread.daemon = True
        git_thread.start()

        logger.info("Claude Cost Scheduler started. Press Ctrl+C to stop.")
        logger.info(f"Configuration file: {self.config_file}")

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.running = False

    def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        logger.info("Stopping scheduler...")

    def test_notifications(self) -> None:
        """Test all notification types"""
        logger.info("Testing all notification types...")

        tests = [
            ("Daily Summary", self.notifier.send_daily_summary),
            ("Weekly Summary", self.notifier.send_weekly_summary),
            ("Efficiency Report", self.notifier.send_efficiency_report),
            (
                "Budget Alert (Daily)",
                lambda: self.notifier.send_budget_alert(1.00, "daily"),
            ),
        ]

        for name, func in tests:
            try:
                logger.info(f"Testing {name}...")
                if func():
                    logger.info(f"✅ {name} sent successfully")
                else:
                    logger.warning(f"❌ {name} failed")
                time.sleep(2)  # Avoid rate limiting
            except Exception as e:
                logger.error(f"❌ {name} error: {e}")


def create_systemd_service() -> None:
    """Create systemd service file for Linux systems"""
    service_content = """[Unit]
Description=Claude Cost Scheduler
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
Environment="PATH={path}"
ExecStart={python} {script_path} run
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""

    # Get current user and paths
    import pwd

    user = pwd.getpwuid(os.getuid()).pw_name
    working_dir = Path.cwd()
    python_path = sys.executable
    script_path = Path(__file__).resolve()
    path = os.environ.get("PATH", "/usr/bin:/bin")

    service_file = service_content.format(
        user=user,
        working_dir=working_dir,
        python=python_path,
        script_path=script_path,
        path=path,
    )

    service_path = Path.home() / ".config/systemd/user/claude-cost-scheduler.service"
    service_path.parent.mkdir(parents=True, exist_ok=True)

    with open(service_path, "w") as f:
        f.write(service_file)

    print(f"✅ Systemd service file created: {service_path}")
    print("\nTo enable the service, run:")
    print("  systemctl --user daemon-reload")
    print("  systemctl --user enable claude-cost-scheduler")
    print("  systemctl --user start claude-cost-scheduler")
    print("\nTo check status:")
    print("  systemctl --user status claude-cost-scheduler")


def create_launchd_plist() -> None:
    """Create launchd plist file for macOS"""
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudeflow.cost-scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>{script_path}</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{working_dir}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{path}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_dir}/claude-cost-scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>{log_dir}/claude-cost-scheduler.error.log</string>
</dict>
</plist>
"""

    # Get paths
    working_dir = Path.cwd()
    python_path = sys.executable
    script_path = Path(__file__).resolve()
    path = os.environ.get("PATH", "/usr/bin:/bin:/usr/local/bin")
    log_dir = Path.home() / "Library/Logs"

    plist_file = plist_content.format(
        python=python_path,
        script_path=script_path,
        working_dir=working_dir,
        path=path,
        log_dir=log_dir,
    )

    plist_path = (
        Path.home() / "Library/LaunchAgents/com.claudeflow.cost-scheduler.plist"
    )
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    with open(plist_path, "w") as f:
        f.write(plist_file)

    print(f"✅ LaunchAgent plist created: {plist_path}")
    print("\nTo enable the service, run:")
    print(f"  launchctl load {plist_path}")
    print("\nTo check status:")
    print("  launchctl list | grep claudeflow")
    print("\nTo stop the service:")
    print(f"  launchctl unload {plist_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Claude Cost Scheduler - Automated cost notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude_cost_scheduler run              # Run the scheduler
  claude_cost_scheduler test             # Test all notifications
  claude_cost_scheduler config           # Show current configuration
  claude_cost_scheduler install-service  # Install as system service
        """,
    )

    parser.add_argument(
        "command",
        choices=["run", "test", "config", "install-service"],
        help="Command to execute",
    )
    parser.add_argument("--config", help="Path to configuration file")

    args = parser.parse_args()

    # Check if Slack is configured
    if not os.getenv("SLACK_WEBHOOK_URL"):
        print("⚠️  Warning: SLACK_WEBHOOK_URL not set. Notifications will not be sent.")
        print("   Set the environment variable to enable Slack notifications.")

    scheduler = ClaudeCostScheduler(args.config)

    if args.command == "run":
        scheduler.setup_schedules()
        scheduler.run()

    elif args.command == "test":
        scheduler.test_notifications()

    elif args.command == "config":
        print("Current configuration:")
        print(json.dumps(scheduler.config, indent=2))
        print(f"\nConfiguration file: {scheduler.config_file}")

    elif args.command == "install-service":
        system = os.uname().sysname.lower()
        if system == "darwin":
            create_launchd_plist()
        elif system == "linux":
            create_systemd_service()
        else:
            print(f"❌ Service installation not supported on {system}")
            print("   You can use cron to schedule the notifications:")
            print(f"   0 9 * * * {sys.executable} {Path(__file__).resolve()} run")


if __name__ == "__main__":
    main()
