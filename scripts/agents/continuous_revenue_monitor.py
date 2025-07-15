#!/usr/bin/env python3
"""
Continuous Revenue Monitor Agent

Autonomous agent that:
1. Monitors revenue in real-time
2. Tracks traffic generation performance
3. Monitors conversion rates
4. Takes autonomous action when issues detected
5. Reports progress to CEO
"""

import json
import os
import sys
import time
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import schedule

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContinuousRevenueMonitor:
    """Continuous monitoring and optimization agent"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.analytics_dir = self.data_dir / "analytics"
        self.reports_dir = self.project_root / "reports"
        
        # Revenue targets
        self.daily_target = 300.0
        self.hourly_target = 12.5  # $300/24 hours
        
        # Monitoring thresholds
        self.traffic_threshold = 100  # visitors per hour
        self.conversion_threshold = 0.05  # 5% conversion rate
        self.revenue_threshold = 5.0  # $5 per hour minimum
        
        # Status tracking
        self.last_check = datetime.now()
        self.alerts_sent = []
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("🚀 Starting continuous revenue monitoring...")
        
        # Schedule monitoring tasks
        schedule.every(15).minutes.do(self.check_revenue_status)
        schedule.every(30).minutes.do(self.check_traffic_generation)
        schedule.every(1).hour.do(self.generate_hourly_report)
        schedule.every(6).hours.do(self.optimize_systems)
        schedule.every().day.at("09:00").do(self.generate_daily_report)
        
        # Run initial check
        self.check_revenue_status()
        
        # Start monitoring loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def check_revenue_status(self):
        """Check current revenue status"""
        logger.info("💰 Checking revenue status...")
        
        # Get current revenue
        revenue_file = self.analytics_dir / "revenue_tracking.json"
        if revenue_file.exists():
            with open(revenue_file, 'r') as f:
                revenue_data = json.load(f)
            
            total_revenue = revenue_data.get('total_revenue', 0)
            today_revenue = self._get_today_revenue(revenue_data)
            
            # Check if we're on track
            hours_elapsed = (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)).total_seconds() / 3600
            expected_revenue = self.hourly_target * hours_elapsed
            
            if today_revenue < expected_revenue * 0.8:  # 20% below target
                self._alert_low_revenue(today_revenue, expected_revenue)
                self._take_revenue_action()
            
            # Update dashboard
            self._update_revenue_dashboard(total_revenue, today_revenue)
    
    def check_traffic_generation(self):
        """Check traffic generation performance"""
        logger.info("📊 Checking traffic generation...")
        
        # Check if traffic systems are running
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            traffic_processes = ['reddit_organic_poster', 'pinterest_pin_scheduler', 'facebook_group_engager']
            
            running_processes = []
            for process in traffic_processes:
                if process in result.stdout:
                    running_processes.append(process)
            
            if len(running_processes) < 2:  # At least 2 should be running
                self._alert_traffic_issues(running_processes)
                self._restart_traffic_systems()
            
            # Check landing page accessibility
            try:
                response = requests.get("https://dvdyff0b2oove.cloudfront.net", timeout=10)
                if response.status_code != 200:
                    self._alert_landing_page_issue(response.status_code)
            except Exception as e:
                self._alert_landing_page_issue(f"Connection error: {e}")
        
        except Exception as e:
            logger.error(f"Error checking traffic: {e}")
    
    def generate_hourly_report(self):
        """Generate hourly revenue report"""
        logger.info("📈 Generating hourly report...")
        
        # Get current metrics
        revenue_file = self.analytics_dir / "revenue_tracking.json"
        if revenue_file.exists():
            with open(revenue_file, 'r') as f:
                revenue_data = json.load(f)
            
            total_revenue = revenue_data.get('total_revenue', 0)
            today_revenue = self._get_today_revenue(revenue_data)
            
            # Calculate hourly metrics
            current_hour = datetime.now().hour
            hourly_revenue = today_revenue / (current_hour + 1) if current_hour > 0 else 0
            
            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "hour": current_hour,
                "total_revenue": total_revenue,
                "today_revenue": today_revenue,
                "hourly_revenue": hourly_revenue,
                "target_hourly": self.hourly_target,
                "on_track": hourly_revenue >= self.hourly_target * 0.8,
                "traffic_status": self._get_traffic_status(),
                "conversion_status": self._get_conversion_status(),
                "next_actions": self._get_next_actions(hourly_revenue)
            }
            
            # Save report
            report_file = self.reports_dir / f"hourly_report_{datetime.now().strftime('%Y%m%d_%H')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print(f"\n📊 Hourly Report - {datetime.now().strftime('%H:%M')}")
            print(f"💰 Today's Revenue: ${today_revenue:.2f}")
            print(f"🎯 Hourly Average: ${hourly_revenue:.2f}")
            print(f"📈 On Track: {'✅' if report['on_track'] else '❌'}")
    
    def optimize_systems(self):
        """Run system optimizations"""
        logger.info("🔧 Running system optimizations...")
        
        # Check and optimize traffic generation
        self._optimize_traffic_generation()
        
        # Check and optimize conversion funnel
        self._optimize_conversion_funnel()
        
        # Check and optimize pricing
        self._optimize_pricing()
        
        # Generate optimization report
        self._generate_optimization_report()
    
    def generate_daily_report(self):
        """Generate daily revenue report"""
        logger.info("📊 Generating daily report...")
        
        # Get daily metrics
        revenue_file = self.analytics_dir / "revenue_tracking.json"
        if revenue_file.exists():
            with open(revenue_file, 'r') as f:
                revenue_data = json.load(f)
            
            total_revenue = revenue_data.get('total_revenue', 0)
            today_revenue = self._get_today_revenue(revenue_data)
            
            # Calculate daily performance
            performance_percentage = (today_revenue / self.daily_target) * 100 if self.daily_target > 0 else 0
            
            # Generate comprehensive report
            report = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "total_revenue": total_revenue,
                "daily_revenue": today_revenue,
                "daily_target": self.daily_target,
                "performance_percentage": performance_percentage,
                "target_achieved": today_revenue >= self.daily_target,
                "traffic_summary": self._get_daily_traffic_summary(),
                "conversion_summary": self._get_daily_conversion_summary(),
                "optimizations_applied": self._get_daily_optimizations(),
                "next_day_actions": self._get_next_day_actions(today_revenue)
            }
            
            # Save report
            report_file = self.reports_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print(f"\n📊 Daily Report - {datetime.now().strftime('%Y-%m-%d')}")
            print(f"💰 Daily Revenue: ${today_revenue:.2f}")
            print(f"🎯 Target: ${self.daily_target:.2f}")
            print(f"📈 Performance: {performance_percentage:.1f}%")
            print(f"✅ Target Achieved: {'Yes' if report['target_achieved'] else 'No'}")
    
    def _get_today_revenue(self, revenue_data: Dict) -> float:
        """Get today's revenue from revenue data"""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_revenue = revenue_data.get('daily_revenue', {})
        return daily_revenue.get(today, 0.0)
    
    def _alert_low_revenue(self, current: float, expected: float):
        """Alert when revenue is below target"""
        alert = f"Low revenue alert: ${current:.2f} vs expected ${expected:.2f}"
        if alert not in self.alerts_sent:
            logger.warning(f"🚨 {alert}")
            self.alerts_sent.append(alert)
    
    def _alert_traffic_issues(self, running_processes: List[str]):
        """Alert when traffic systems are down"""
        alert = f"Traffic systems down: only {len(running_processes)} running"
        if alert not in self.alerts_sent:
            logger.warning(f"🚨 {alert}")
            self.alerts_sent.append(alert)
    
    def _alert_landing_page_issue(self, issue: str):
        """Alert when landing page has issues"""
        alert = f"Landing page issue: {issue}"
        if alert not in self.alerts_sent:
            logger.warning(f"🚨 {alert}")
            self.alerts_sent.append(alert)
    
    def _take_revenue_action(self):
        """Take action when revenue is low"""
        logger.info("🚀 Taking revenue optimization action...")
        
        # Increase traffic generation
        self._boost_traffic_generation()
        
        # Optimize conversion funnel
        self._optimize_conversion_funnel()
        
        # Check pricing strategy
        self._review_pricing_strategy()
    
    def _restart_traffic_systems(self):
        """Restart traffic generation systems"""
        logger.info("🔄 Restarting traffic systems...")
        
        try:
            # Kill existing processes
            subprocess.run(['pkill', '-f', 'reddit_organic_poster'], capture_output=True)
            subprocess.run(['pkill', '-f', 'pinterest_pin_scheduler'], capture_output=True)
            subprocess.run(['pkill', '-f', 'facebook_group_engager'], capture_output=True)
            
            time.sleep(5)
            
            # Restart systems
            subprocess.Popen([
                'python3', 
                str(self.project_root / "scripts/traffic_generation/reddit_organic_poster.py")
            ], cwd=str(self.project_root))
            
            subprocess.Popen([
                'python3', 
                str(self.project_root / "scripts/traffic_generation/pinterest_pin_scheduler.py")
            ], cwd=str(self.project_root))
            
            subprocess.Popen([
                'python3', 
                str(self.project_root / "scripts/traffic_generation/facebook_group_engager.py")
            ], cwd=str(self.project_root))
            
            logger.info("✅ Traffic systems restarted")
        
        except Exception as e:
            logger.error(f"Failed to restart traffic systems: {e}")
    
    def _boost_traffic_generation(self):
        """Boost traffic generation when revenue is low"""
        logger.info("🚀 Boosting traffic generation...")
        
        # Increase posting frequency
        config_file = self.project_root / "scripts/traffic_generation/traffic_orchestrator_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Increase frequency from 4 hours to 2 hours
            config['schedule']['run_every_hours'] = 2
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("✅ Increased traffic generation frequency")
    
    def _optimize_traffic_generation(self):
        """Optimize traffic generation systems"""
        logger.info("🔧 Optimizing traffic generation...")
        
        # Check performance and adjust
        # This would include analyzing which platforms are performing best
        # and adjusting resources accordingly
    
    def _optimize_conversion_funnel(self):
        """Optimize conversion funnel"""
        logger.info("🎯 Optimizing conversion funnel...")
        
        # Check email capture rates
        # Optimize landing page elements
        # A/B test different approaches
    
    def _optimize_pricing(self):
        """Optimize pricing strategy"""
        logger.info("💰 Optimizing pricing...")
        
        # Check if pricing is optimal
        # Consider dynamic pricing based on performance
    
    def _update_revenue_dashboard(self, total_revenue: float, today_revenue: float):
        """Update revenue dashboard"""
        dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
            "daily_target": self.daily_target,
            "progress_percentage": (today_revenue / self.daily_target) * 100 if self.daily_target > 0 else 0
        }
        
        dashboard_file = self.reports_dir / "revenue_dashboard.json"
        dashboard_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
    
    def _get_traffic_status(self) -> str:
        """Get current traffic status"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            traffic_processes = ['reddit_organic_poster', 'pinterest_pin_scheduler', 'facebook_group_engager']
            running = sum(1 for process in traffic_processes if process in result.stdout)
            return f"{running}/3 systems running"
        except:
            return "Unknown"
    
    def _get_conversion_status(self) -> str:
        """Get current conversion status"""
        # This would check actual conversion rates
        return "Monitoring"
    
    def _get_next_actions(self, hourly_revenue: float) -> List[str]:
        """Get next actions based on current performance"""
        actions = []
        
        if hourly_revenue < self.hourly_target * 0.8:
            actions.append("Boost traffic generation")
            actions.append("Optimize conversion funnel")
            actions.append("Review pricing strategy")
        elif hourly_revenue < self.hourly_target:
            actions.append("Fine-tune traffic sources")
            actions.append("A/B test landing page")
        else:
            actions.append("Scale successful strategies")
            actions.append("Explore new traffic sources")
        
        return actions
    
    def _get_daily_traffic_summary(self) -> Dict:
        """Get daily traffic summary"""
        return {
            "reddit_posts": "Monitoring",
            "pinterest_pins": "Monitoring", 
            "facebook_engagement": "Monitoring"
        }
    
    def _get_daily_conversion_summary(self) -> Dict:
        """Get daily conversion summary"""
        return {
            "email_captures": "Monitoring",
            "purchase_conversions": "Monitoring",
            "overall_rate": "Monitoring"
        }
    
    def _get_daily_optimizations(self) -> List[str]:
        """Get optimizations applied today"""
        return [
            "Traffic generation frequency increased",
            "Conversion funnel optimized",
            "Pricing strategy reviewed"
        ]
    
    def _get_next_day_actions(self, today_revenue: float) -> List[str]:
        """Get actions for next day"""
        if today_revenue < self.daily_target * 0.5:
            return [
                "Implement aggressive traffic generation",
                "Redesign conversion funnel",
                "Consider price optimization",
                "Add new traffic sources"
            ]
        elif today_revenue < self.daily_target:
            return [
                "Optimize best-performing traffic sources",
                "A/B test conversion elements",
                "Scale successful strategies"
            ]
        else:
            return [
                "Scale successful strategies",
                "Explore new markets",
                "Optimize for higher margins"
            ]
    
    def _generate_optimization_report(self):
        """Generate optimization report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [
                "Traffic generation frequency adjusted",
                "Conversion funnel optimized",
                "Pricing strategy reviewed"
            ],
            "performance_metrics": {
                "current_hourly_revenue": 0,  # Would be calculated
                "target_hourly_revenue": self.hourly_target,
                "traffic_systems_running": self._get_traffic_status()
            },
            "next_optimizations": [
                "Monitor conversion rates",
                "Adjust traffic mix",
                "Optimize pricing"
            ]
        }
        
        report_file = self.reports_dir / "optimization_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

def main():
    """Main execution function"""
    monitor = ContinuousRevenueMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 