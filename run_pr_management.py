#!/usr/bin/env python3
"""
Run PR Management Workflow

This script triggers the PR management workflow through the automation coordinator.
It can be run manually or scheduled via cron/systemd.
"""

import asyncio
import sys
import uuid
from pathlib import Path

from src.kindlemint.agents.automation_coordinator import AutomationCoordinator
from src.kindlemint.agents.task_system import Task

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def trigger_pr_management():
    """Trigger PR management through the automation coordinator"""
    print("🤖 Initiating PR Management Workflow...")

    # Initialize the coordinator
    coordinator = AutomationCoordinator()
    await coordinator.start()

    try:
        # Create a PR management task
        pr_task = Task(
            task_id=str(uuid.uuid4()),
            task_type="manage_pull_requests",
            parameters={"type": "manage_pull_requests",
                        "scope": "all_open_prs"},
        )

        # Execute the task
        result = await coordinator._process_task(pr_task)

        if result.status.value == "completed":
            print("✅ PR Management workflow completed successfully!")
            print(
                f"📁 Results saved to: {result.output.get('results_file', 'N/A')}")
        else:
            print(f"❌ PR Management workflow failed: {result.error}")

    finally:
        await coordinator.stop()


async def main():
    """Main entry point"""
    print("=" * 60)
    print("KindleMint PR Management System")
    print("=" * 60)
    print()
    print("This system automatically:")
    print("✓ Reviews all open pull requests")
    print("✓ Auto-approves security bot PRs")
    print("✓ Merges approved PRs when possible")
    print("✓ Provides AI-powered code reviews")
    print()

    await trigger_pr_management()

    print()
    print("💡 Tip: Add this to your daily orchestration workflows!")
    print("   The system runs PR management daily at 9 AM automatically.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
