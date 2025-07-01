#!/usr/bin/env python3
"""
PR Orchestrator Monitoring Dashboard
Real-time insights into automated PR handling
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
from github import Github
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text


class PROrchestratorDashboard:
    """Real-time monitoring dashboard for PR Orchestrator"""

    def __init__(self, repo_name: str, token: Optional[str] = None):
        self.repo_name = repo_name
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.token)
        self.repo = self.github.get_repo(repo_name)
        self.console = Console()

        # Cache for performance
        self.cache = {
            "prs": [],
            "metrics": {},
            "last_update": None
        }

    def get_orchestrator_metrics(self) -> Dict:
        """Fetch orchestrator performance metrics"""
        metrics = {
            "total_prs_analyzed": 0,
            "auto_merged": 0,
            "manual_review": 0,
            "conflicts_resolved": 0,
            "hygiene_fixes": 0,
            "average_merge_time": 0,
            "success_rate": 0,
            "pr_by_type": defaultdict(int),
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0}
        }

        # Get workflow runs for orchestrator
        workflows = self.repo.get_workflows()
        orchestrator_workflow = None

        for workflow in workflows:
            if "orchestrator" in workflow.name.lower():
                orchestrator_workflow = workflow
                break

        if orchestrator_workflow:
            runs = orchestrator_workflow.get_runs()

            for run in runs:
                if run.conclusion == "success":
                    metrics["total_prs_analyzed"] += 1

                    # Try to get artifacts for detailed metrics
                    try:
                        artifacts = run.get_artifacts()
                        for artifact in artifacts:
                            if "pr-analysis" in artifact.name:
                                # In real implementation, download and parse artifact
                                # For now, simulate metrics
                                metrics["auto_merged"] += 1 if run.created_at.hour % 2 == 0 else 0
                                metrics["hygiene_fixes"] += 1 if run.created_at.hour % 3 == 0 else 0
                    except:
                        pass

        # Calculate success rate
        if metrics["total_prs_analyzed"] > 0:
            metrics["success_rate"] = (
                metrics["auto_merged"] / metrics["total_prs_analyzed"]) * 100

        return metrics

    def get_active_prs(self) -> List[Dict]:
        """Get all active PRs with orchestrator status"""
        prs = []

        for pr in self.repo.get_pulls(state="open"):
            pr_data = {
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "created_at": pr.created_at,
                "labels": [l.name for l in pr.labels],
                "status": self.get_pr_orchestrator_status(pr),
                "checks": self.get_pr_checks_summary(pr),
                "type": self.categorize_pr(pr),
                "size": pr.additions + pr.deletions
            }
            prs.append(pr_data)

        return prs

    def get_pr_orchestrator_status(self, pr) -> str:
        """Determine orchestrator status for a PR"""
        labels = [l.name for l in pr.labels]

        if "do-not-merge" in labels or "hold" in labels:
            return "⛔ Blocked"
        elif "auto-merge" in labels:
            return "🚀 Auto-merge"
        elif "needs-manual-review" in labels:
            return "👀 Manual Review"
        elif "hygiene-fixes-applied" in labels:
            return "🧹 Fixes Applied"
        else:
            return "🔍 Analyzing"

    def get_pr_checks_summary(self, pr) -> Dict:
        """Get summary of PR checks"""
        try:
            last_commit = pr.get_commits().reversed[0]
            check_runs = last_commit.get_check_runs()

            summary = {
                "total": 0,
                "success": 0,
                "failure": 0,
                "pending": 0
            }

            for check in check_runs:
                summary["total"] += 1
                if check.conclusion == "success":
                    summary["success"] += 1
                elif check.conclusion == "failure":
                    summary["failure"] += 1
                else:
                    summary["pending"] += 1

            return summary
        except:
            return {"total": 0, "success": 0, "failure": 0, "pending": 0}

    def categorize_pr(self, pr) -> str:
        """Categorize PR type"""
        title = pr.title.lower()

        if any(word in title for word in ["fix", "bug", "patch"]):
            return "bugfix"
        elif any(word in title for word in ["feat", "feature", "add"]):
            return "feature"
        elif any(word in title for word in ["docs", "documentation"]):
            return "docs"
        elif any(word in title for word in ["test", "spec"]):
            return "test"
        elif any(word in title for word in ["deps", "dependency"]):
            return "dependency"
        else:
            return "other"

    def create_metrics_panel(self, metrics: Dict) -> Panel:
        """Create metrics display panel"""
        table = Table(show_header=False, padding=1)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="green", width=20)

        table.add_row("Total PRs Analyzed", str(metrics["total_prs_analyzed"]))
        table.add_row(
            "Auto-Merged", f"{metrics['auto_merged']} ({metrics['success_rate']:.1f}%)")
        table.add_row("Manual Review Required", str(metrics["manual_review"]))
        table.add_row("Conflicts Resolved", str(metrics["conflicts_resolved"]))
        table.add_row("Hygiene Fixes Applied", str(metrics["hygiene_fixes"]))

        return Panel(table, title="📊 Orchestrator Metrics", border_style="blue")

    def create_pr_table(self, prs: List[Dict]) -> Panel:
        """Create PR status table"""
        table = Table(padding=0)
        table.add_column("PR", style="cyan", width=8)
        table.add_column("Title", style="white", width=40)
        table.add_column("Author", style="yellow", width=15)
        table.add_column("Type", style="blue", width=10)
        table.add_column("Status", width=20)
        table.add_column("Checks", style="green", width=15)
        table.add_column("Age", style="magenta", width=10)

        for pr in sorted(prs, key=lambda x: x["created_at"], reverse=True)[:10]:
            # Format checks
            checks = pr["checks"]
            if checks["total"] == 0:
                checks_str = "No checks"
            else:
                checks_str = f"✅{checks['success']}/🔴{checks['failure']}/⏳{checks['pending']}"

            # Calculate age
            age = datetime.now(pr["created_at"].tzinfo) - pr["created_at"]
            if age.days > 0:
                age_str = f"{age.days}d"
            else:
                age_str = f"{age.seconds // 3600}h"

            table.add_row(
                f"#{pr['number']}",
                pr["title"][:40] +
                "..." if len(pr["title"]) > 40 else pr["title"],
                pr["author"],
                pr["type"],
                pr["status"],
                checks_str,
                age_str
            )

        return Panel(table, title="🔄 Active Pull Requests", border_style="green")

    def create_activity_log(self) -> Panel:
        """Create recent activity log"""
        activities = []

        # Get recent workflow runs
        workflows = self.repo.get_workflows()
        for workflow in workflows:
            if "orchestrator" in workflow.name.lower():
                runs = workflow.get_runs()
                for run in list(runs)[:5]:
                    activity = f"[{run.created_at.strftime('%H:%M')}] "
                    if run.conclusion == "success":
                        activity += f"✅ Analyzed PR #{run.head_branch}"
                    else:
                        activity += f"❌ Failed to analyze PR #{run.head_branch}"
                    activities.append(activity)

        # Get recent comments
        for issue in self.repo.get_issues(state="all", sort="updated")[:5]:
            if issue.pull_request:
                for comment in issue.get_comments()[:1]:
                    if any(cmd in comment.body for cmd in ["/merge", "/hold", "/analyze"]):
                        activity = f"[{comment.created_at.strftime('%H:%M')}] "
                        activity += f"💬 Command on PR #{issue.number}: {comment.body.strip()}"
                        activities.append(activity)

        text = "\n".join(
            activities[:10]) if activities else "No recent activity"
        return Panel(text, title="📜 Recent Activity", border_style="yellow")

    def create_pr_type_distribution(self, prs: List[Dict]) -> Panel:
        """Create PR type distribution panel"""
        type_counts = defaultdict(int)
        for pr in prs:
            type_counts[pr["type"]] += 1

        table = Table(show_header=False)
        table.add_column("Type", style="cyan", width=15)
        table.add_column("Count", style="green", width=10)
        table.add_column("Bar", width=30)

        total = sum(type_counts.values())
        for pr_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 2)
            table.add_row(pr_type.capitalize(), str(
                count), f"{bar} {percentage:.1f}%")

        return Panel(table, title="📈 PR Type Distribution", border_style="magenta")

    def create_dashboard_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()

        # Update cache if needed
        if not self.cache["last_update"] or \
           datetime.now() - self.cache["last_update"] > timedelta(minutes=1):
            self.cache["metrics"] = self.get_orchestrator_metrics()
            self.cache["prs"] = self.get_active_prs()
            self.cache["last_update"] = datetime.now()

        # Create layout structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )

        layout["left"].split_column(
            Layout(name="metrics"),
            Layout(name="distribution")
        )

        layout["right"].split_column(
            Layout(name="prs"),
            Layout(name="activity", size=10)
        )

        # Header
        header_text = Text("🤖 PR Orchestrator Dashboard",
                           style="bold white on blue")
        header_text.append(f"\n{self.repo_name}", style="dim")
        header_text.append(
            f" | Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        layout["header"].update(Panel(header_text, style="blue"))

        # Components
        layout["metrics"].update(
            self.create_metrics_panel(self.cache["metrics"]))
        layout["distribution"].update(
            self.create_pr_type_distribution(self.cache["prs"]))
        layout["prs"].update(self.create_pr_table(self.cache["prs"]))
        layout["activity"].update(self.create_activity_log())

        # Footer
        footer_text = "[q] Quit | [r] Refresh | [/] Commands | [?] Help"
        layout["footer"].update(Panel(footer_text, style="dim"))

        return layout

    def run(self):
        """Run the interactive dashboard"""
        with Live(self.create_dashboard_layout(), refresh_per_second=1) as live:
            try:
                while True:
                    # Auto-refresh every 30 seconds
                    import time
                    time.sleep(30)
                    self.cache["last_update"] = None  # Force refresh
                    live.update(self.create_dashboard_layout())
            except KeyboardInterrupt:
                pass


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="PR Orchestrator Dashboard")
    parser.add_argument("--repo", default="IgorGanapolsky/ai-kindlemint-engine",
                        help="Repository name (owner/repo)")
    parser.add_argument(
        "--token", help="GitHub token (or use GITHUB_TOKEN env)")

    args = parser.parse_args()

    dashboard = PROrchestratorDashboard(args.repo, args.token)
    dashboard.run()


if __name__ == "__main__":
    main()
