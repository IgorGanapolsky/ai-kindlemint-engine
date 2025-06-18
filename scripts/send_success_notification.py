#!/usr/bin/env python3
"""
Send success notification after autonomous publishing
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

def send_slack_notification():
    """Send success notification to Slack"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ Slack webhook not configured")
        return
    
    # Get latest publishing report
    reports_dir = Path("output/publishing_reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob("publishing_report_*.json"))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            with open(latest_report, 'r') as f:
                report_data = json.load(f)
        else:
            report_data = {}
    else:
        report_data = {}
    
    # Create Slack message
    message = {
        "text": "🎉 KindleMint Autonomous Publishing Success!",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Autonomous Publishing Completed!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Series:* Large Print Crossword Masters"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Books Generated:* {report_data.get('books_generated', 'N/A')}/5"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Covers Created:* {report_data.get('covers_created', 'N/A')}/5"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*KDP Published:* {report_data.get('kdp_published', 'N/A')} volumes"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Drive Backup:* {'✅ Complete' if report_data.get('google_drive_uploaded') else '⚠️ Pending'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Completion:* {report_data.get('success_metrics', {}).get('completion_rate', 'N/A')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💰 *Business Impact:*\\n• Series Value: ${report_data.get('success_metrics', {}).get('total_estimated_value', 0):.2f}\\n• Generation Cost: {report_data.get('success_metrics', {}).get('generation_cost', 'N/A')}\\n• ROI Potential: {report_data.get('success_metrics', {}).get('roi_potential', 'N/A')}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | 🤖 KindleMint AI Publishing System"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            print("✅ Slack notification sent successfully")
        else:
            print(f"⚠️ Slack notification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Slack notification error: {e}")

def main():
    """Send success notifications"""
    print("📧 Sending success notifications...")
    
    send_slack_notification()
    
    # Could add more notification methods here:
    # - Email notifications
    # - Discord webhooks
    # - SMS alerts
    # - Dashboard updates
    
    print("✅ Notifications sent")

if __name__ == "__main__":
    main()