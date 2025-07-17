#!/usr/bin/env python3
"""
Traffic Generation Orchestrator
Coordinates all traffic generation methods to drive visitors to landing page

Goal: Generate 1000+ daily visitors to achieve $300/day revenue
"""

import os
import sys
import json
import time
import schedule
import logging
from datetime import datetime
from typing import Dict

# Import our traffic modules
from reddit_organic_poster import RedditOrganicPoster
from pinterest_pin_scheduler import PinterestPinScheduler
from facebook_group_engager import FacebookGroupEngager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TrafficOrchestrator:
    def __init__(self):
        """Initialize traffic orchestrator"""
        self.landing_page_url = "https://dvdyff0b2oove.cloudfront.net"
        self.config = self.load_or_create_config()
        
        # Initialize traffic sources if configured
        self.reddit_bot = None
        self.pinterest_scheduler = None
        self.facebook_engager = None
        
        self.initialize_traffic_sources()
        
    def load_or_create_config(self) -> Dict:
        """Load or create orchestrator configuration"""
        config_path = "traffic_orchestrator_config.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "enabled_sources": {
                    "reddit": False,
                    "pinterest": False,
                    "facebook": False
                },
                "schedule": {
                    "reddit": ["09:00", "14:00", "19:00"],
                    "pinterest": ["08:00", "11:00", "14:00", "17:00", "20:00"],
                    "facebook": ["10:00", "16:00"]
                },
                "daily_goals": {
                    "visitors": 1000,
                    "email_signups": 250,
                    "conversions": 25
                },
                "metrics_webhook": None  # Optional Slack/Discord webhook
            }
            
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default config at {config_path}")
            return default_config
    
    def initialize_traffic_sources(self):
        """Initialize enabled traffic sources"""
        if self.config["enabled_sources"]["reddit"]:
            if os.path.exists("reddit_config.json"):
                self.reddit_bot = RedditOrganicPoster()
                logger.info("✅ Reddit bot initialized")
            else:
                logger.warning("❌ Reddit config not found")
        
        if self.config["enabled_sources"]["pinterest"]:
            if os.path.exists("pinterest_config.json"):
                self.pinterest_scheduler = PinterestPinScheduler()
                logger.info("✅ Pinterest scheduler initialized")
            else:
                logger.warning("❌ Pinterest config not found")
        
        if self.config["enabled_sources"]["facebook"]:
            if os.path.exists("facebook_config.json"):
                self.facebook_engager = FacebookGroupEngager()
                logger.info("✅ Facebook engager initialized")
            else:
                logger.warning("❌ Facebook config not found")
    
    def run_reddit_routine(self):
        """Run Reddit posting routine"""
        if not self.reddit_bot:
            logger.warning("Reddit bot not initialized")
            return
        
        logger.info("🔴 Starting Reddit routine...")
        try:
            self.reddit_bot.run_daily_routine()
            logger.info("✅ Reddit routine completed")
        except Exception as e:
            logger.error(f"❌ Reddit routine failed: {e}")
    
    def run_pinterest_routine(self):
        """Run Pinterest pinning routine"""
        if not self.pinterest_scheduler:
            logger.warning("Pinterest scheduler not initialized")
            return
        
        logger.info("📌 Starting Pinterest routine...")
        try:
            self.pinterest_scheduler.schedule_daily_pins()
            logger.info("✅ Pinterest routine completed")
        except Exception as e:
            logger.error(f"❌ Pinterest routine failed: {e}")
    
    def run_facebook_routine(self):
        """Run Facebook engagement routine"""
        if not self.facebook_engager:
            logger.warning("Facebook engager not initialized")
            return
        
        logger.info("📘 Starting Facebook routine...")
        try:
            self.facebook_engager.run_daily_engagement()
            logger.info("✅ Facebook routine completed")
        except Exception as e:
            logger.error(f"❌ Facebook routine failed: {e}")
    
    def calculate_daily_metrics(self) -> Dict:
        """Calculate estimated daily metrics from all sources"""
        metrics = {
            "date": datetime.now().isoformat(),
            "estimated_reach": 0,
            "estimated_visitors": 0,
            "sources": {}
        }
        
        # Reddit metrics
        if os.path.exists("reddit_metrics.json"):
            with open("reddit_metrics.json", 'r') as f:
                reddit_data = json.load(f)
                if reddit_data:
                    latest = reddit_data[-1]
                    metrics["sources"]["reddit"] = latest.get("estimated_reach", 0)
                    metrics["estimated_reach"] += latest.get("estimated_reach", 0)
        
        # Pinterest metrics
        if os.path.exists("pinterest_metrics.json"):
            with open("pinterest_metrics.json", 'r') as f:
                pinterest_data = json.load(f)
                if pinterest_data:
                    latest = pinterest_data[-1]
                    metrics["sources"]["pinterest"] = latest.get("estimated_impressions", 0)
                    metrics["estimated_reach"] += latest.get("estimated_impressions", 0)
        
        # Facebook metrics
        if os.path.exists("facebook_metrics.json"):
            with open("facebook_metrics.json", 'r') as f:
                facebook_data = json.load(f)
                if facebook_data:
                    latest = facebook_data[-1]
                    metrics["sources"]["facebook"] = latest.get("estimated_reach", 0)
                    metrics["estimated_reach"] += latest.get("estimated_reach", 0)
        
        # Estimate visitors (conservative 2% CTR)
        metrics["estimated_visitors"] = int(metrics["estimated_reach"] * 0.02)
        
        # Estimate conversions (25% email capture, 10% purchase)
        metrics["estimated_signups"] = int(metrics["estimated_visitors"] * 0.25)
        metrics["estimated_sales"] = int(metrics["estimated_signups"] * 0.10)
        metrics["estimated_revenue"] = metrics["estimated_sales"] * 4.99  # $4.99 per sale
        
        return metrics
    
    def send_daily_report(self):
        """Send daily metrics report"""
        metrics = self.calculate_daily_metrics()
        
        report = f"""
📊 Daily Traffic Generation Report
==================================
Date: {datetime.now().strftime('%Y-%m-%d')}

🎯 Landing Page: {self.landing_page_url}

📈 Estimated Metrics:
- Total Reach: {metrics['estimated_reach']:,}
- Estimated Visitors: {metrics['estimated_visitors']:,}
- Email Signups: {metrics['estimated_signups']:,}
- Sales: {metrics['estimated_sales']}
- Revenue: ${metrics['estimated_revenue']:.2f}

📊 By Source:
- Reddit: {metrics['sources'].get('reddit', 0):,} reach
- Pinterest: {metrics['sources'].get('pinterest', 0):,} impressions
- Facebook: {metrics['sources'].get('facebook', 0):,} reach

🎯 Goals:
- Visitors Goal: {self.config['daily_goals']['visitors']:,} ({metrics['estimated_visitors']/self.config['daily_goals']['visitors']*100:.1f}% achieved)
- Revenue Goal: $300 ({metrics['estimated_revenue']/300*100:.1f}% achieved)

💡 Recommendations:
"""
        
        if metrics['estimated_revenue'] < 100:
            report += "- ⚠️ Revenue below target. Increase posting frequency.\n"
            report += "- ⚠️ Consider paid ads to boost traffic.\n"
        
        if metrics['estimated_visitors'] < 500:
            report += "- ⚠️ Low visitor count. Review content quality.\n"
            report += "- ⚠️ Test different headlines and hooks.\n"
        
        logger.info(report)
        
        # Save report
        with open(f"reports/traffic_report_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
            f.write(report)
        
        # Send to webhook if configured
        if self.config.get("metrics_webhook"):
            # Send to Slack/Discord webhook
            pass
    
    def setup_schedule(self):
        """Setup scheduled tasks"""
        # Reddit schedules
        if self.config["enabled_sources"]["reddit"]:
            for time_str in self.config["schedule"]["reddit"]:
                schedule.every().day.at(time_str).do(self.run_reddit_routine)
        
        # Pinterest schedules
        if self.config["enabled_sources"]["pinterest"]:
            for time_str in self.config["schedule"]["pinterest"]:
                schedule.every().day.at(time_str).do(self.run_pinterest_routine)
        
        # Facebook schedules
        if self.config["enabled_sources"]["facebook"]:
            for time_str in self.config["schedule"]["facebook"]:
                schedule.every().day.at(time_str).do(self.run_facebook_routine)
        
        # Daily report at 11 PM
        schedule.every().day.at("23:00").do(self.send_daily_report)
        
        logger.info("📅 Schedule configured")
    
    def run(self):
        """Run the traffic orchestrator"""
        logger.info("🚀 Traffic Orchestrator started!")
        logger.info(f"🎯 Target: {self.landing_page_url}")
        logger.info("💰 Goal: $300/day revenue")
        
        # Setup schedules
        self.setup_schedule()
        
        # Run initial routines
        logger.info("Running initial traffic generation...")
        if self.reddit_bot:
            self.run_reddit_routine()
        if self.pinterest_scheduler:
            self.run_pinterest_routine()
        if self.facebook_engager:
            self.run_facebook_routine()
        
        # Run scheduled tasks
        logger.info("Starting scheduled operations...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Check if any configs exist
    configs_exist = any([
        os.path.exists("reddit_config.json"),
        os.path.exists("pinterest_config.json"),
        os.path.exists("facebook_config.json")
    ])
    
    if not configs_exist:
        print("⚠️  No traffic source configurations found!")
        print("Please configure at least one traffic source:")
        print("- reddit_config.json")
        print("- pinterest_config.json") 
        print("- facebook_config.json")
        print("\nThen enable sources in traffic_orchestrator_config.json")
    else:
        # Run orchestrator
        orchestrator = TrafficOrchestrator()
        orchestrator.run()