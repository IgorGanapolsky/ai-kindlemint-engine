#!/bin/bash
while true; do
    python3 check_revenue.py >> revenue_log.txt
    sleep 300  # Check every 5 minutes
done
