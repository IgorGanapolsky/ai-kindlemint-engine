#!/usr/bin/env python3
"""
Context-Aware Success Notification System
Sends rich, actionable success alerts to Slack with business metrics
"""
import sys
import os
import argparse
import requests
import json
from datetime import datetime
from pathlib import Path

def send_success_notification(args):
    """Send detailed success notification to Slack."""
    
    # Get Slack webhook from environment
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("❌ No SLACK_WEBHOOK_URL environment variable found")
        return False
    
    # Truncate commit SHA for readability
    short_commit = args.commit[:7] if args.commit else "unknown"
    
    # Truncate commit message if too long
    commit_msg = args.commit_msg or "No commit message"
    if len(commit_msg) > 50:
        commit_msg = commit_msg[:47] + "..."
    
    # Get latest publishing report for business metrics
    reports_dir = Path("output/publishing_reports")
    report_data = {}
    if reports_dir.exists():
        report_files = list(reports_dir.glob("publishing_report_*.json"))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_report, 'r') as f:
                    report_data = json.load(f)
            except:
                pass
    
    # Build rich Slack message
    slack_message = {
        "text": f"✅ SUCCESS: {args.workflow}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ SUCCESS: {args.workflow}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Commit:* `{short_commit}` - {commit_msg}"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Triggered by:* {args.triggered_by}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Branch:* {args.branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Volumes:* {args.volumes}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Books Published:* {report_data.get('kdp_published', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.now().strftime('%I:%M %p UTC')}"
                    }
                ]
            }
        ]
    }
    
    # Add business metrics if available
    if report_data:
        business_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"💰 *Business Impact:*\n• Series Value: ${report_data.get('success_metrics', {}).get('total_estimated_value', 0):.2f}\n• Books Generated: {report_data.get('books_generated', 'N/A')}/5\n• Drive Backup: {'✅ Complete' if report_data.get('google_drive_uploaded') else '⚠️ Pending'}"
            }
        }
        slack_message["blocks"].append(business_section)
    
    # Add action button to view run
    action_section = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📊 View Run Details"
                },
                "url": args.run_url,
                "style": "primary"
            }
        ]
    }
    slack_message["blocks"].append(action_section)
    
    # Add debug info
    debug_section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Debug Info:* Run ID `{args.run_id}` | <{args.run_url}|Direct Link to Success>"
        }
    }
    slack_message["blocks"].append(debug_section)
    
    try:
        response = requests.post(webhook_url, json=slack_message, timeout=10)
        response.raise_for_status()
        print(f"✅ Success notification sent to Slack successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Send context-aware success notification')
    parser.add_argument('--workflow', required=True, help='Workflow name')
    parser.add_argument('--run-id', required=True, help='GitHub run ID')
    parser.add_argument('--run-url', required=True, help='Direct URL to GitHub run')
    parser.add_argument('--commit', required=True, help='Commit SHA')
    parser.add_argument('--commit-msg', help='Commit message')
    parser.add_argument('--triggered-by', required=True, help='User who triggered the workflow')
    parser.add_argument('--branch', required=True, help='Git branch')
    parser.add_argument('--volumes', help='Volumes being published')
    
    args = parser.parse_args()
    
    print(f"📧 Sending success notification for: {args.workflow}")
    success = send_success_notification(args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()