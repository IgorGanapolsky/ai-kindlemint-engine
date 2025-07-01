#!/bin/bash
# Real-time Orchestration Monitoring Dashboard

PROJECT_ROOT="$(dirname "$(dirname "$0")")"

echo "📊 KindleMint Orchestration Monitor"
echo "=================================="

# Function to check if process is running
check_process() {
    if pgrep -f "orchestrator_daemon.py" > /dev/null; then
        echo "✅ Orchestrator: RUNNING (PID: $(pgrep -f orchestrator_daemon.py))"
    else
        echo "❌ Orchestrator: STOPPED"
    fi
}

# Function to show recent logs
show_logs() {
    echo -e "\n📜 Recent Activity:"
    tail -n 20 "$PROJECT_ROOT/logs/orchestration.log" | grep -E "(INFO|WARNING|ERROR|CRITICAL)"
}

# Function to show PR status
show_pr_status() {
    echo -e "\n🔄 Open PRs:"
    gh pr list --limit 10 --state open | head -5
}

# Main monitoring loop
while true; do
    clear
    echo "📊 KindleMint Orchestration Monitor"
    echo "==================================="
    echo "Time: $(date)"
    echo ""
    
    check_process
    show_pr_status
    show_logs
    
    echo -e "\nPress Ctrl+C to exit. Refreshing in 10 seconds..."
    sleep 10
done
