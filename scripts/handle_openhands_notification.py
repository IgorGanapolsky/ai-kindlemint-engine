#!/usr/bin/env python3
"""
OpenHands Notification Handler

Processes OpenHands AI notifications about CI/CD failures and repository issues.
Can be triggered by email webhooks, GitHub webhooks, or manual execution.
"""

import asyncio
import logging
import re
import sys
import uuid
from pathlib import Path

from src.kindlemint.agents.github_issues_agent import GitHubIssuesAgent
from src.kindlemint.agents.task_system import Task, TaskStatus

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def handle_openhands_notification(
    pr_number: int, notification_type: str = "ci_cd_failure"
):
    """Handle a specific OpenHands notification"""
    print(f"\n🤖 Processing OpenHands notification for PR #{pr_number}...")

    # Initialize GitHub agent
    github_agent = GitHubIssuesAgent()
    await github_agent.start()

    try:
        # Create OpenHands handling task
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type="handle_openhands",
            parameters={
                "action_type": "handle_openhands",
                "pr_number": pr_number,
                "notification_type": notification_type,
            },
        )

        # Process the task
        result = await github_agent._process_task(task)

        if result and result.status == TaskStatus.COMPLETED:
            output = result.output
            print(f"✅ OpenHands notification processed successfully!")
            print(f"   Failed Checks: {output.get('failed_checks', 0)}")
            print(
                f"   Critical Failures: {output.get('critical_failures', 0)}")
            print(
                f"   Actions Taken: {', '.join(output.get('actions_taken', []))}")

            return {"success": True, "pr_number": pr_number, "details": output}
        else:
            error_msg = result.error if result else "No result returned"
            print(f"❌ Failed to process OpenHands notification: {error_msg}")
            return {"success": False, "pr_number": pr_number, "error": error_msg}

    finally:
        await github_agent.stop()


async def parse_email_content(email_content: str):
    """Parse OpenHands email to extract PR number and details"""
    # Extract PR number from subject or content
    pr_match = re.search(r"PR #(\d+)", email_content)
    if not pr_match:
        pr_match = re.search(r"#(\d+)", email_content)

    if pr_match:
        pr_number = int(pr_match.group(1))
        return pr_number

    return None


async def main():
    """Main entry point"""
    print("=" * 60)
    print("KindleMint OpenHands Notification Handler")
    print("=" * 60)
    print()

    if len(sys.argv) == 2:
        # Handle specific PR
        try:
            pr_number = int(sys.argv[1])
            await handle_openhands_notification(pr_number)
        except ValueError:
            print("❌ Invalid PR number provided")
    else:
        print("Usage:")
        print("  python scripts/handle_openhands_notification.py <pr_number>")


if __name__ == "__main__":
    asyncio.run(main())
