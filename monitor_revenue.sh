#!/bin/bash
# Simple revenue monitor

while true; do
    clear
    echo "💰 REVENUE MONITOR 💰"
    echo "===================="
    echo "Time: $(date '+%H:%M:%S')"
    echo ""
    
    # Check if memory file exists
    if [ -f "revenue_memory.json" ]; then
        echo "📊 Today's Revenue: $(grep -o '"daily_revenues".*' revenue_memory.json | tail -1)"
    fi
    
    echo ""
    echo "🎯 Goal: $300/day"
    echo ""
    echo "Press Ctrl+C to exit"
    
    sleep 60
done
