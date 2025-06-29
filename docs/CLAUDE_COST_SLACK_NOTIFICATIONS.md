# Claude Cost Slack Notifications

Automated Slack notifications for Claude API cost tracking, providing real-time insights and budget management.

## Overview

The Claude Cost Slack Notification system provides:
- 📊 Daily and weekly cost summaries
- 🚨 Budget alerts when thresholds are exceeded
- ⚡ Efficiency reports with optimization recommendations
- 💰 Per-commit cost notifications
- 📈 Trend analysis and insights

## Quick Start

### 1. Set Up Slack Webhook

```bash
# Set your Slack webhook URL
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

# Add to your shell profile for persistence
echo "export SLACK_WEBHOOK_URL='your-webhook-url'" >> ~/.bashrc
```

### 2. Set Up Automated Notifications

```bash
# Run the setup script
./claude-flow-costs-notify setup

# This will configure:
# - Daily summaries at 9 AM
# - Weekly reports on Mondays at 9 AM
# - Efficiency reports on Fridays at 3 PM
# - Hourly budget checks during work hours
```

### 3. Test Notifications

```bash
# Test all notification types
./claude-flow-costs-notify test

# Test individual notifications
./claude-flow-costs-notify daily
./claude-flow-costs-notify weekly
./claude-flow-costs-notify efficiency
```

## Notification Types

### Daily Summary
Sent every morning at 9 AM with:
- Total daily cost
- Number of commits
- Average cost per commit
- Most expensive commit details
- Daily recommendations

### Weekly Analysis
Sent Monday mornings with:
- Week-over-week cost trends
- Daily cost breakdown chart
- Efficiency metrics
- Projected monthly costs
- Strategic recommendations

### Efficiency Reports
Sent Friday afternoons with:
- Tokens per dollar metrics
- Expensive file pattern analysis
- Time-based usage insights
- Optimization opportunities
- Cost-saving recommendations

### Budget Alerts
Triggered when costs exceed limits:
- Immediate notification
- Overage amount and percentage
- Actionable recommendations
- Recent expensive commits

### Commit Notifications
Sent after each commit (configurable threshold):
- Commit cost breakdown
- Token usage
- Files changed
- Model used

## Configuration

### Default Schedule

| Notification | Schedule | Time |
|-------------|----------|------|
| Daily Summary | Every day | 9:00 AM |
| Weekly Analysis | Mondays | 9:00 AM |
| Efficiency Report | Fridays | 3:00 PM |
| Budget Checks | Weekdays | Every hour 9AM-6PM |

### Budget Limits

Default budget limits:
- Daily: $5.00
- Weekly: $25.00
- Monthly: $100.00

Customize limits:
```bash
# Set custom daily budget
./claude-flow-costs-notify budget --budget-limit 10.00 --budget-period daily

# Set weekly budget
./claude-flow-costs-notify budget --budget-limit 50.00 --budget-period weekly
```

### Advanced Configuration

Create a configuration file for the scheduler:

```json
{
  "daily_summary": {
    "enabled": true,
    "time": "09:00"
  },
  "weekly_summary": {
    "enabled": true,
    "day": "monday",
    "time": "09:00"
  },
  "budget_alerts": {
    "enabled": true,
    "daily_limit": 5.00,
    "weekly_limit": 25.00,
    "monthly_limit": 100.00,
    "check_interval": 60
  },
  "efficiency_reports": {
    "enabled": true,
    "frequency": "weekly",
    "day": "friday",
    "time": "15:00"
  },
  "realtime_commits": {
    "enabled": true,
    "min_cost_threshold": 0.10
  }
}
```

Save as `~/.claude-cost-scheduler.json` and run:
```bash
./claude-flow-costs-notify scheduler
```

## Slack Message Examples

### Daily Summary
```
📊 Daily Claude Cost Report - ai-kindlemint-engine
Status: ✅ EXCELLENT - Low costs

📈 TODAY'S METRICS
Total Cost: $2.45
Commits: 12
Avg/Commit: $0.2042
Total Tokens: 134,567

💸 Most Expensive Commit:
`abc123d` - $0.8534
feat: Implement new authentication system...

💡 RECOMMENDATIONS
• Consider batching similar changes to reduce API calls
• Use Claude Haiku for simpler code changes
```

### Budget Alert
```
🚨 CLAUDE COST BUDGET ALERT - ai-kindlemint-engine
⚠️ Daily budget exceeded by 45.2%

Budget Limit: $5.00
Current Cost: $7.26
Overage: $2.26
Period: Daily (1 days)

🛑 IMMEDIATE ACTIONS RECOMMENDED:
• Review recent commits for expensive operations
• Consider using Claude Haiku for simpler tasks
• Batch similar changes to reduce API calls
• Enable cost pre-approval for large changes
```

## Running Continuous Scheduler

For always-on notifications without cron:

```bash
# Run in foreground
./claude-flow-costs-notify scheduler

# Run in background
nohup ./claude-flow-costs-notify scheduler > scheduler.log 2>&1 &

# Install as system service (macOS)
python3 scripts/claude_cost_scheduler.py install-service
```

## Troubleshooting

### Notifications not sending?

1. Check Slack webhook:
```bash
echo $SLACK_WEBHOOK_URL
```

2. Test webhook manually:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  $SLACK_WEBHOOK_URL
```

3. Check logs:
```bash
tail -f ~/.claude-cost-logs/*.log
```

### Cron jobs not running?

1. Verify cron jobs:
```bash
crontab -l | grep "Claude Cost"
```

2. Check cron service:
```bash
# Linux
systemctl status cron

# macOS
sudo launchctl list | grep cron
```

3. Test command manually:
```bash
cd /path/to/repo && python3 scripts/claude_cost_slack_notifier.py daily
```

### Budget alerts too frequent?

Adjust check interval in configuration:
```json
{
  "budget_alerts": {
    "check_interval": 180  // Check every 3 hours instead of hourly
  }
}
```

## Integration with CI/CD

Add to GitHub Actions:

```yaml
- name: Send Claude Cost Report
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    ./claude-flow-costs-notify daily

- name: Check Claude Budget
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    ./claude-flow-costs-notify budget --budget-limit 10.00 --budget-period daily
    # Fail build if over budget
    if [ $? -ne 0 ]; then
      echo "Claude costs exceed budget!"
      exit 1
    fi
```

## Privacy & Security

- All cost data remains local in your repository
- Slack webhook URL should be kept secret
- No sensitive code content is sent to Slack
- Only aggregated metrics and summaries are shared

## Customization

### Custom Notification Templates

Modify notification formatting in `claude_cost_slack_notifier.py`:
- Update emoji and colors
- Add custom fields
- Include repository-specific metrics
- Integrate with other monitoring tools

### Additional Metrics

Extend the system to track:
- Cost per feature/module
- Developer-specific costs
- Model usage distribution
- Time-of-day patterns
- Cost vs. code quality metrics

## Best Practices

1. **Set Realistic Budgets**: Start with higher limits and adjust based on actual usage
2. **Review Weekly Trends**: Use insights to optimize development patterns
3. **Act on Recommendations**: Implement suggested optimizations
4. **Monitor Efficiency**: Track tokens-per-dollar improvements
5. **Batch Similar Work**: Group related changes to reduce API calls

## Support

For issues or feature requests:
- Check logs in `~/.claude-cost-logs/`
- Review configuration with `./claude-flow-costs-notify scheduler config`
- Update notification scripts as needed
