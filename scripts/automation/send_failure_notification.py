#!/usr/bin/env python3
"""
Context-Aware Failure Notification System
Sends rich, actionable failure alerts to Slack with debugging details
"""
import sys
import os
import argparse
import requests
import json
import glob
import re
from datetime import datetime
from pathlib import Path

def get_error_context():
    """Extract meaningful error context from recent logs."""
    try:
        # Look for recent error patterns in common log locations
        log_patterns = [
            "logs/*.log",
            "*.log", 
            "publishing_*.log"
        ]
        
        error_indicators = [
            r"❌.*ERROR.*: (.+)",
            r"INTERFACE ERROR: (.+)",
            r"CREATION ERROR: (.+)", 
            r"Could not find or click (.+)",
            r"Process completed with exit code (\d+)",
            r"Exception: (.+)"
        ]
        
        latest_error = "Unknown error"
        
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                        for error_pattern in error_indicators:
                            matches = re.findall(error_pattern, content)
                            if matches:
                                latest_error = matches[-1][:100] + "..." if len(matches[-1]) > 100 else matches[-1]
                                return latest_error
                except:
                    continue
        
        return latest_error
        
    except Exception as e:
        return f"Error context extraction failed: {str(e)[:50]}"

def send_failure_notification(args):
    """Send detailed failure notification to Slack."""
    
    # Get Slack webhook from environment
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("❌ No SLACK_WEBHOOK_URL environment variable found")
        return False
    
    # Truncate commit SHA for readability
    short_commit = args.commit[:7] if args.commit else "unknown"
    
    # Handle commit message with better debugging
    if args.commit_msg and args.commit_msg.strip():
        commit_msg = args.commit_msg.strip()
        if len(commit_msg) > 50:
            commit_msg = commit_msg[:47] + "..."
    else:
        commit_msg = "No commit message provided"
        print(f"⚠️ DEBUG: args.commit_msg = '{args.commit_msg}'")
    
    # Extract series name from metadata
    series_name = "Unknown Series"
    try:
        # Look for metadata in hierarchical structure
        output_dir = Path("output")
        for brand_dir in output_dir.iterdir():
            if brand_dir.is_dir():
                for series_dir in brand_dir.iterdir():
                    if series_dir.is_dir():
                        for volume_dir in series_dir.glob("volume_*"):
                            metadata_file = volume_dir / "metadata.json"
                            if metadata_file.exists():
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                    series_name = f"{metadata.get('brand', 'Unknown Brand')} - {metadata.get('series', 'Unknown Series')}"
                                    break
                        break
                break
    except:
        pass
    
    # Build rich Slack message
    slack_message = {
        "text": f"❌ FAILURE: {args.workflow}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"❌ FAILURE: {args.workflow}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Series:* {series_name}"
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
                        "text": f"*Volumes:* {args.volumes}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed Step:* {args.failed_step}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:* {datetime.now().strftime('%I:%M %p UTC')}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔍 View Logs"
                        },
                        "url": args.run_url,
                        "style": "danger"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*Error Context:* {get_error_context()}\n*Debug Info:* Run ID `{args.run_id}` | <{args.run_url}|Direct Link to Failure>"
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=slack_message, timeout=10)
        response.raise_for_status()
        print(f"✅ Failure notification sent to Slack successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Send context-aware failure notification')
    parser.add_argument('--workflow', required=True, help='Workflow name')
    parser.add_argument('--run-id', required=True, help='GitHub run ID')
    parser.add_argument('--run-url', required=True, help='Direct URL to GitHub run')
    parser.add_argument('--commit', required=True, help='Commit SHA')
    parser.add_argument('--commit-msg', help='Commit message')
    parser.add_argument('--triggered-by', required=True, help='User who triggered the workflow')
    parser.add_argument('--branch', required=True, help='Git branch')
    parser.add_argument('--volumes', help='Volumes being published')
    parser.add_argument('--failed-step', help='Failed step status')
    
    args = parser.parse_args()
    
    print(f"🚨 Sending failure notification for: {args.workflow}")
    success = send_failure_notification(args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()