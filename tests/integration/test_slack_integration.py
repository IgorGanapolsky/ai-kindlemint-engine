#!/usr/bin/env python3
import pytest

pytest.skip("Skipping Slack integration tests in CI", allow_module_level=True)
"""
Test script for Slack integration in batch processor
"""

import os
import sys
from datetime import datetime

# Add scripts directory to path for imports
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

from slack_notifier import SlackNotifier


def test_slack_integration():
    """Test Slack Integration"""
    """Test various Slack notification methods"""
    print("🧪 Testing Slack Integration for Batch Processor")
    print("=" * 50)

    # Initialize notifier
    notifier = SlackNotifier()

    if not notifier.enabled:
        print("⚠️  Slack notifications are disabled")
        print("   Set SLACK_WEBHOOK_URL environment variable to enable")
        print("\n   Example:")
        print(
            "   export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'"
        )
        return False

    print("✅ Slack notifier initialized")
    print(f"   Webhook URL: {notifier.webhook_url[:30]}...")

    # Test 1: Simple message
    print("\n1. Testing simple message...")
    success = notifier.send_message(
        "🧪 Test message from KindleMint Engine Slack integration", color="#3498db"
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Test 2: Batch completion notification
    print("\n2. Testing batch completion notification...")
    test_batch_results = {
        "batch_id": "test_20240101_120000",
        "books_processed": 5,
        "books_succeeded": 4,
        "books_failed": 1,
        "total_time_seconds": 1234,
        "book_results": {
            "book_1": {"title": "Test Book 1", "status": "complete"},
            "book_2": {"title": "Test Book 2", "status": "complete"},
            "book_3": {"title": "Test Book 3", "status": "complete"},
            "book_4": {"title": "Test Book 4", "status": "complete"},
            "book_5": {
                "title": "Test Book 5",
                "status": "failed",
                "error": "Test error: Unable to generate puzzles",
            },
        },
    }
    success = notifier.send_batch_complete(test_batch_results)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Test 3: Error notification
    print("\n3. Testing error notification...")
    try:
        raise ValueError("Test exception for Slack integration")
    except Exception as e:
        success = notifier.send_error(
            message="Test error from batch processor",
            error=e,
            context={
                "book_id": "test_book",
                "batch_id": "test_batch",
                "step": "test_step",
            },
        )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    # Test 4: Book completion notification
    print("\n4. Testing book completion notification...")
    test_book_result = {
        "id": "test_book_123",
        "title": "Large Print Crossword Masters Vol. 1",
        "status": "complete",
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "steps_completed": [
            "generate_puzzles",
            "create_pdf",
            "create_epub",
            "create_hardcover",
            "run_qa",
        ],
        "artifacts": {
            "pdf_dir": "/path/to/pdf",
            "epub_file": "/path/to/epub",
            "hardcover_dir": "/path/to/hardcover",
        },
    }
    success = notifier.send_book_complete(test_book_result)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    print("\n" + "=" * 50)
    print("✅ Slack integration test complete!")
    print("\n📝 Configuration notes:")
    print("   - Batch completion notifications: Always enabled")
    print("   - Critical error notifications: Always enabled")
    print(
        "   - Individual book notifications: Set SLACK_NOTIFY_PER_BOOK=true to enable"
    )

    return True


if __name__ == "__main__":
    test_slack_integration()
