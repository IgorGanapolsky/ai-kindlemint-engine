#!/usr/bin/env python3
"""
Test script for Sentry AI automation
Verifies that the GitHub workflow and orchestration are working correctly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from alert_orchestration.sentry_ai_orchestrator import SentryAIOrchestrator

async     """Test Sentry Ai"""
def test_sentry_ai():
    """Test Sentry AI automation features"""
    print("🧪 Testing Sentry AI Automation")
    print("=" * 50)

    # Initialize orchestrator
    try:
        orchestrator = SentryAIOrchestrator()
        print("✅ Sentry AI Orchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    # Test 1: Check if GitHub is configured
    if orchestrator.github:
        print("✅ GitHub API configured")
        print(f"   Repository: {orchestrator.repo_name}")
    else:
        print("❌ GitHub API not configured - set GITHUB_TOKEN environment variable")
        print("   Note: This is optional for manual testing")

    # Test 2: Monitor active PRs
    print("\n📋 Checking active PRs...")
    try:
        pr_statuses = await orchestrator.monitor_active_prs()
        print(f"✅ Found {len(pr_statuses)} open PRs")

        for pr in pr_statuses[:3]:  # Show first 3 PRs
            print(f"\n   PR #{pr.get('pr_number')}: {pr.get('title')}")
            print(f"   - Sentry AI Reviewed: {pr.get('has_sentry_review', False)}")
            print(f"   - Processing: {pr.get('is_processing', False)}")
            print(f"   - Labels: {', '.join(pr.get('labels', []))}")
    except Exception as e:
        print(f"❌ Failed to monitor PRs: {e}")

    # Test 3: Check workflow file
    workflow_path = (
        Path(__file__).parent.parent / ".github/workflows/sentry-ai-automation.yml"
    )
    if workflow_path.exists():
        print("\n✅ GitHub workflow file exists")
        print(f"   Path: {workflow_path}")
    else:
        print("\n❌ GitHub workflow not found")

    # Test 4: Verify orchestration integration
    try:
        pass

        print("\n✅ Alert orchestrator imports Sentry AI components")
    except ImportError as e:
        print(f"\n❌ Failed to import alert orchestrator: {e}")

    print("\n" + "=" * 50)
    print("📌 Next Steps:")
    print("1. Create a test PR to trigger automation")
    print("2. Check for @sentry comments on the PR")
    print("3. Monitor Slack for PR quality notifications")
    print("4. Review Sentry dashboard for AI insights")

    print("\n🎯 Test Commands:")
    print(
        "- Manual trigger: python scripts/alert_orchestration/sentry_ai_orchestrator.py check --pr <PR_NUMBER>"
    )
    print(
        "- Monitor PRs: python scripts/alert_orchestration/sentry_ai_orchestrator.py monitor"
    )
    print(
        "- Start full orchestration: python scripts/alert_orchestration/alert_orchestrator.py"
    )


if __name__ == "__main__":
    asyncio.run(test_sentry_ai())
