#!/usr/bin/env python3
"""
Lambda Deployment Notification System
Only sends notifications for critical Lambda deployment failures
"""
import sys
import os
import argparse
import requests
import json
from datetime import datetime

def send_lambda_notification(args):
    """Send critical Lambda deployment failure notification to Slack."""
    
    # Get Slack webhook from environment
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("❌ No SLACK_WEBHOOK_URL environment variable found")
        return False
    
    # Only send notifications for failures - successes are noise
    if args.status != "FAILED":
        print("✅ Lambda deployment succeeded - no notification needed")
        return True
    
    # Truncate commit SHA for readability
    short_commit = args.commit[:7] if args.commit else "unknown"
    
    # Handle commit message
    if args.commit_msg and args.commit_msg.strip():
        commit_msg = args.commit_msg.strip()
        if len(commit_msg) > 50:
            commit_msg = commit_msg[:47] + "..."
    else:
        commit_msg = "Lambda deployment failure"
    
    # Build critical failure Slack message
    slack_message = {
        "text": f"🚨 CRITICAL: Lambda Deployment Failed",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 CRITICAL: Lambda Deployment Failed"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Impact:* Publishing system may be offline"
                    },
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
                        "text": f"*Time:* {datetime.now().strftime('%I:%M %p UTC')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ *Action Required:* Lambda deployment failure may impact autonomous publishing. Check logs and redeploy immediately."
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=slack_message, timeout=10)
        response.raise_for_status()
        print(f"✅ Critical Lambda failure notification sent to Slack")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send Lambda failure notification: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Send Lambda deployment notification')
    parser.add_argument('--status', required=True, help='Deployment status (SUCCESS/FAILED)')
    parser.add_argument('--commit', required=True, help='Commit SHA')
    parser.add_argument('--commit-msg', help='Commit message')
    parser.add_argument('--triggered-by', required=True, help='User who triggered the deployment')
    parser.add_argument('--branch', required=True, help='Git branch')
    
    args = parser.parse_args()
    
    print(f"🚨 Processing Lambda deployment notification: {args.status}")
    success = send_lambda_notification(args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()