#!/usr/bin/env python3
import pytest

pytest.skip("Skipping real API connection tests in CI", allow_module_level=True)
"""
Test Real API Connections
Validates that all API keys work and return real data
Updated: 2025-06-24 - Testing workflow triggers
"""

import os
import json
import requests
import praw
from serpapi.google_search import GoogleSearch
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_serpapi():
    """Test SerpApi connection and functionality"""
    print("🔍 Testing SerpApi...")

    serpapi_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        print("❌ SERPAPI_API_KEY not found in environment")
        return False

    try:
        # Test Amazon search
        search_params = {
            "engine": "amazon",
            "amazon_domain": "amazon.com",
            "k": "crossword puzzle books",
            "api_key": serpapi_key,
        }

        search = GoogleSearch(search_params)
        results = search.get_dict()

        if "organic_results" in results:
            product_count = len(results["organic_results"])
            print(f"✅ SerpApi working - found {product_count} Amazon products")

            # Show sample product
            if product_count > 0:
                sample = results["organic_results"][0]
                print(f"   Sample: {sample.get('title', 'No title')[:50]}...")
                print(f"   Price: {sample.get('price', 'N/A')}")
                print(f"   Reviews: {sample.get('reviews_count', 'N/A')}")

            return True
        else:
            print("❌ SerpApi returned no organic results")
            print(f"   Response keys: {list(results.keys())}")
            if "error" in results:
                print(f"   Error: {results['error']}")
            return False

    except Exception as e:
        print(f"❌ SerpApi error: {e}")
        return False


def test_reddit_api():
    """Test Reddit API connection"""
    print("🗨️ Testing Reddit API...")

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        print("❌ Reddit API credentials missing")
        print(f"   CLIENT_ID: {'✅' if client_id else '❌'}")
        print(f"   CLIENT_SECRET: {'✅' if client_secret else '❌'}")
        print(f"   USER_AGENT: {'✅' if user_agent else '❌'}")
        return False

    try:
        reddit = praw.Reddit(
            client_id=client_id, client_secret=client_secret, user_agent=user_agent
        )

        # Test access to a subreddit
        subreddit = reddit.subreddit("crossword")
        subscribers = subreddit.subscribers

        print(f"✅ Reddit API working - r/crossword has {subscribers:,} subscribers")

        # Get a few hot posts
        hot_posts = list(subreddit.hot(limit=3))
        print(f"   Found {len(hot_posts)} hot posts")

        for post in hot_posts:
            print(f"   - {post.title[:50]}... ({post.score} upvotes)")

        return True

    except Exception as e:
        print(f"❌ Reddit API error: {e}")
        return False


def test_google_trends_via_serpapi():
    """Test Google Trends via SerpApi"""
    print("📈 Testing Google Trends via SerpApi...")

    serpapi_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        print("❌ SERPAPI_API_KEY not found for Google Trends")
        return False

    try:
        search_params = {
            "engine": "google_trends",
            "q": "crossword books",
            "date": "today 3-m",  # Last 3 months
            "api_key": serpapi_key,
        }

        search = GoogleSearch(search_params)
        trends_results = search.get_dict()

        if "interest_over_time" in trends_results:
            timeline_data = trends_results["interest_over_time"].get(
                "timeline_data", []
            )
            print(f"✅ Google Trends working - found {len(timeline_data)} data points")

            if timeline_data:
                recent_value = timeline_data[-1].get("value", 0)
                print(f"   Latest interest score: {recent_value}")

                # Calculate average
                values = [point.get("value", 0) for point in timeline_data]
                avg_interest = sum(values) / len(values) if values else 0
                print(f"   Average interest (3 months): {avg_interest:.1f}")

            return True
        else:
            print("❌ Google Trends returned no timeline data")
            print(f"   Response keys: {list(trends_results.keys())}")
            return False

    except Exception as e:
        print(f"❌ Google Trends error: {e}")
        return False


def test_slack_webhook():
    """Test Slack webhook"""
    print("📧 Testing Slack webhook...")

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL not found")
        return False

    try:
        test_message = {
            "text": "🧪 API Test Complete",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🧪 Real API Test Results"},
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f'All APIs tested successfully at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    },
                },
            ],
        }

        response = requests.post(webhook_url, json=test_message, timeout=30)

        if response.status_code == 200:
            print("✅ Slack webhook working - test message sent")
            return True
        else:
            print(f"❌ Slack webhook failed - status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Slack webhook error: {e}")
        return False


def main():
    """Run all API tests"""
    print("🧪 REAL API CONNECTION TESTS")
    print("=" * 50)

    test_results = {
        "serpapi": test_serpapi(),
        "reddit": test_reddit_api(),
        "google_trends": test_google_trends_via_serpapi(),
        "slack": test_slack_webhook(),
    }

    print("\n📊 TEST SUMMARY:")
    print("=" * 30)

    for api, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{api.upper()}: {status}")

    total_passed = sum(test_results.values())
    total_tests = len(test_results)

    print(f"\n🎯 OVERALL: {total_passed}/{total_tests} APIs working")

    if total_passed == total_tests:
        print("🎉 All APIs ready for real market research!")
    else:
        print("⚠️ Some APIs need configuration before running real workflows")

    # Save test results
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "results": test_results,
        "summary": {
            "passed": total_passed,
            "total": total_tests,
            "success_rate": f"{(total_passed/total_tests)*100:.1f}%",
        },
    }

    os.makedirs("research/api_tests", exist_ok=True)
    with open(
        f'research/api_tests/api_test_{datetime.now().strftime("%Y%m%d_%H%M")}.json',
        "w",
    ) as f:
        json.dump(test_report, f, indent=2)

    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
