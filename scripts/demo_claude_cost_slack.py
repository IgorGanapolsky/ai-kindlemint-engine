#!/usr/bin/env python3
"""
Demo script to showcase Claude Cost Slack Notifications
"""

import os
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.claude_cost_slack_notifier import ClaudeCostSlackNotifier
from scripts.claude_cost_tracker import ClaudeCostTracker


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def main():
    print_header("🤖 Claude Cost Slack Notifications Demo")

    # Check if Slack is configured
    if not os.getenv("SLACK_WEBHOOK_URL"):
        print("⚠️  SLACK_WEBHOOK_URL not set!")
        print("\nTo see the demo with actual Slack messages:")
        print("1. Create a Slack webhook: https://api.slack.com/messaging/webhooks")
        print("2. Export it: export SLACK_WEBHOOK_URL='your-webhook-url'")
        print("\nContinuing with console output only...\n")
        time.sleep(2)

    # Initialize components
    notifier = ClaudeCostSlackNotifier()
    ClaudeCostTracker()

    # Show current status
    print_header("📊 Current Cost Status")
    os.system("./claude-flow-costs status")

    print("\nPress Enter to continue...")
    input()

    # Demo 1: Daily Summary
    print_header("📅 Demo 1: Daily Summary Notification")
    print("This notification is sent every morning at 9 AM")
    print("It includes today's costs, commits, and recommendations")
    print("\nSending daily summary to Slack...")

    if notifier.send_daily_summary():
        print("✅ Daily summary sent successfully!")
    else:
        print("ℹ️  Daily summary would be sent (Slack not configured or no data)")

    time.sleep(2)

    # Demo 2: Weekly Analysis
    print_header("📈 Demo 2: Weekly Analysis Notification")
    print("This notification is sent every Monday morning")
    print("It includes week-over-week trends and insights")
    print("\nSending weekly analysis to Slack...")

    if notifier.send_weekly_summary():
        print("✅ Weekly analysis sent successfully!")
    else:
        print("ℹ️  Weekly analysis would be sent (Slack not configured or no data)")

    time.sleep(2)

    # Demo 3: Budget Alert
    print_header("🚨 Demo 3: Budget Alert Notification")
    print("This notification is triggered when costs exceed limits")
    print("Testing with a $1.00 daily budget...")
    print("\nChecking budget and sending alert if needed...")

    if notifier.send_budget_alert(1.00, "daily"):
        print("✅ Budget alert sent - costs exceed $1.00!")
    else:
        print("ℹ️  No budget alert needed - within limits")

    time.sleep(2)

    # Demo 4: Efficiency Report
    print_header("⚡ Demo 4: Efficiency Report Notification")
    print("This notification is sent every Friday at 3 PM")
    print("It includes efficiency metrics and optimization tips")
    print("\nSending efficiency report to Slack...")

    if notifier.send_efficiency_report():
        print("✅ Efficiency report sent successfully!")
    else:
        print("ℹ️  Efficiency report would be sent (Slack not configured or no data)")

    time.sleep(2)

    # Show setup instructions
    print_header("🚀 Setting Up Continuous Notifications")
    print("To receive these notifications automatically:")
    print("\n1. Set up Slack webhook:")
    print("   export SLACK_WEBHOOK_URL='your-webhook-url'")
    print("\n2. Run the setup script:")
    print("   ./claude-flow-costs-notify setup")
    print("\n3. Or run the continuous scheduler:")
    print("   ./claude-flow-costs-notify scheduler")
    print("\nScheduled notifications:")
    print("  • Daily summaries at 9:00 AM")
    print("  • Weekly analysis on Mondays at 9:00 AM")
    print("  • Efficiency reports on Fridays at 3:00 PM")
    print("  • Budget checks every hour during work hours")
    print("  • Per-commit notifications (for commits > $0.10)")

    print_header("📚 Documentation")
    print("Full documentation available at:")
    print("  • docs/CLAUDE_COST_TRACKING.md")
    print("  • docs/CLAUDE_COST_SLACK_NOTIFICATIONS.md")
    print("\nCommands:")
    print("  • ./claude-flow-costs status")
    print("  • ./claude-flow-costs summary --days 7")
    print("  • ./claude-flow-costs-notify test")
    print("  • ./claude-flow-costs-notify scheduler")


if __name__ == "__main__":
    main()
