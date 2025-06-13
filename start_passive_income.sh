#!/bin/bash

# AI KindleMint Passive Income Automation Startup Script
echo "🚀 Starting AI KindleMint Passive Income System..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing automation processes
pkill -f "simple_passive_income.py" 2>/dev/null
pkill -f "passive_income_dashboard.py" 2>/dev/null

echo "📊 Starting passive income automation..."

# Start the automation in background
nohup python automation/simple_passive_income.py start > logs/automation.log 2>&1 &
AUTOMATION_PID=$!

# Save PID for management
echo $AUTOMATION_PID > automation.pid

echo "✅ Passive Income Automation Started!"
echo ""
echo "🎯 SYSTEM STATUS:"
echo "   📚 Daily book generation at 6:00 AM"
echo "   💰 Estimated $2.50-$4.00 per book"
echo "   📊 View stats: python automation/view_stats.py"
echo "   📋 View logs: tail -f logs/automation.log"
echo ""
echo "📈 IMMEDIATE ACTIONS:"
echo "   • Test generation: python automation/simple_passive_income.py generate"
echo "   • View statistics: python automation/view_stats.py"
echo "   • Stop automation: ./stop_passive_income.sh"
echo ""
echo "💤 Your passive income system is now running automatically!"
echo "📚 Books will generate daily without manual work"