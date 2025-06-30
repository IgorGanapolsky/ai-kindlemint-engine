#!/usr/bin/env python3
"""
GitHub Issues Manager - Automated issue and PR handling with monitoring
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sentry_config import init_sentry, track_kdp_operation
from slack_notifier import SlackNotifier

from kindlemint.agents.github_issues_agent import GitHubActionType, GitHubIssuesAgent
from kindlemint.agents.task_system import Task, TaskPriority, TaskType

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "scripts"))


# Initialize monitoring
init_sentry()


class GitHubIssuesManager:
    """Manager for GitHub issues with Slack notifications"""

    def __init__(self, repo: str = "IgorGanapolsky/ai-kindlemint-engine"):
        self.repo = repo
        self.agent = GitHubIssuesAgent(repo=repo)
        self.slack_notifier = None

        # Initialize Slack if configured
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if webhook_url:
            self.slack_notifier = SlackNotifier(webhook_url)

    async def process_all_issues(self) -> Dict[str, Any]:
        """Process all open issues and PRs"""
        with track_kdp_operation("github_issues_processing"):
            # Generate report first
            report_task = Task(
                task_type=TaskType.GENERATE_REPORTS,
                input_data={
                    "action_type": GitHubActionType.GENERATE_REPORT.value},
                priority=TaskPriority.NORMAL,
            )

            result = await self.agent.process_task(report_task)

            if not result.success:
                self._send_error_notification(
                    "Failed to generate issues report", result.error_message
                )
                return {"success": False, "error": result.error_message}

            report = result.output_data

            # Process security PRs
            security_results = await self._process_security_items(report)

            # Send summary to Slack
            self._send_summary_notification(report, security_results)

            return {
                "success": True,
                "report": report,
                "security_results": security_results,
            }

    async def _process_security_items(self, report: Dict) -> List[Dict]:
        """Process security-related issues and PRs"""
        results = []

        # Find Pixeebot PRs
        for pr in report.get("pull_requests", []):
            if pr["author"]["login"].lower() == "pixeebot" and pr["state"] == "OPEN":
                # Review security PR
                task = Task(
                    task_type=TaskType.ANALYZE_PERFORMANCE,  # Using as proxy
                    input_data={
                        "action_type": GitHubActionType.SECURITY_REVIEW.value,
                        "pr_number": pr["number"],
                        "auto_approve": True,  # Auto-approve Pixeebot improvements
                    },
                    priority=TaskPriority.HIGH,
                )

                result = await self.agent.process_task(task)
                results.append(
                    {
                        "pr_number": pr["number"],
                        "title": pr["title"],
                        "result": (
                            result.output_data
                            if result.success
                            else {"error": result.error_message}
                        ),
                    }
                )

        # Process Pixeebot dashboard issues
        for issue in report.get("issues", []):
            if issue["author"][
                "login"
            ].lower() == "pixeebot" and "Dashboard" in issue.get("title", ""):
                task = Task(
                    task_type=TaskType.ANALYZE_PERFORMANCE,
                    input_data={
                        "action_type": GitHubActionType.ANALYZE_ISSUE.value,
                        "issue_number": issue["number"],
                    },
                    priority=TaskPriority.NORMAL,
                )

                result = await self.agent.process_task(task)
                results.append(
                    {
                        "issue_number": issue["number"],
                        "title": issue["title"],
                        "result": (
                            result.output_data
                            if result.success
                            else {"error": result.error_message}
                        ),
                    }
                )

        return results

    def _send_summary_notification(self, report: Dict, security_results: List[Dict]):
        """Send summary notification to Slack"""
        if not self.slack_notifier:
            return

        # Build message blocks
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🐙 GitHub Issues Report"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Repository*: `{report['repository']}`\n"
                    f"*Generated*: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📋 Open Issues*\n{report['summary']['open_issues']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🔄 Open PRs*\n{report['summary']['open_prs']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🔒 Security Items*\n{report['summary']['security_items']}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🤖 Active Bots*\n{', '.join(report['security_bots_active']) or 'None'}",
                    },
                ],
            },
        ]

        # Add security processing results
        if security_results:
            blocks.extend(
                [
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*🔒 Security Items Processed:*",
                        },
                    },
                ]
            )

            for item in security_results:
                if "pr_number" in item:
                    action = item["result"].get("action_taken", "reviewed")
                    emoji = "✅" if action == "auto_approved_and_merged" else "👀"
                    text = f"{emoji} PR  # {
                        item['pr_number']}: {
                        item['title']}\n   Action: {action}"
                else:
                    text = f"📊 Issue #{item['issue_number']}: {item['title']}"

                blocks.append(
                    {"type": "section", "text": {"type": "mrkdwn", "text": text}}
                )

        # Add recommendations
        blocks.extend(
            [
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💡 *Tip*: Use `@pixeebot next` in PR comments to see additional improvements",
                        }
                    ],
                },
            ]
        )

        self.slack_notifier.send_message(
            text = "GitHub Issues Report", blocks = blocks, color = "#3498db"
        )

    def _send_error_notification(self, error_type: str, details: str):
        """Send error notification to Slack"""
        if not self.slack_notifier:
            return

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "❌ GitHub Issues Error"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error*: {error_type}\n*Details*: {details}\n*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                },
            },
        ]

        self.slack_notifier.send_message(
            text = "GitHub Issues Error", blocks = blocks, color = "#e74c3c"
        )


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Issues Manager")
    parser.add_argument(
        "--repo",
        default = "IgorGanapolsky/ai-kindlemint-engine",
        help = "GitHub repository",
    )
    parser.add_argument(
        "--process-all", action = "store_true", help = "Process all open issues and PRs"
    )
    parser.add_argument("--review-pr", type=int,
                        help = "Review specific PR number")
    parser.add_argument(
        "--analyze-issue", type =int, help="Analyze specific issue number"
    )

    args = parser.parse_args()

    manager = GitHubIssuesManager(repo=args.repo)

    if args.process_all:
        print("🔍 Processing all GitHub issues and PRs...")
        result = await manager.process_all_issues()

        if result["success"]:
            report = result["report"]
            print(f"\n✅ Processed successfully!")
            print(f"   Open Issues: {report['summary']['open_issues']}")
            print(f"   Open PRs: {report['summary']['open_prs']}")
            print(f"   Security Items: {report['summary']['security_items']}")

            if result.get("security_results"):
                print(
                    f"\n🔒 Security items processed: {len(result['security_results'])}"
                )
        else:
            print(f"\n❌ Error: {result['error']}")

    elif args.review_pr:
        print(f"👀 Reviewing PR #{args.review_pr}...")
        task = Task(
            task_type=TaskType.ANALYZE_PERFORMANCE,
            input_data={
                "action_type": GitHubActionType.REVIEW_PR.value,
                "pr_number": args.review_pr,
            },
        )
        result = await manager.agent.process_task(task)

        if result.success:
            print("✅ PR reviewed successfully!")
        else:
            print(f"❌ Error: {result.error_message}")

    elif args.analyze_issue:
        print(f"🔍 Analyzing issue #{args.analyze_issue}...")
        task = Task(
            task_type=TaskType.ANALYZE_PERFORMANCE,
            input_data={
                "action_type": GitHubActionType.ANALYZE_ISSUE.value,
                "issue_number": args.analyze_issue,
            },
        )
        result = await manager.agent.process_task(task)

        if result.success:
            print("✅ Issue analyzed successfully!")
            print(f"Analysis: {result.output_data.get('analysis', '')}")
        else:
            print(f"❌ Error: {result.error_message}")

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
