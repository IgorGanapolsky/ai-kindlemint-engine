#!/bin/bash
# Setup Always-On Orchestration System

echo "🚀 Setting up KindleMint Always-On Orchestration System"

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$DIR")"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data/monitoring"

# Make scripts executable
chmod +x "$PROJECT_ROOT/scripts/orchestrator_daemon.py"

# For macOS - Create LaunchDaemon plist
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Setting up macOS LaunchDaemon..."
    
    PLIST_FILE="$HOME/Library/LaunchAgents/com.kindlemint.orchestrator.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kindlemint.orchestrator</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_ROOT/venv/bin/python</string>
        <string>$PROJECT_ROOT/scripts/orchestrator_daemon.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$PROJECT_ROOT/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$PROJECT_ROOT/logs/orchestration.log</string>
    
    <key>StandardErrorPath</key>
    <string>$PROJECT_ROOT/logs/orchestration-error.log</string>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

    # Load the daemon
    launchctl load "$PLIST_FILE"
    
    echo "✅ macOS LaunchDaemon installed and started"
    echo "   - To stop: launchctl unload $PLIST_FILE"
    echo "   - To restart: launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"
    echo "   - Logs: tail -f $PROJECT_ROOT/logs/orchestration*.log"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # For Linux - Use systemd
    echo "🐧 Setting up Linux systemd service..."
    
    sudo cp "$PROJECT_ROOT/kindlemint-orchestrator.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable kindlemint-orchestrator
    sudo systemctl start kindlemint-orchestrator
    
    echo "✅ Linux systemd service installed and started"
    echo "   - To check status: sudo systemctl status kindlemint-orchestrator"
    echo "   - To restart: sudo systemctl restart kindlemint-orchestrator"
    echo "   - Logs: sudo journalctl -u kindlemint-orchestrator -f"
fi

# Create monitoring dashboard script
cat > "$PROJECT_ROOT/scripts/monitor_orchestration.sh" << 'EOF'
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
EOF

chmod +x "$PROJECT_ROOT/scripts/monitor_orchestration.sh"

echo ""
echo "🎉 Always-On Orchestration Setup Complete!"
echo ""
echo "📋 Quick Commands:"
echo "   - Monitor: $PROJECT_ROOT/scripts/monitor_orchestration.sh"
echo "   - Logs: tail -f $PROJECT_ROOT/logs/orchestration*.log"
echo "   - Status: ./claude-flow status"
echo ""
echo "🤖 The orchestration system is now running 24/7 with:"
echo "   ✅ Automatic restart on failure"
echo "   ✅ Health monitoring every 60 seconds"
echo "   ✅ PR backlog processing every 5 minutes"
echo "   ✅ Resource monitoring and alerts"
echo "   ✅ Comprehensive logging"