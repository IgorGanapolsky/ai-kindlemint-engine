#!/bin/bash
# Setup script for Claude Cost Slack Notifications

echo "🤖 Claude Cost Slack Notifications Setup"
echo "========================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/..")"

# Check if SLACK_WEBHOOK_URL is set
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "⚠️  SLACK_WEBHOOK_URL environment variable is not set!"
    echo ""
    echo "To set it up:"
    echo "1. Go to https://api.slack.com/apps"
    echo "2. Create a new app or use existing one"
    echo "3. Add 'Incoming Webhooks' and activate it"
    echo "4. Copy the webhook URL"
    echo "5. Export it: export SLACK_WEBHOOK_URL='your-webhook-url'"
    echo ""
    read -p "Do you want to continue without Slack notifications? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to add cron job
add_cron_job() {
    local schedule=$1
    local command=$2
    local comment=$3

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$comment"; then
        echo "✓ Cron job already exists: $comment"
    else
        # Add the cron job
        (crontab -l 2>/dev/null; echo "# $comment"; echo "$schedule $command") | crontab -
        echo "✅ Added cron job: $comment"
    fi
}

# Create logs directory
LOGS_DIR="$HOME/.claude-cost-logs"
mkdir -p "$LOGS_DIR"

echo ""
echo "📅 Setting up scheduled notifications..."
echo ""

# Daily summary at 9 AM
add_cron_job \
    "0 9 * * *" \
    "cd $REPO_ROOT && python3 $SCRIPT_DIR/claude_cost_slack_notifier.py daily >> $LOGS_DIR/daily.log 2>&1" \
    "Claude Cost Daily Summary"

# Weekly summary on Mondays at 9 AM
add_cron_job \
    "0 9 * * 1" \
    "cd $REPO_ROOT && python3 $SCRIPT_DIR/claude_cost_slack_notifier.py weekly >> $LOGS_DIR/weekly.log 2>&1" \
    "Claude Cost Weekly Summary"

# Efficiency report on Fridays at 3 PM
add_cron_job \
    "0 15 * * 5" \
    "cd $REPO_ROOT && python3 $SCRIPT_DIR/claude_cost_slack_notifier.py efficiency >> $LOGS_DIR/efficiency.log 2>&1" \
    "Claude Cost Efficiency Report"

# Budget check every hour (9 AM - 6 PM on weekdays)
add_cron_job \
    "0 9-18 * * 1-5" \
    "cd $REPO_ROOT && python3 $SCRIPT_DIR/claude_cost_slack_notifier.py budget --budget-limit 5.00 --budget-period daily >> $LOGS_DIR/budget.log 2>&1" \
    "Claude Cost Budget Check"

echo ""
echo "📋 Current cron jobs:"
echo "===================="
crontab -l | grep "Claude Cost" || echo "No Claude Cost jobs found"

echo ""
echo "🚀 Setup complete!"
echo ""
echo "Available commands:"
echo "  ./claude-flow-costs status           # Check current costs"
echo "  ./claude-flow-costs summary          # View cost summary"
echo "  ./claude-flow-costs export report.csv # Export cost data"
echo ""
echo "Manual notifications:"
echo "  python3 $SCRIPT_DIR/claude_cost_slack_notifier.py daily"
echo "  python3 $SCRIPT_DIR/claude_cost_slack_notifier.py weekly"
echo "  python3 $SCRIPT_DIR/claude_cost_slack_notifier.py efficiency"
echo ""
echo "Logs are stored in: $LOGS_DIR"
echo ""
echo "To view scheduled jobs: crontab -l"
echo "To edit scheduled jobs: crontab -e"
echo "To remove all Claude Cost jobs: crontab -l | grep -v 'Claude Cost' | crontab -"
