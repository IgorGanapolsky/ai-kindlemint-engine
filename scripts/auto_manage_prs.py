#!/usr/bin/env python3
"""
Automated PR Management Script

Automatically reviews and handles pull requests using the GitHub Issues Agent.
Can process individual PRs or entire backlogs.
"""

import asyncio
import logging
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


async def auto_manage_pr(agent: GitHubIssuesAgent, pr_number: int) -> dict:
    """Automatically review and handle a single PR"""
    print(f"\n🔍 Processing PR #{pr_number}...")

    # Create review task
    task = Task(
        task_id=str(uuid.uuid4()),
        task_type="github_pr_review",
        parameters={
            "action_type": "review_pr",
            "pr_number": pr_number,
            "auto_approve": True,
        },
    )

    # Process the task
    result = await agent._process_task(task)

    if result and result.status == TaskStatus.COMPLETED:
        print(f"✅ PR #{pr_number}: Successfully reviewed")

        # For security and bot PRs, try auto-merge
        merge_task = Task(
            task_id=str(uuid.uuid4()),
            task_type="github_pr_merge",
            parameters={
                "action_type": "security_review",
                "pr_number": pr_number,
                "auto_approve": True,
            },
        )

        merge_result = await agent._process_task(merge_task)

        if merge_result and merge_result.status == TaskStatus.COMPLETED:
            action = merge_result.output.get("action_taken", "unknown")
            if action == "auto_approved_and_merged":
                print(f"🚀 PR #{pr_number}: Auto-merged!")
            else:
                print(f"📋 PR #{pr_number}: {action}")
    else:
        error_msg = result.error if result else "No result returned"
        print(f"❌ PR #{pr_number}: Review failed - {error_msg}")

    return result


async def process_pr_backlog(pr_numbers: list):
    """Process a backlog of PRs"""
    print("🤖 KindleMint PR Automation Starting...")
    print(f"📊 Processing {len(pr_numbers)} PRs: {pr_numbers}")

    # Initialize GitHub agent
    github_agent = GitHubIssuesAgent()
    await github_agent.start()

    results = {
        "processed": 0,
        "auto_merged": 0,
        "manual_review": 0,
        "failed": 0,
        "details": [],
    }

    try:
        for pr_num in pr_numbers:
            result = await auto_manage_pr(github_agent, pr_num)

            results["processed"] += 1

            if result and result.status == TaskStatus.COMPLETED:
                if (
                    hasattr(result, "output")
                    and result.output
                    and result.output.get("action_taken") == "auto_approved_and_merged"
                ):
                    results["auto_merged"] += 1
                else:
                    results["manual_review"] += 1
            else:
                results["failed"] += 1

            results["details"].append(
                {
                    "pr": pr_num,
                    "status": (
                        result.status.value
                        if result and hasattr(result, "status")
                        else "error"
                    ),
                    "output": (
                        result.output if result and hasattr(
                            result, "output") else None
                    ),
                }
            )

            # Small delay to avoid rate limiting
            await asyncio.sleep(2)

    finally:
        await github_agent.stop()

    # Print summary
    print("\n" + "=" * 50)
    print("📈 PR Management Summary:")
    print(f"   Total Processed: {results['processed']}")
    print(f"   ✅ Auto-merged: {results['auto_merged']}")
    print(f"   📋 Manual Review: {results['manual_review']}")
    print(f"   ❌ Failed: {results['failed']}")
    print("=" * 50)

    return results


async def main():
    """Main entry point"""
    # Default PR backlog from the user's screenshot
    default_prs = [76, 75, 74, 73, 72, 71, 70, 33]

    # Check if specific PRs were provided as arguments
    if len(sys.argv) > 1:
        pr_numbers = [int(pr) for pr in sys.argv[1:]]
    else:
        pr_numbers = default_prs

    await process_pr_backlog(pr_numbers)


if __name__ == "__main__":
    asyncio.run(main())
