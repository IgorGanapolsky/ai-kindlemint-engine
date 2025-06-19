#!/usr/bin/env python3
"""
Send failure notification if autonomous publishing fails
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

def send_failure_notification():
    """Send failure notification to Slack"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ Slack webhook not configured")
        return
    
    # Get error details if available
    error_details = "Check GitHub Actions logs for details"
    
    # Check for specific error files
    error_files = [
        "output/publishing_report.json",
        "output/drive_upload_summary.json",
        "logs/kindlemint.log"
    ]
    
    latest_errors = []
    for error_file in error_files:
        if Path(error_file).exists():
            try:
                with open(error_file, 'r') as f:
                    if error_file.endswith('.json'):
                        data = json.load(f)
                        if 'failed_volumes' in data and data['failed_volumes']:
                            latest_errors.append(f"Failed volumes: {data['failed_volumes']}")
                        if 'status' in data and data['status'] != 'completed':
                            latest_errors.append(f"Status: {data['status']}")
            except:
                pass
    
    if latest_errors:
        error_details = "\\n".join(latest_errors)
    
    # Create Slack message
    message = {
        "text": "❌ KindleMint Autonomous Publishing Failed!",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Autonomous Publishing Failed"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Series:* Large Print Crossword Masters\\n*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\\n*Error Details:*\\n{error_details}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔧 Troubleshooting Steps:*\\n• Check GitHub Actions logs\\n• Verify API credentials\\n• Check KDP login status\\n• Retry publishing process"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 KindleMint AI Publishing System - Failure Alert"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            print("✅ Failure notification sent successfully")
        else:
            print(f"⚠️ Failure notification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Failure notification error: {e}")

def main():
    """Send failure notifications"""
    print("🚨 Sending failure notifications...")
    
    send_failure_notification()
    
    print("✅ Failure notifications sent")

if __name__ == "__main__":
    main()