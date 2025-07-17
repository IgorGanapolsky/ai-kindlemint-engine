#!/bin/bash
# Add these cron jobs for automatic profit generation
echo "# Puzzle Book Profit Automation" >> /tmp/cron_jobs
echo "0 9,14,19 * * * cd /workspace && python3 scripts/traffic_generation/reddit_organic_poster.py" >> /tmp/cron_jobs
echo "0 10,16 * * * cd /workspace && python3 scripts/traffic_generation/pinterest_pin_scheduler.py" >> /tmp/cron_jobs
echo "0 23 * * * cd /workspace && python3 scripts/revenue_dashboard.py > /workspace/daily_revenue_report.txt" >> /tmp/cron_jobs
echo "Cron jobs ready to install. Run: crontab /tmp/cron_jobs"
