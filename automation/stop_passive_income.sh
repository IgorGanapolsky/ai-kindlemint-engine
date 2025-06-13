#!/bin/bash

echo "🛑 Stopping AI KindleMint Passive Income Automation..."

# Kill automation process using PID file
if [ -f automation.pid ]; then
    PID=$(cat automation.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Stopped automation process (PID: $PID)"
    else
        echo "⚠ Process not running (PID: $PID)"
    fi
    rm automation.pid
else
    echo "⚠ No PID file found"
fi

# Kill any remaining processes
pkill -f "simple_passive_income.py" 2>/dev/null && echo "✅ Killed remaining automation processes"
pkill -f "passive_income_dashboard.py" 2>/dev/null

echo "🛑 Passive income automation stopped"