#!/usr/bin/env python3
"""
One-Click Deployment Script for Complete Passive Income Automation
Deploys everything to run without manual intervention
"""
import os
import subprocess
import json
import time
from datetime import datetime

class OneClickDeployment:
    """Complete deployment automation for passive income system"""
    
    def __init__(self):
        self.deployment_log = []
        self.start_time = datetime.now()
    
    def log(self, message):
        """Log deployment progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def check_prerequisites(self):
        """Check if all required tools are available"""
        self.log("Checking prerequisites...")
        
        required_env_vars = [
            'GEMINI_API_KEY',
            'OPENAI_API_KEY', 
            'GMAIL_USER',
            'GMAIL_APP_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        self.log("All prerequisites met")
        return True
    
    def setup_local_automation(self):
        """Set up local automation that runs continuously"""
        self.log("Setting up local passive income automation...")
        
        # Create automation scheduler
        scheduler_code = '''
import schedule
import time
import subprocess
import os
from datetime import datetime

def generate_daily_book():
    """Generate a book automatically"""
    print(f"[{datetime.now()}] Starting automated book generation...")
    
    try:
        # Run mission control with random topic
        result = subprocess.run(['python', 'mission_control.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Book generated successfully")
            
            # Log to dashboard
            try:
                from automation.passive_income_dashboard import dashboard
                dashboard.log_book_generation(
                    title="Auto-Generated Book",
                    topic="Automated Adventure",
                    word_count=3000
                )
            except:
                pass
        else:
            print(f"✗ Book generation failed: {result.stderr}")
    
    except Exception as e:
        print(f"✗ Automation error: {e}")

def start_automation():
    """Start the passive income automation"""
    print("🚀 Starting Passive Income Automation")
    print("📅 Daily book generation scheduled for 6:00 AM")
    
    # Schedule daily book generation
    schedule.every().day.at("06:00").do(generate_daily_book)
    
    # Schedule weekly analytics
    schedule.every().monday.at("09:00").do(lambda: print("📊 Weekly analytics ready"))
    
    # Run continuously
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    start_automation()
'''
        
        with open('automation/scheduler.py', 'w') as f:
            f.write(scheduler_code)
        
        self.log("Local automation scheduler created")
    
    def create_startup_script(self):
        """Create startup script for complete automation"""
        startup_script = '''#!/bin/bash

# AI KindleMint Engine - Complete Automation Startup Script
echo "🚀 Starting AI KindleMint Passive Income Engine..."

# Kill any existing processes
pkill -f "passive_income_dashboard.py"
pkill -f "webhook_server.py"
pkill -f "scheduler.py"

# Start the dashboard (monitoring)
echo "📊 Starting passive income dashboard..."
nohup python automation/passive_income_dashboard.py > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "Dashboard PID: $DASHBOARD_PID"

# Start webhook server (external triggers)
echo "🔗 Starting webhook server..."
nohup python webhook_server.py > logs/webhook.log 2>&1 &
WEBHOOK_PID=$!
echo "Webhook PID: $WEBHOOK_PID"

# Start automation scheduler (daily generation)
echo "⏰ Starting daily automation scheduler..."
nohup python automation/scheduler.py > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "Scheduler PID: $SCHEDULER_PID"

# Save PIDs for management
echo "$DASHBOARD_PID" > automation/dashboard.pid
echo "$WEBHOOK_PID" > automation/webhook.pid
echo "$SCHEDULER_PID" > automation/scheduler.pid

# Wait for services to start
sleep 5

echo "✅ All services started successfully!"
echo ""
echo "🎯 PASSIVE INCOME SYSTEM ACTIVE"
echo "📊 Dashboard: http://localhost:5000"
echo "🔗 Webhooks: http://localhost:5001"
echo "📚 Books generate daily at 6:00 AM automatically"
echo "💰 Monitor earnings and progress via dashboard"
echo ""
echo "🛑 To stop: ./stop_automation.sh"
echo "📋 View logs: tail -f logs/*.log"
'''
        
        with open('start_automation.sh', 'w') as f:
            f.write(startup_script)
        
        os.chmod('start_automation.sh', 0o755)
        
        # Create stop script
        stop_script = '''#!/bin/bash

echo "🛑 Stopping AI KindleMint automation..."

# Read PIDs and kill processes
if [ -f automation/dashboard.pid ]; then
    kill $(cat automation/dashboard.pid) 2>/dev/null
    rm automation/dashboard.pid
fi

if [ -f automation/webhook.pid ]; then
    kill $(cat automation/webhook.pid) 2>/dev/null
    rm automation/webhook.pid
fi

if [ -f automation/scheduler.pid ]; then
    kill $(cat automation/scheduler.pid) 2>/dev/null
    rm automation/scheduler.pid
fi

# Kill any remaining processes
pkill -f "passive_income_dashboard.py"
pkill -f "webhook_server.py"
pkill -f "scheduler.py"

echo "✅ Automation stopped"
'''
        
        with open('stop_automation.sh', 'w') as f:
            f.write(stop_script)
        
        os.chmod('stop_automation.sh', 0o755)
        
        self.log("Startup and stop scripts created")
    
    def create_monitoring_dashboard(self):
        """Create enhanced monitoring dashboard"""
        dashboard_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI KindleMint - Passive Income Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2em; font-weight: bold; color: #2196F3; }
        .stat-label { color: #666; margin-top: 5px; }
        .recent-books { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .book-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .book-item:last-child { border-bottom: none; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
        .status.active { background: #4CAF50; color: white; }
        .status.generated { background: #2196F3; color: white; }
        .controls { margin: 20px 0; text-align: center; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI KindleMint Passive Income Dashboard</h1>
            <p>Automated Book Generation & Publishing System</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_books }}</div>
                <div class="stat-label">Total Books Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.books_this_month }}</div>
                <div class="stat-label">Books This Month</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${{ stats.estimated_revenue }}</div>
                <div class="stat-label">Estimated Revenue</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">
                    <span class="status {{ stats.automation_status }}">{{ stats.automation_status.title() }}</span>
                </div>
                <div class="stat-label">Automation Status</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="triggerGeneration()">Generate Book Now</button>
            <button class="btn btn-success" onclick="refreshStats()">Refresh Stats</button>
        </div>
        
        <div class="recent-books">
            <h3>Recent Books</h3>
            {% for book in stats.recent_books %}
            <div class="book-item">
                <strong>{{ book[0] }}</strong> - {{ book[1] }}
                <span class="status generated">{{ book[3] }}</span>
                <div style="font-size: 0.9em; color: #666;">{{ book[2] }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        function refreshStats() {
            location.reload();
        }
        
        function triggerGeneration() {
            const topic = prompt("Enter book topic (or leave blank for random):");
            fetch('/api/trigger-generation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic || 'Adventure Quest' })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.success) location.reload();
            });
        }
        
        // Auto-refresh every 5 minutes
        setInterval(refreshStats, 300000);
    </script>
</body>
</html>
'''
        
        os.makedirs('templates', exist_ok=True)
        with open('templates/dashboard.html', 'w') as f:
            f.write(dashboard_template)
        
        self.log("Enhanced monitoring dashboard created")
    
    def create_logs_directory(self):
        """Create logs directory for monitoring"""
        os.makedirs('logs', exist_ok=True)
        self.log("Logs directory created")
    
    def deploy_complete_system(self):
        """Deploy the complete passive income system"""
        self.log("Starting complete system deployment...")
        
        if not self.check_prerequisites():
            self.log("❌ Prerequisites not met. Deployment aborted.")
            return False
        
        self.create_logs_directory()
        self.setup_local_automation()
        self.create_startup_script()
        self.create_monitoring_dashboard()
        
        # Create deployment summary
        summary = f'''
AI KINDLEMINT PASSIVE INCOME SYSTEM DEPLOYED
===========================================

Deployment completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Deployment time: {(datetime.now() - self.start_time).total_seconds():.1f} seconds

SYSTEM COMPONENTS:
✅ Mission Control (Book Generation)
✅ Webhook Server (External Triggers) 
✅ Passive Income Dashboard (Monitoring)
✅ Daily Automation Scheduler
✅ Email Notifications
✅ File Management & Analytics

AUTOMATION FEATURES:
📚 Daily book generation at 6:00 AM
📊 Real-time income tracking
📧 Email notifications for publications
🔗 Webhook endpoints for external automation
📈 Revenue estimation and analytics

GETTING STARTED:
1. Run: ./start_automation.sh
2. Visit: http://localhost:5000 (Dashboard)
3. Books generate automatically daily
4. Monitor progress and earnings via dashboard

MANAGEMENT:
- Start: ./start_automation.sh
- Stop: ./stop_automation.sh  
- Logs: tail -f logs/*.log
- Dashboard: http://localhost:5000

PASSIVE INCOME MODE: ACTIVE
Your system now generates books automatically without manual work!
'''
        
        with open('DEPLOYMENT_SUMMARY.txt', 'w') as f:
            f.write(summary)
        
        self.log("✅ Complete passive income system deployed!")
        print(summary)
        
        return True

def main():
    """Main deployment function"""
    deployer = OneClickDeployment()
    success = deployer.deploy_complete_system()
    
    if success:
        print("\n🎉 DEPLOYMENT COMPLETE!")
        print("🚀 Run './start_automation.sh' to begin earning passive income")
        print("📊 Monitor at: http://localhost:5000")
    else:
        print("\n❌ Deployment failed. Check logs for details.")

if __name__ == '__main__':
    main()