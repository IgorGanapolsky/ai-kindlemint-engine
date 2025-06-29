#!/usr/bin/env python3
"""
Simple Market Research Script - Actually Works
"""

import json
import os
from datetime import datetime

import requests


def run_simple_research():
    """Run simple market research that actually works"""
    print("🔍 Simple Market Research - Real APIs")
    print("=" * 50)

    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "apis_tested": [],
    }

    # Test SerpApi
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if serpapi_key:
        try:
            # Simple Amazon search
            params = {
                "engine": "amazon",
                "amazon_domain": "amazon.com",
                "k": "crossword puzzle books",
                "api_key": serpapi_key,
            }

            response = requests.get(
                "https://serpapi.com/search", params=params, timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if "organic_results" in data:
                    results["amazon_products"] = len(data["organic_results"])
                    results["apis_tested"].append("SerpApi - SUCCESS")
                    print(f"✅ SerpApi: Found {len(data['organic_results'])} products")
                else:
                    results["apis_tested"].append("SerpApi - No results")
                    print("⚠️ SerpApi: No organic results")
            else:
                results["apis_tested"].append(f"SerpApi - HTTP {response.status_code}")
                print(f"⚠️ SerpApi: HTTP {response.status_code}")

        except Exception as e:
            results["apis_tested"].append(f"SerpApi - ERROR: {str(e)}")
            print(f"❌ SerpApi error: {e}")
    else:
        results["apis_tested"].append("SerpApi - No API key")
        print("⚠️ No SerpApi key found")

    # Test Slack webhook
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if webhook_url:
        try:
            message = {
                "text": f'✅ Simple Market Research Test - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            }
            response = requests.post(webhook_url, json=message, timeout=30)
            if response.status_code == 200:
                results["apis_tested"].append("Slack - SUCCESS")
                print("✅ Slack: Notification sent")
            else:
                results["apis_tested"].append(f"Slack - HTTP {response.status_code}")
                print(f"⚠️ Slack: HTTP {response.status_code}")
        except Exception as e:
            results["apis_tested"].append(f"Slack - ERROR: {str(e)}")
            print(f"❌ Slack error: {e}")
    else:
        results["apis_tested"].append("Slack - No webhook URL")
        print("⚠️ No Slack webhook found")

    # Save results
    os.makedirs("research/simple_tests", exist_ok=True)
    filename = f'research/simple_tests/simple_test_{datetime.now().strftime("%Y_%m_%d_%H%M")}.json'

    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 SUMMARY:")
    print(f"✅ APIs tested: {len(results['apis_tested'])}")
    for api_result in results["apis_tested"]:
        print(f"   {api_result}")
    print(f"📁 Results saved: {filename}")

    return results


if __name__ == "__main__":
    run_simple_research()
