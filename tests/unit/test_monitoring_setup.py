#!/usr/bin/env python3
"""
Test monitoring setup for Slack and Sentry
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


    """Test Slack Notification"""
def test_slack_notification():
    """Test Slack webhook notification"""
    try:
        from scripts.slack_notifier import SlackNotifier

        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            print("❌ SLACK_WEBHOOK_URL not set in .env file")
            print(
                "   Please add: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
            )
            return False

        notifier = SlackNotifier(webhook_url)

        # Send test notification using the correct method
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🎉 KindleMint Monitoring Test"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Slack integration is working!*\n\n"
                    f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• System: AI-KindleMint-Engine\n"
                    f"• Environment: {os.getenv('ENVIRONMENT', 'development')}",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Monitored Events:*\n"
                    "• 📚 Book batch completions\n"
                    "• ❌ Quality validation failures\n"
                    "• 💰 Cost threshold alerts\n"
                    "• 📊 Daily/weekly reports\n"
                    "• 🚨 Critical errors\n"
                    "• 🤖 Agent task completions",
                },
            },
        ]

        success = notifier.send_message(
            text="KindleMint Monitoring Test", blocks=blocks, color="#2ecc71"
        )

        if success:
            print("✅ Slack test notification sent successfully!")
            return True
        else:
            print("❌ Failed to send Slack notification")
            return False

    except Exception as e:
        print(f"❌ Slack test failed: {e}")
        return False


    """Test Sentry Monitoring"""
def test_sentry_monitoring():
    """Test Sentry error tracking"""
    try:
        import sentry_sdk

        from scripts.sentry_config import add_breadcrumb, capture_kdp_error, init_sentry

        sentry_dsn = os.getenv("SENTRY_DSN")
        if not sentry_dsn:
            print("❌ SENTRY_DSN not set in .env file")
            print("   Please add: SENTRY_DSN=https://your-key@sentry.io/project-id")
            return False

        # Initialize Sentry
        init_sentry("monitoring-test")

        # Test error capture
        try:
            # Create a test error
            raise ValueError("Test error from KindleMint monitoring setup")
        except Exception as e:
            # Capture with context (correct signature - only error and context)
            capture_kdp_error(
                e,
                context={
                    "operation": "monitoring_test",
                    "test_type": "setup_verification",
                    "timestamp": datetime.now().isoformat(),
                    "environment": os.getenv("ENVIRONMENT", "development"),
                },
            )

        # Test breadcrumb
        add_breadcrumb(
            message="Test breadcrumb from monitoring setup",
            category="monitoring",
            level="info",
            data={"test": True},
        )

        # Test transaction
        with sentry_sdk.start_transaction(op="test", name="monitoring_test"):
            sentry_sdk.set_tag("test.type", "monitoring_setup")

        print("✅ Sentry test error sent successfully!")
        print("   Check your Sentry dashboard for the test error")
        return True

    except Exception as e:
        print(f"❌ Sentry test failed: {e}")
        return False


    """Test Github Integration"""
def test_github_integration():
    """Test GitHub CLI integration"""
    try:
        import subprocess

        # Test gh CLI
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ GitHub CLI authenticated successfully!")
            print(f"   {result.stdout.strip()}")
            return True
        else:
            print("❌ GitHub CLI not authenticated")
            print("   Run: gh auth login")
            return False

    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not installed")
        print("   Install with: brew install gh")
        return False
    except Exception as e:
        print(f"❌ GitHub test failed: {e}")
        return False


    """Main"""
def main():
    """Run all monitoring tests"""
    print("🔍 Testing KindleMint Monitoring Setup")
    print("=" * 50)

    results = {"slack": False, "sentry": False, "github": False}

    # Test Slack
    print("\n📢 Testing Slack Integration...")
    results["slack"] = test_slack_notification()

    # Test Sentry
    print("\n🐛 Testing Sentry Integration...")
    results["sentry"] = test_sentry_monitoring()

    # Test GitHub
    print("\n🐙 Testing GitHub Integration...")
    results["github"] = test_github_integration()

    # Summary
    print("\n" + "=" * 50)
    print("📊 MONITORING SETUP SUMMARY")
    print("=" * 50)

    all_passed = all(results.values())

    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(
            f"{icon} {service.capitalize()}: {'Working' if status else 'Not configured'}"
        )

    if all_passed:
        print("\n🎉 All monitoring services are configured and working!")
    else:
        print("\n⚠️  Some services need configuration. Check the messages above.")

    # Send summary to Slack if it's working
    if results["slack"]:
        try:
            from scripts.slack_notifier import SlackNotifier

            notifier = SlackNotifier(os.getenv("SLACK_WEBHOOK_URL"))

            summary_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Monitoring Setup Summary",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• Slack: {'✅ Working' if results['slack'] else '❌ Not configured'}\n"
                        f"• Sentry: {'✅ Working' if results['sentry'] else '❌ Not configured'}\n"
                        f"• GitHub: {'✅ Working' if results['github'] else '❌ Not configured'}",
                    },
                },
            ]

            notifier.send_message(
                text="Monitoring Setup Summary", blocks=summary_blocks, color="#3498db"
            )
        except Exception:
            pass

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
