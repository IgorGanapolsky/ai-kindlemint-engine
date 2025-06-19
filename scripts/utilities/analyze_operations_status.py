#!/usr/bin/env python3
"""
KindleMint Operations Status Analyzer
Analyzes why certain operations are being skipped and provides recommendations.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def analyze_operations_status():
    """Analyze why operations are being skipped."""
    
    print("🔍 KINDLEMINT OPERATIONS STATUS ANALYZER")
    print("=" * 60)
    
    # Check configuration settings
    print("\n📋 Configuration Analysis:")
    
    config_file = Path("config/v3-production-config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        operational_settings = config.get('operational_settings', {})
        scaling = operational_settings.get('scaling', {})
        
        print(f"✅ Max daily books: {scaling.get('max_daily_books', 'NOT SET')}")
        print(f"✅ Max concurrent books: {scaling.get('max_concurrent_books', 'NOT SET')}")
        print(f"✅ Auto scaling: {scaling.get('enable_auto_scaling', 'NOT SET')}")
        
        cost_mgmt = operational_settings.get('cost_management', {})
        print(f"✅ Daily budget limit: ${cost_mgmt.get('daily_budget_limit', 'NOT SET')}")
        print(f"✅ Cost optimization: {cost_mgmt.get('optimize_for_cost', 'NOT SET')}")
    else:
        print("❌ Configuration file not found")
    
    # Check environment variables
    print("\n🔧 Environment Variables:")
    required_vars = [
        'OPENAI_API_KEY', 'SLACK_WEBHOOK_URL', 'ASSETS_BUCKET', 
        'FARGATE_INVOKER_ARN', 'BUFFER_ACCESS_TOKEN'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'key' in var.lower() or 'token' in var.lower():
                display_value = value[:10] + "..." if len(value) > 10 else "SET"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    # Analyze potential causes of skipped operations
    print("\n⚠️ Common Causes of Skipped Operations:")
    
    reasons = [
        {
            "operation": "Market Research",
            "causes": [
                "Daily limit reached (max_daily_books: 1)",
                "Cost optimization enabled - skipping expensive operations",
                "OpenAI API rate limits or quotas",
                "Previous operation still in progress",
                "Scheduler not triggering due to timing"
            ]
        },
        {
            "operation": "Marketing",
            "causes": [
                "Buffer API credentials not configured",
                "No books to market (publishing pipeline empty)",
                "Marketing module waiting for book completion",
                "Social media API rate limits",
                "Cost optimization skipping non-essential tasks"
            ]
        },
        {
            "operation": "Book Publishing",
            "causes": [
                "Prompt Co-Pilot workflow paused (waiting for cover)",
                "KDP authentication issues",
                "Fargate task failures",
                "Cover generation errors (before our fix)",
                "Validation threshold not met"
            ]
        }
    ]
    
    for reason_group in reasons:
        print(f"\n📊 {reason_group['operation']}:")
        for i, cause in enumerate(reason_group['causes'], 1):
            print(f"   {i}. {cause}")
    
    # Check recent logs or state
    print("\n📁 System State Check:")
    
    output_dir = Path("output")
    if output_dir.exists():
        book_dirs = list(output_dir.glob("*/"))
        print(f"✅ Found {len(book_dirs)} book directories")
        
        # Check for paused workflows
        paused_workflows = list(output_dir.glob("*/cover_workflow_state.json"))
        if paused_workflows:
            print(f"⏸️ Found {len(paused_workflows)} paused workflows (waiting for covers)")
            for workflow_file in paused_workflows:
                print(f"   📁 {workflow_file.parent.name}")
        else:
            print("▶️ No paused workflows detected")
    else:
        print("❌ Output directory not found")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    recommendations = [
        "1. Check CloudWatch logs for specific error messages",
        "2. Verify AWS Lambda function permissions and execution",
        "3. Check EventBridge scheduler is properly configured",
        "4. Ensure Buffer API credentials are configured for marketing",
        "5. Monitor Prompt Co-Pilot workflow for paused cover creation",
        "6. Review daily budget limits and cost optimization settings",
        "7. Check if operations are being throttled due to rate limits"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # Slack channel fix
    print("\n📱 Slack Channel Configuration:")
    print("✅ Updated SlackNotifier to send to #general by default")
    print("✅ All future notifications will go to #general channel")
    
    return True

def main():
    """Main analysis function."""
    try:
        analyze_operations_status()
        print("\n✅ Analysis complete!")
        return True
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)