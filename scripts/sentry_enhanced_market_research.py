#!/usr/bin/env python3
"""
Sentry-Enhanced Market Research - Zero-Touch Debugging
"""

import json
import os
from datetime import datetime

import requests
from sentry_config import (
    SentryKDPOperation,
    add_breadcrumb,
    capture_kdp_error,
    init_sentry,
)


def run_sentry_enhanced_research():
    """Market research with Seer AI monitoring"""

    # Initialize Sentry + Seer AI
    if not init_sentry("market-research-engine"):
        print("⚠️ Running without Sentry monitoring")

    add_breadcrumb("Starting market research automation", category="automation")

    with SentryKDPOperation("market_research_full_cycle") as transaction:

        results = {
            "timestamp": datetime.now().isoformat(),
            "sentry_enabled": True,
            "operations_tracked": [],
            "apis_tested": [],
        }

        # AMAZON KDP ANALYSIS with Seer AI monitoring
        with SentryKDPOperation(
            "amazon_competitor_analysis", {"api": "serpapi"}
        ) as sub_transaction:
            try:
                add_breadcrumb("Initializing SerpApi connection", category="api")

                serpapi_key = os.getenv("SERPAPI_API_KEY")
                if not serpapi_key:
                    raise ValueError("SERPAPI_API_KEY not found in environment")

                add_breadcrumb("SerpApi key validated", category="api")

                # Amazon search with error tracking
                params = {
                    "engine": "amazon",
                    "amazon_domain": "amazon.com",
                    "k": "crossword puzzle books",
                    "api_key": serpapi_key,
                }

                add_breadcrumb(
                    "Making SerpApi request", category="api", data={"params": params}
                )

                response = requests.get(
                    "https://serpapi.com/search", params=params, timeout=30
                )

                if response.status_code != 200:
                    raise requests.HTTPError(
                        f"SerpApi returned {response.status_code}: {response.text}"
                    )

                data = response.json()

                if "organic_results" not in data:
                    raise ValueError(
                        f"No organic_results in SerpApi response: {list(data.keys())}"
                    )

                # Success tracking
                product_count = len(data["organic_results"])
                results["amazon_products"] = product_count
                results["apis_tested"].append("SerpApi - SUCCESS")
                results["operations_tracked"].append("amazon_competitor_analysis")

                add_breadcrumb(
                    f"SerpApi success: {product_count} products found",
                    category="api",
                    data={"product_count": product_count},
                )

                print(f"✅ SerpApi: Found {product_count} products")

                # Extract key competitor insights for Seer AI
                if product_count > 0:
                    top_competitor = data["organic_results"][0]
                    add_breadcrumb(
                        "Top competitor analyzed",
                        category="business_intelligence",
                        data={
                            "title": top_competitor.get("title", "Unknown")[:50]
                            + "...",
                            "price": top_competitor.get("price", "N/A"),
                            "rating": top_competitor.get("rating", "N/A"),
                        },
                    )

            except requests.RequestException as e:
                capture_kdp_error(
                    e,
                    {
                        "operation": "amazon_competitor_analysis",
                        "api": "serpapi",
                        "error_category": "api_request_failure",
                    },
                )
                results["apis_tested"].append(f"SerpApi - REQUEST_ERROR: {str(e)}")
                print(f"❌ SerpApi request error: {e}")

            except ValueError as e:
                capture_kdp_error(
                    e,
                    {
                        "operation": "amazon_competitor_analysis",
                        "api": "serpapi",
                        "error_category": "data_validation_failure",
                    },
                )
                results["apis_tested"].append(f"SerpApi - DATA_ERROR: {str(e)}")
                print(f"❌ SerpApi data error: {e}")

            except Exception as e:
                capture_kdp_error(
                    e,
                    {
                        "operation": "amazon_competitor_analysis",
                        "api": "serpapi",
                        "error_category": "unexpected_failure",
                    },
                )
                results["apis_tested"].append(f"SerpApi - UNEXPECTED_ERROR: {str(e)}")
                print(f"❌ SerpApi unexpected error: {e}")

        # SLACK INTEGRATION with Seer AI monitoring
        with SentryKDPOperation(
            "slack_notification", {"integration": "webhook"}
        ) as sub_transaction:
            try:
                add_breadcrumb(
                    "Initializing Slack notification", category="notification"
                )

                webhook_url = os.getenv("SLACK_WEBHOOK_URL")
                if not webhook_url:
                    raise ValueError("SLACK_WEBHOOK_URL not found in environment")

                # Prepare Seer AI-enhanced notification
                api_count = len(
                    [api for api in results["apis_tested"] if "SUCCESS" in api]
                )

                message = {
                    "text": f"🔍 Sentry-Enhanced Market Research Complete!",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "🎯 Seer AI Market Intelligence",
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*APIs Working:* {api_count}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Products Found:* {results.get("amazon_products", 0)}',
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Sentry Tracking:* ✅ Active",
                                },
                                {"type": "mrkdwn", "text": f"*Seer AI:* ✅ Monitoring"},
                            ],
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f'🤖 Zero-Touch Debugging Active - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                                }
                            ],
                        },
                    ],
                }

                add_breadcrumb(
                    "Sending Slack notification",
                    category="notification",
                    data={"message_blocks": len(message["blocks"])},
                )

                response = requests.post(webhook_url, json=message, timeout=10)

                if response.status_code != 200:
                    raise requests.HTTPError(
                        f"Slack webhook returned {
                            response.status_code}: {
                            response.text}"
                    )

                results["apis_tested"].append("Slack - SUCCESS")
                results["operations_tracked"].append("slack_notification")

                add_breadcrumb(
                    "Slack notification sent successfully", category="notification"
                )
                print("✅ Slack: Sentry-enhanced notification sent")

            except requests.RequestException as e:
                capture_kdp_error(
                    e,
                    {
                        "operation": "slack_notification",
                        "integration": "webhook",
                        "error_category": "notification_failure",
                    },
                )
                results["apis_tested"].append(f"Slack - REQUEST_ERROR: {str(e)}")
                print(f"❌ Slack request error: {e}")

            except ValueError as e:
                capture_kdp_error(
                    e,
                    {
                        "operation": "slack_notification",
                        "integration": "webhook",
                        "error_category": "configuration_failure",
                    },
                )
                results["apis_tested"].append(f"Slack - CONFIG_ERROR: {str(e)}")
                print(f"❌ Slack config error: {e}")

            except Exception as e:
                capture_kdp_error(
                    e,
                    {
                        "operation": "slack_notification",
                        "integration": "webhook",
                        "error_category": "unexpected_failure",
                    },
                )
                results["apis_tested"].append(f"Slack - UNEXPECTED_ERROR: {str(e)}")
                print(f"❌ Slack unexpected error: {e}")

        # SAVE RESULTS with Seer AI context
        try:
            os.makedirs("research/sentry_enhanced", exist_ok=True)
            filename = f'research/sentry_enhanced/sentry_research_{
                datetime.now().strftime("%Y_%m_%d_%H%M")}.json'

            with open(filename, "w") as f:
                json.dump(results, f, indent=2)

            add_breadcrumb(
                "Research results saved",
                category="file_operation",
                data={"filename": filename, "api_count": len(results["apis_tested"])},
            )

            print(f"\n📊 SENTRY-ENHANCED SUMMARY:")
            print(f"✅ APIs tested: {len(results['apis_tested'])}")
            print(f"🔍 Operations tracked: {len(results['operations_tracked'])}")
            for api_result in results["apis_tested"]:
                print(f"   {api_result}")
            print(f"📁 Results saved: {filename}")
            print(f"🤖 Seer AI: Monitoring for automated fixes")

            # Final success breadcrumb
            add_breadcrumb(
                "Market research completed successfully",
                category="automation",
                data={"total_operations": len(results["operations_tracked"])},
            )

        except Exception as e:
            capture_kdp_error(
                e,
                {
                    "operation": "save_results",
                    "error_category": "file_operation_failure",
                },
            )
            print(f"❌ Failed to save results: {e}")

    return results


if __name__ == "__main__":
    run_sentry_enhanced_research()
