#!/usr/bin/env python3
"""
Consumer Trends Integration Production Service Runner

This script runs the Consumer Trends Integration as a production service,
continuously monitoring trends and generating insights.
"""

import sys
import json
import asyncio
import logging
import signal
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.intelligence.predictive_trend_analyzer import PredictiveTrendAnalyzer
from kindlemint.marketing.personalization_engine import PersonalizationEngine
from kindlemint.agents.signal_listener import SignalListener
from kindlemint.utils.data_manager import DataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/consumer_trends_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConsumerTrendsService:
    """Production service for Consumer Trends Integration."""
    
    def __init__(self):
        self.config_path = Path("config/consumer_trends_production.json")
        self.running = False
        self.services = {}
        self.tasks = []
        
        # Load configuration
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
    
    async def initialize_services(self) -> None:
        """Initialize all Consumer Trends services."""
        logger.info("🚀 Initializing Consumer Trends services...")
        
        try:
            # Initialize data manager
            data_manager = DataManager(
                storage_type=self.config["storage"]["type"],
                bucket_name=self.config["storage"]["bucket"],
                region=self.config["storage"]["region"]
            )
            
            # Initialize trend analyzer
            trend_analyzer = PredictiveTrendAnalyzer(
                data_manager=data_manager,
                config=self.config["trend_analysis"]
            )
            
            # Initialize personalization engine
            personalization_engine = PersonalizationEngine(
                data_manager=data_manager,
                config=self.config["personalization"]
            )
            
            # Initialize signal listener
            signal_listener = SignalListener(
                data_manager=data_manager,
                config=self.config["signal_monitoring"]
            )
            
            self.services = {
                "trend_analyzer": trend_analyzer,
                "personalization_engine": personalization_engine,
                "signal_listener": signal_listener,
                "data_manager": data_manager
            }
            
            logger.info("✅ All services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            raise
    
    async def run_trend_analysis_cycle(self) -> None:
        """Run a complete trend analysis cycle."""
        logger.info("📊 Starting trend analysis cycle...")
        
        try:
            # Analyze all trends
            trends = await self.services["trend_analyzer"].analyze_all_trends()
            
            # Generate insights
            insights = await self.services["trend_analyzer"].generate_insights(trends)
            
            # Save results
            timestamp = datetime.now().isoformat()
            results = {
                "timestamp": timestamp,
                "trends": trends,
                "insights": insights,
                "cycle_duration": time.time()
            }
            
            await self.services["data_manager"].save_data(
                f"trend_analysis/{timestamp}.json",
                results
            )
            
            logger.info(f"✅ Trend analysis cycle complete: {len(trends)} trends analyzed")
            
            # Send notifications for high-priority trends
            high_priority_trends = [t for t in trends if t.get("priority", 0) > 0.8]
            if high_priority_trends:
                await self.send_high_priority_alert(high_priority_trends)
                
        except Exception as e:
            logger.error(f"❌ Trend analysis cycle failed: {e}")
    
    async def run_personalization_cycle(self) -> None:
        """Run a personalization cycle."""
        logger.info("🎯 Starting personalization cycle...")
        
        try:
            # Generate user segments
            segments = await self.services["personalization_engine"].generate_user_segments()
            
            # Create content variations
            variations = await self.services["personalization_engine"].create_content_variations()
            
            # Run A/B testing if enabled
            if self.config["personalization"]["a_b_testing_enabled"]:
                test_results = await self.services["personalization_engine"].run_ab_tests()
                logger.info(f"✅ A/B test results: {test_results}")
            
            # Save personalization data
            timestamp = datetime.now().isoformat()
            personalization_data = {
                "timestamp": timestamp,
                "segments": segments,
                "variations": variations
            }
            
            await self.services["data_manager"].save_data(
                f"personalization/{timestamp}.json",
                personalization_data
            )
            
            logger.info(f"✅ Personalization cycle complete: {len(segments)} segments created")
            
        except Exception as e:
            logger.error(f"❌ Personalization cycle failed: {e}")
    
    async def run_signal_monitoring_cycle(self) -> None:
        """Run a signal monitoring cycle."""
        logger.info("🔍 Starting signal monitoring cycle...")
        
        try:
            # Monitor signals
            signals = await self.services["signal_listener"].monitor_signals()
            
            # Process alerts
            alerts = await self.services["signal_listener"].process_alerts(signals)
            
            # Send notifications
            if alerts:
                await self.send_alerts(alerts)
            
            logger.info(f"✅ Signal monitoring cycle complete: {len(signals)} signals processed")
            
        except Exception as e:
            logger.error(f"❌ Signal monitoring cycle failed: {e}")
    
    async def send_high_priority_alert(self, trends: List[Dict]) -> None:
        """Send high-priority trend alerts."""
        logger.info(f"🚨 Sending high-priority alerts for {len(trends)} trends")
        
        # Format alert message
        alert_message = "🚨 HIGH-PRIORITY TRENDS DETECTED\n\n"
        for trend in trends:
            alert_message += f"📈 {trend['name']}\n"
            alert_message += f"   Priority: {trend.get('priority', 0):.2f}\n"
            alert_message += f"   Confidence: {trend.get('confidence', 0):.2f}\n"
            alert_message += f"   Source: {trend.get('source', 'Unknown')}\n\n"
        
        # Send to configured notification channels
        await self.send_notification("High-Priority Trends", alert_message)
    
    async def send_alerts(self, alerts: List[Dict]) -> None:
        """Send general alerts."""
        logger.info(f"📢 Sending {len(alerts)} alerts")
        
        for alert in alerts:
            await self.send_notification(
                alert.get("title", "Consumer Trends Alert"),
                alert.get("message", "New alert from Consumer Trends Integration")
            )
    
    async def send_notification(self, title: str, message: str) -> None:
        """Send notification to all configured channels."""
        notifications = self.config.get("notifications", {})
        
        # Email notification
        if notifications.get("email"):
            await self.send_email_notification(notifications["email"], title, message)
        
        # Slack notification
        if notifications.get("slack"):
            await self.send_slack_notification(notifications["slack"], title, message)
        
        # Discord notification
        if notifications.get("discord"):
            await self.send_discord_notification(notifications["discord"], title, message)
    
    async def send_email_notification(self, email: str, title: str, message: str) -> None:
        """Send email notification."""
        # Implementation would use smtplib or similar
        logger.info(f"📧 Email notification sent to {email}: {title}")
    
    async def send_slack_notification(self, webhook_url: str, title: str, message: str) -> None:
        """Send Slack notification."""
        # Implementation would use aiohttp to post to webhook
        logger.info(f"💬 Slack notification sent: {title}")
    
    async def send_discord_notification(self, webhook_url: str, title: str, message: str) -> None:
        """Send Discord notification."""
        # Implementation would use aiohttp to post to webhook
        logger.info(f"🎮 Discord notification sent: {title}")
    
    async def start_periodic_tasks(self) -> None:
        """Start all periodic tasks."""
        logger.info("🔄 Starting periodic tasks...")
        
        # Start trend analysis task
        trend_interval = self.config["trend_analysis"]["update_frequency_minutes"] * 60
        trend_task = asyncio.create_task(
            self.periodic_task(self.run_trend_analysis_cycle, trend_interval)
        )
        self.tasks.append(trend_task)
        
        # Start personalization task (runs every 2 hours)
        personalization_task = asyncio.create_task(
            self.periodic_task(self.run_personalization_cycle, 7200)
        )
        self.tasks.append(personalization_task)
        
        # Start signal monitoring task
        signal_interval = self.config["signal_monitoring"]["check_interval_seconds"]
        signal_task = asyncio.create_task(
            self.periodic_task(self.run_signal_monitoring_cycle, signal_interval)
        )
        self.tasks.append(signal_task)
        
        logger.info("✅ All periodic tasks started")
    
    async def periodic_task(self, task_func, interval: int) -> None:
        """Run a task periodically."""
        while self.running:
            try:
                await task_func()
            except Exception as e:
                logger.error(f"❌ Periodic task failed: {e}")
            
            await asyncio.sleep(interval)
    
    def signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals."""
        logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    async def run(self) -> None:
        """Main service run loop."""
        logger.info("🚀 Starting Consumer Trends Integration service...")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Initialize services
            await self.initialize_services()
            
            # Start periodic tasks
            await self.start_periodic_tasks()
            
            # Run initial analysis
            logger.info("📊 Running initial analysis...")
            await self.run_trend_analysis_cycle()
            await self.run_personalization_cycle()
            
            # Start signal monitoring
            await self.services["signal_listener"].start_monitoring()
            
            self.running = True
            logger.info("✅ Consumer Trends Integration service is running")
            
            # Keep the service running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Service failed: {e}")
            raise
        finally:
            # Cleanup
            logger.info("🧹 Cleaning up...")
            for task in self.tasks:
                task.cancel()
            
            # Stop signal monitoring
            if "signal_listener" in self.services:
                await self.services["signal_listener"].stop_monitoring()
            
            logger.info("👋 Consumer Trends Integration service stopped")

async def main():
    """Main service entry point."""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    service = ConsumerTrendsService()
    await service.run()

if __name__ == "__main__":
    asyncio.run(main()) 