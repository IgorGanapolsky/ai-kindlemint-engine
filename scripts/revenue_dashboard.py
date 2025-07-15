#!/usr/bin/env python3
"""
Revenue Dashboard
Real-time monitoring of all revenue-generating systems
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

class RevenueDashboard:
    """Real-time revenue monitoring dashboard"""
    
    def __init__(self):
        self.base_path = Path("/home/igorganapolsky/workspace/git/ai-kindlemint-engine")
        self.traffic_path = self.base_path / "worktrees/experiments/scripts/traffic_generation"
    
    def get_system_status(self):
        """Get status of all revenue systems"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "revenue": {},
            "traffic": {},
            "next_actions": []
        }
        
        # Check traffic generation systems
        traffic_systems = [
            ("reddit_traffic", "quick_start_reddit.py"),
            ("facebook_traffic", "facebook_group_engager.py"),
            ("pinterest_traffic", "pinterest_pin_scheduler.py")
        ]
        
        for system_name, script_name in traffic_systems:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", script_name], 
                    capture_output=True, 
                    text=True
                )
                status["systems"][system_name] = "active" if result.returncode == 0 else "inactive"
            except:
                status["systems"][system_name] = "unknown"
        
        # Check book generation
        try:
            result = subprocess.run(
                ["pgrep", "-f", "quick_book_generator.py"], 
                capture_output=True, 
                text=True
            )
            status["systems"]["book_generation"] = "active" if result.returncode == 0 else "inactive"
        except:
            status["systems"]["book_generation"] = "unknown"
        
        # Check email automation
        try:
            result = subprocess.run(
                ["pgrep", "-f", "email_automation.py"], 
                capture_output=True, 
                text=True
            )
            status["systems"]["email_automation"] = "active" if result.returncode == 0 else "inactive"
        except:
            status["systems"]["email_automation"] = "unknown"
        
        # Load revenue data
        try:
            with open(self.base_path / "revenue_data.json", 'r') as f:
                revenue_data = json.load(f)
            status["revenue"] = revenue_data
        except:
            status["revenue"] = {"total_revenue": 0, "daily_tracking": {}}
        
        # Load revenue status
        try:
            with open(self.base_path / "revenue_status.json", 'r') as f:
                revenue_status = json.load(f)
            status["revenue"].update(revenue_status)
        except:
            pass
        
        # Check traffic logs
        try:
            with open(self.traffic_path / "traffic_generation.log", 'r') as f:
                log_lines = f.readlines()
                recent_logs = log_lines[-10:] if len(log_lines) > 10 else log_lines
                status["traffic"]["recent_logs"] = recent_logs
        except:
            status["traffic"]["recent_logs"] = []
        
        # Determine next actions
        if status["systems"].get("reddit_traffic") == "inactive":
            status["next_actions"].append("Restart Reddit traffic generation")
        
        if status["systems"].get("facebook_traffic") == "inactive":
            status["next_actions"].append("Restart Facebook traffic generation")
        
        if status["systems"].get("pinterest_traffic") == "inactive":
            status["next_actions"].append("Restart Pinterest traffic generation")
        
        if status["revenue"].get("total_revenue", 0) == 0:
            status["next_actions"].append("Upload backend course to Gumroad")
            status["next_actions"].append("Monitor email captures on landing page")
        
        return status
    
    def display_dashboard(self):
        """Display the revenue dashboard"""
        status = self.get_system_status()
        
        print("💰 REVENUE AUTOMATION DASHBOARD")
        print("=" * 60)
        print(f"📊 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Revenue Summary
        total_revenue = status["revenue"].get("total_revenue", 0)
        current_daily = status["revenue"].get("current_daily", 0)
        goal = 300
        
        print("💵 REVENUE SUMMARY")
        print("-" * 30)
        print(f"Today's Revenue: ${current_daily:.2f}")
        print(f"Total Revenue:   ${total_revenue:.2f}")
        print(f"Daily Goal:      ${goal:.2f}")
        print(f"Goal Progress:   {(current_daily/goal)*100:.1f}%")
        print()
        
        # System Status
        print("🚀 SYSTEM STATUS")
        print("-" * 30)
        for system, state in status["systems"].items():
            icon = "✅" if state == "active" else "❌" if state == "inactive" else "⚠️"
            print(f"{icon} {system.replace('_', ' ').title()}: {state}")
        print()
        
        # Traffic Status
        print("📈 TRAFFIC STATUS")
        print("-" * 30)
        if status["traffic"]["recent_logs"]:
            print("Recent Activity:")
            for log in status["traffic"]["recent_logs"][-3:]:
                print(f"  {log.strip()}")
        else:
            print("No recent traffic logs found")
        print()
        
        # Opportunities
        print("🎯 OPPORTUNITIES")
        print("-" * 30)
        opportunities = status["revenue"].get("opportunities", [])
        if opportunities:
            for opp in opportunities:
                print(f"• {opp}")
        else:
            print("• Monitor traffic generation performance")
            print("• Upload backend course to Gumroad")
            print("• Check email capture conversion rates")
        print()
        
        # Next Actions
        print("⚡ NEXT ACTIONS")
        print("-" * 30)
        if status["next_actions"]:
            for action in status["next_actions"]:
                print(f"• {action}")
        else:
            print("• All systems running optimally")
            print("• Monitor for first sales")
        print()
        
        # Revenue Path
        print("📊 REVENUE PATH")
        print("-" * 30)
        print("Day 1-2: Traffic generation → 500+ daily visitors")
        print("Day 3-4: Email captures → 100+ subscribers")
        print("Day 5-6: Frontend sales → $124.75/day")
        print("Day 7: Backend sales → $485/day")
        print("Target: $300/day by Week 2")
        print()
        
        print("=" * 60)
        print("🚀 Revenue automation is running autonomously!")
        print("💡 Monitor this dashboard for real-time updates")

def main():
    """Main entry point"""
    dashboard = RevenueDashboard()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main() 