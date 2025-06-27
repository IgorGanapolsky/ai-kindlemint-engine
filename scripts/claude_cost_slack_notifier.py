#!/usr/bin/env python3
"""
Claude Cost Slack Notifier
Sends Claude API cost tracking notifications to Slack
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.claude_cost_tracker import ClaudeCostTracker
from scripts.slack_notifier import SlackNotifier


class ClaudeCostSlackNotifier:
    """Specialized Slack notifier for Claude cost tracking"""

    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize the Claude cost Slack notifier"""
        self.slack_notifier = SlackNotifier(webhook_url)
        self.cost_tracker = ClaudeCostTracker()
        self.repo_name = self._get_repo_name()

    def _get_repo_name(self) -> str:
        """Get repository name from git"""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=True,
            )
            url = result.stdout.strip()
            # Extract repo name from URL
            if "/" in url:
                return url.split("/")[-1].replace(".git", "")
            return "Unknown Repository"
        except:
            return "Unknown Repository"

    def send_commit_notification(self, commit_hash: str) -> bool:
        """Send notification for a specific commit"""
        commit_costs = self.cost_tracker.load_commit_costs()

        # Find the commit
        commit_data = None
        for commit in commit_costs.get("commits", []):
            if commit["hash"] == commit_hash[:8]:
                commit_data = commit
                break

        if not commit_data:
            return False

        # Determine color based on cost
        cost = commit_data["cost"]
        if cost < 0.10:
            color = "#2ecc71"  # Green - low cost
            emoji = "💚"
        elif cost < 0.50:
            color = "#f39c12"  # Orange - medium cost
            emoji = "💛"
        else:
            color = "#e74c3c"  # Red - high cost
            emoji = "❤️"

        # Create rich message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 Claude Cost Update - {self.repo_name}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*New commit tracked:* `{commit_hash[:8]}`",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Cost:*\n{emoji} ${cost:.4f}"},
                    {"type": "mrkdwn", "text": f"*Tokens:*\n{commit_data['tokens']:,}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Files:*\n{commit_data['files_changed']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Model:*\n{commit_data.get('model', 'claude-3-sonnet')}",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message:* {commit_data['message']}",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Claude Cost Tracker",
                    }
                ],
            },
        ]

        return self.slack_notifier.send_message(
            text=f"Claude Cost: ${cost:.4f} for commit {commit_hash[:8]}",
            blocks=blocks,
            color=color,
        )

    def send_daily_summary(self) -> bool:
        """Send daily cost summary"""
        summary = self.cost_tracker.get_cost_summary(days=1)

        if "error" in summary:
            return False

        # Calculate efficiency metrics
        commits = summary["commit_count"]
        total_cost = summary["total_cost"]
        avg_cost = summary["average_cost_per_commit"]

        # Determine status
        if total_cost < 1.0:
            status = "✅ EXCELLENT - Low costs"
            color = "#2ecc71"
        elif total_cost < 5.0:
            status = "⚠️ MODERATE - Monitor usage"
            color = "#f39c12"
        else:
            status = "🚨 HIGH - Review needed"
            color = "#e74c3c"

        # Create rich message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Daily Claude Cost Report - {self.repo_name}",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Status:* {status}"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*📈 TODAY'S METRICS*"},
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Cost:*\n${total_cost:.2f}"},
                    {"type": "mrkdwn", "text": f"*Commits:*\n{commits}"},
                    {"type": "mrkdwn", "text": f"*Avg/Commit:*\n${avg_cost:.4f}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tokens:*\n{summary['total_tokens']:,}",
                    },
                ],
            },
        ]

        # Add most expensive commit if available
        if summary.get("most_expensive_commit"):
            commit = summary["most_expensive_commit"]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*💸 Most Expensive Commit:*\n`{commit['hash']}` - ${commit['cost']:.4f}\n_{commit['message'][:60]}..._",
                    },
                }
            )

        # Add recommendations
        recommendations = self._generate_daily_recommendations(summary)
        if recommendations:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*💡 RECOMMENDATIONS*\n" + "\n".join(recommendations),
                    },
                }
            )

        # Add context
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | View details: `./claude-flow-costs status`",
                    }
                ],
            }
        )

        return self.slack_notifier.send_message(
            text=f"Daily Claude Cost Report: ${total_cost:.2f} ({commits} commits)",
            blocks=blocks,
            color=color,
        )

    def send_weekly_summary(self) -> bool:
        """Send weekly cost summary with trends"""
        current_week = self.cost_tracker.get_cost_summary(days=7)
        previous_week = self.cost_tracker.get_cost_summary(days=14)

        if "error" in current_week:
            return False

        # Calculate week-over-week changes
        current_cost = current_week["total_cost"]

        # Get previous week data (last 14 days minus last 7 days)
        if "error" not in previous_week:
            # Filter commits to get only previous week
            all_commits = self.cost_tracker.load_commit_costs()["commits"]
            week_ago = datetime.now() - timedelta(days=7)
            two_weeks_ago = datetime.now() - timedelta(days=14)

            previous_week_commits = [
                c
                for c in all_commits
                if two_weeks_ago <= datetime.fromisoformat(c["timestamp"]) < week_ago
            ]

            previous_cost = sum(c["cost"] for c in previous_week_commits)
            cost_change = current_cost - previous_cost
            cost_change_pct = (
                (cost_change / previous_cost * 100) if previous_cost > 0 else 0
            )
        else:
            previous_cost = 0
            cost_change = current_cost
            cost_change_pct = 100

        # Determine trend
        if cost_change_pct < -20:
            trend = "📉 Significant decrease"
            trend_emoji = "🎉"
        elif cost_change_pct < 0:
            trend = "📉 Decrease"
            trend_emoji = "✅"
        elif cost_change_pct < 20:
            trend = "📊 Stable"
            trend_emoji = "➡️"
        elif cost_change_pct < 50:
            trend = "📈 Increase"
            trend_emoji = "⚠️"
        else:
            trend = "📈 Significant increase"
            trend_emoji = "🚨"

        # Create rich message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Weekly Claude Cost Analysis - {self.repo_name}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Week-over-Week Trend:* {trend} {trend_emoji}",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*📈 THIS WEEK'S SUMMARY*"},
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Cost:*\n${current_cost:.2f}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Change:*\n{'+' if cost_change >= 0 else ''}${cost_change:.2f} ({cost_change_pct:+.1f}%)",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Commits:*\n{current_week['commit_count']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Avg/Commit:*\n${current_week['average_cost_per_commit']:.4f}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tokens:*\n{current_week['total_tokens']:,}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Projected Monthly:*\n${(current_cost * 4.3):.2f}",
                    },
                ],
            },
        ]

        # Add cost breakdown by day
        daily_costs = self._calculate_daily_costs(7)
        if daily_costs:
            chart_text = "*📊 DAILY BREAKDOWN*\n```\n"
            for day, cost in daily_costs:
                bar_length = int(cost / max(d[1] for d in daily_costs) * 20)
                bar = "█" * bar_length
                chart_text += f"{day}: {bar} ${cost:.2f}\n"
            chart_text += "```"

            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": chart_text}}
            )

        # Add efficiency insights
        insights = self._generate_weekly_insights(current_week, previous_week)
        if insights:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🔍 INSIGHTS & RECOMMENDATIONS*\n"
                        + "\n".join(insights),
                    },
                }
            )

        # Add context
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Export: `./claude-flow-costs export weekly_report.csv`",
                    }
                ],
            }
        )

        return self.slack_notifier.send_message(
            text=f"Weekly Claude Cost Analysis: ${current_cost:.2f} ({cost_change_pct:+.1f}% change)",
            blocks=blocks,
            color="#3498db",
        )

    def send_budget_alert(self, budget_limit: float, period: str = "daily") -> bool:
        """Send budget alert when threshold is exceeded"""
        days = 1 if period == "daily" else 7 if period == "weekly" else 30
        summary = self.cost_tracker.get_cost_summary(days=days)

        if "error" in summary:
            return False

        current_cost = summary["total_cost"]

        if current_cost <= budget_limit:
            return False  # No alert needed

        overage = current_cost - budget_limit
        overage_pct = (overage / budget_limit) * 100

        # Create alert message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 CLAUDE COST BUDGET ALERT - {self.repo_name}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⚠️ {period.capitalize()} budget exceeded by {overage_pct:.1f}%*",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Budget Limit:*\n${budget_limit:.2f}"},
                    {"type": "mrkdwn", "text": f"*Current Cost:*\n${current_cost:.2f}"},
                    {"type": "mrkdwn", "text": f"*Overage:*\n${overage:.2f}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Period:*\n{period.capitalize()} ({days} days)",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🛑 IMMEDIATE ACTIONS RECOMMENDED:*\n• Review recent commits for expensive operations\n• Consider using Claude Haiku for simpler tasks\n• Batch similar changes to reduce API calls\n• Enable cost pre-approval for large changes",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 Alert triggered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    }
                ],
            },
        ]

        return self.slack_notifier.send_message(
            text=f"🚨 Claude Cost Budget Alert: ${current_cost:.2f} exceeds ${budget_limit:.2f} limit",
            blocks=blocks,
            color="#e74c3c",
        )

    def send_efficiency_report(self) -> bool:
        """Send efficiency analysis report"""
        # Get data for analysis
        summary_7d = self.cost_tracker.get_cost_summary(days=7)
        summary_30d = self.cost_tracker.get_cost_summary(days=30)

        if "error" in summary_7d or "error" in summary_30d:
            return False

        # Load detailed commit data
        commit_costs = self.cost_tracker.load_commit_costs()
        recent_commits = commit_costs["commits"][-20:]  # Last 20 commits

        # Calculate efficiency metrics
        tokens_per_dollar = summary_7d["total_tokens"] / max(
            summary_7d["total_cost"], 0.01
        )
        commits_per_dollar = summary_7d["commit_count"] / max(
            summary_7d["total_cost"], 0.01
        )

        # Find patterns
        expensive_files = self._analyze_expensive_patterns(recent_commits)
        time_patterns = self._analyze_time_patterns(recent_commits)

        # Create efficiency report
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"⚡ Claude Cost Efficiency Report - {self.repo_name}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 EFFICIENCY METRICS (Last 7 Days)*",
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Tokens per Dollar:*\n{tokens_per_dollar:,.0f}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Commits per Dollar:*\n{commits_per_dollar:.2f}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Avg Token Usage:*\n{summary_7d['total_tokens'] // max(summary_7d['commit_count'], 1):,}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Cost Efficiency:*\n{'🟢 High' if tokens_per_dollar > 200000 else '🟡 Medium' if tokens_per_dollar > 100000 else '🔴 Low'}",
                    },
                ],
            },
        ]

        # Add expensive file patterns
        if expensive_files:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*💸 EXPENSIVE FILE PATTERNS*\n"
                        + "\n".join(expensive_files[:5]),
                    },
                }
            )

        # Add time-based insights
        if time_patterns:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🕐 TIME-BASED INSIGHTS*\n" + "\n".join(time_patterns),
                    },
                }
            )

        # Add optimization recommendations
        optimizations = self._generate_optimization_recommendations(
            summary_7d, summary_30d
        )
        if optimizations:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🚀 OPTIMIZATION OPPORTUNITIES*\n"
                        + "\n".join(optimizations),
                    },
                }
            )

        # Add context
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 Analysis period: {datetime.now().strftime('%Y-%m-%d')} | Full report: `./claude-flow-costs details --last 50`",
                    }
                ],
            }
        )

        return self.slack_notifier.send_message(
            text=f"Claude Cost Efficiency Report: {tokens_per_dollar:,.0f} tokens per dollar",
            blocks=blocks,
            color="#9b59b6",
        )

    def _calculate_daily_costs(self, days: int) -> List[Tuple[str, float]]:
        """Calculate costs for each day"""
        commit_costs = self.cost_tracker.load_commit_costs()
        daily_costs = {}

        for commit in commit_costs.get("commits", []):
            commit_date = datetime.fromisoformat(commit["timestamp"]).date()
            if (datetime.now().date() - commit_date).days < days:
                day_str = commit_date.strftime("%a")
                daily_costs[day_str] = daily_costs.get(day_str, 0) + commit["cost"]

        # Sort by day of week
        days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return [
            (day, daily_costs.get(day, 0)) for day in days_order if day in daily_costs
        ]

    def _generate_daily_recommendations(self, summary: Dict) -> List[str]:
        """Generate recommendations based on daily usage"""
        recommendations = []

        if summary["total_cost"] > 5.0:
            recommendations.append(
                "• Consider batching similar changes to reduce API calls"
            )

        if summary["average_cost_per_commit"] > 0.50:
            recommendations.append("• Review file sizes - large files increase costs")
            recommendations.append("• Use Claude Haiku for simpler code changes")

        if summary["commit_count"] > 20:
            recommendations.append(
                "• High commit volume - consider grouping related changes"
            )

        return recommendations

    def _generate_weekly_insights(
        self, current_week: Dict, previous_week: Dict
    ) -> List[str]:
        """Generate insights comparing weeks"""
        insights = []

        # Token efficiency
        current_tpd = current_week["total_tokens"] / max(
            current_week["total_cost"], 0.01
        )
        insights.append(f"• Token efficiency: {current_tpd:,.0f} tokens per dollar")

        # Cost trends
        if current_week["total_cost"] > 10:
            insights.append(
                "• 💰 Consider setting daily budget limits to control costs"
            )

        # Commit patterns
        if current_week["commit_count"] > 50:
            insights.append(
                "• 📈 High commit frequency - explore batch processing options"
            )

        # Model recommendations
        if current_week["average_cost_per_commit"] > 0.30:
            insights.append(
                "• 🤖 Switch to Claude Haiku for routine tasks (80% cost reduction)"
            )

        return insights

    def _analyze_expensive_patterns(self, commits: List[Dict]) -> List[str]:
        """Analyze patterns in expensive commits"""
        patterns = []

        # Group by file patterns
        file_costs = {}
        for commit in commits:
            if commit["cost"] > 0.10:  # Focus on expensive commits
                # This is simplified - in real implementation, we'd analyze actual files
                msg = commit["message"].lower()
                if "test" in msg:
                    file_costs["test files"] = (
                        file_costs.get("test files", 0) + commit["cost"]
                    )
                elif "doc" in msg:
                    file_costs["documentation"] = (
                        file_costs.get("documentation", 0) + commit["cost"]
                    )
                elif "config" in msg:
                    file_costs["configuration"] = (
                        file_costs.get("configuration", 0) + commit["cost"]
                    )

        # Sort by cost
        sorted_patterns = sorted(file_costs.items(), key=lambda x: x[1], reverse=True)

        for pattern, cost in sorted_patterns[:3]:
            patterns.append(f"• {pattern.capitalize()}: ${cost:.2f} total cost")

        return patterns

    def _analyze_time_patterns(self, commits: List[Dict]) -> List[str]:
        """Analyze time-based patterns"""
        patterns = []

        # Hour analysis
        hour_costs = {}
        for commit in commits:
            hour = datetime.fromisoformat(commit["timestamp"]).hour
            hour_costs[hour] = hour_costs.get(hour, 0) + commit["cost"]

        # Find peak hours
        if hour_costs:
            peak_hour = max(hour_costs.items(), key=lambda x: x[1])
            patterns.append(
                f"• Peak usage hour: {peak_hour[0]:02d}:00 (${peak_hour[1]:.2f})"
            )

        # Day of week analysis
        dow_costs = {}
        for commit in commits:
            dow = datetime.fromisoformat(commit["timestamp"]).strftime("%A")
            dow_costs[dow] = dow_costs.get(dow, 0) + commit["cost"]

        if dow_costs:
            peak_day = max(dow_costs.items(), key=lambda x: x[1])
            patterns.append(f"• Most expensive day: {peak_day[0]} (${peak_day[1]:.2f})")

        return patterns

    def _generate_optimization_recommendations(
        self, week_data: Dict, month_data: Dict
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Model optimization
        avg_cost = week_data["average_cost_per_commit"]
        if avg_cost > 0.20:
            savings = (
                (avg_cost - 0.05) * week_data["commit_count"] * 4
            )  # Monthly savings
            recommendations.append(
                f"• Switch to Haiku for routine tasks: Save ~${savings:.2f}/month"
            )

        # Batching optimization
        if week_data["commit_count"] > 30:
            recommendations.append(
                "• Implement change batching: Reduce costs by 30-40%"
            )

        # Time-based optimization
        recommendations.append("• Schedule non-urgent changes during off-peak hours")

        # File-based optimization
        if week_data["total_tokens"] > 500000:
            recommendations.append(
                "• Use .claudeignore to exclude large generated files"
            )

        return recommendations


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Send Claude cost notifications to Slack"
    )
    parser.add_argument(
        "notification_type",
        choices=["commit", "daily", "weekly", "budget", "efficiency"],
        help="Type of notification to send",
    )
    parser.add_argument("--commit-hash", help="Commit hash for commit notification")
    parser.add_argument(
        "--budget-limit", type=float, help="Budget limit for budget alerts"
    )
    parser.add_argument(
        "--budget-period",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Budget period",
    )

    args = parser.parse_args()

    notifier = ClaudeCostSlackNotifier()

    if not notifier.slack_notifier.enabled:
        print("⚠️ Slack notifications disabled - set SLACK_WEBHOOK_URL to enable")
        sys.exit(1)

    success = False

    if args.notification_type == "commit":
        if not args.commit_hash:
            print("❌ --commit-hash required for commit notifications")
            sys.exit(1)
        success = notifier.send_commit_notification(args.commit_hash)

    elif args.notification_type == "daily":
        success = notifier.send_daily_summary()

    elif args.notification_type == "weekly":
        success = notifier.send_weekly_summary()

    elif args.notification_type == "budget":
        if not args.budget_limit:
            print("❌ --budget-limit required for budget alerts")
            sys.exit(1)
        success = notifier.send_budget_alert(args.budget_limit, args.budget_period)

    elif args.notification_type == "efficiency":
        success = notifier.send_efficiency_report()

    if success:
        print(f"✅ {args.notification_type.capitalize()} notification sent!")
    else:
        print(f"❌ Failed to send {args.notification_type} notification")
        sys.exit(1)
