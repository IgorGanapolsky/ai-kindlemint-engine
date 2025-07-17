#!/usr/bin/env python3
"""
Consumer Trends Integration Production Deployment Script

This script deploys the Consumer Trends Integration system for production use,
including environment validation, API key setup, and service initialization.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.intelligence.predictive_trend_analyzer import PredictiveTrendAnalyzer
from kindlemint.marketing.personalization_engine import PersonalizationEngine
from kindlemint.agents.signal_listener import SignalListener
from kindlemint.utils.data_manager import DataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsumerTrendsDeployer:
    """Production deployment orchestrator for Consumer Trends Integration."""
    
    def __init__(self):
        self.config_path = Path("config/consumer_trends_production.json")
        self.env_file = Path(".env")
        self.required_apis = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "TIKTOK_ACCESS_TOKEN",
            "GOOGLE_TRENDS_API_KEY",
            "AMAZON_PRODUCT_API_KEY",
            "AMAZON_PRODUCT_SECRET"
        ]
        
    def validate_environment(self) -> bool:
        """Validate that all required environment variables are set."""
        logger.info("🔍 Validating production environment...")
        
        missing_vars = []
        for var in self.required_apis:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("💡 Please set these in your .env file or environment")
            return False
        
        logger.info("✅ Environment validation passed")
        return True
    
    def create_production_config(self) -> Dict:
        """Create production configuration for Consumer Trends Integration."""
        config = {
            "trend_analysis": {
                "enabled": True,
                "update_frequency_minutes": 30,
                "max_concurrent_analyses": 5,
                "data_retention_days": 90,
                "confidence_threshold": 0.75
            },
            "personalization": {
                "enabled": True,
                "user_segment_count": 10,
                "content_variation_count": 5,
                "a_b_testing_enabled": True
            },
            "signal_monitoring": {
                "enabled": True,
                "check_interval_seconds": 300,
                "alert_threshold": 0.8,
                "webhook_url": os.getenv("WEBHOOK_URL", ""),
                "slack_webhook": os.getenv("SLACK_WEBHOOK", "")
            },
            "apis": {
                "reddit": {
                    "subreddits": [
                        "books", "Kindle", "amazon", "reading", "booktok",
                        "puzzles", "crosswords", "sudoku", "wordsearch"
                    ],
                    "post_limit": 100,
                    "time_filter": "week"
                },
                "tiktok": {
                    "hashtags": [
                        "#booktok", "#kindle", "#amazon", "#reading",
                        "#puzzles", "#crosswords", "#sudoku", "#wordsearch"
                    ],
                    "video_limit": 50
                },
                "google_trends": {
                    "keywords": [
                        "kindle books", "puzzle books", "crossword books",
                        "sudoku books", "word search books", "activity books"
                    ],
                    "geo": "US",
                    "time_range": "30d"
                },
                "amazon": {
                    "categories": [
                        "Books > Children's Books > Activities, Crafts & Games",
                        "Books > Education & Teaching > Schools & Teaching",
                        "Books > Reference > Words, Language & Grammar"
                    ],
                    "max_results": 100
                }
            },
            "storage": {
                "type": "s3" if os.getenv("AWS_ACCESS_KEY_ID") else "local",
                "bucket": os.getenv("S3_BUCKET", "kindlemint-trends"),
                "region": os.getenv("AWS_REGION", "us-east-1")
            },
            "notifications": {
                "email": os.getenv("ALERT_EMAIL", ""),
                "slack": os.getenv("SLACK_WEBHOOK", ""),
                "discord": os.getenv("DISCORD_WEBHOOK", "")
            }
        }
        
        # Save configuration
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ Production config created: {self.config_path}")
        return config
    
    async def initialize_services(self, config: Dict) -> Dict:
        """Initialize all Consumer Trends services."""
        logger.info("🚀 Initializing Consumer Trends services...")
        
        # Initialize data manager
        data_manager = DataManager(
            storage_type=config["storage"]["type"],
            bucket_name=config["storage"]["bucket"],
            region=config["storage"]["region"]
        )
        
        # Initialize trend analyzer
        trend_analyzer = PredictiveTrendAnalyzer(
            data_manager=data_manager,
            config=config["trend_analysis"]
        )
        
        # Initialize personalization engine
        personalization_engine = PersonalizationEngine(
            data_manager=data_manager,
            config=config["personalization"]
        )
        
        # Initialize signal listener
        signal_listener = SignalListener(
            data_manager=data_manager,
            config=config["signal_monitoring"]
        )
        
        logger.info("✅ All services initialized successfully")
        
        return {
            "trend_analyzer": trend_analyzer,
            "personalization_engine": personalization_engine,
            "signal_listener": signal_listener,
            "data_manager": data_manager
        }
    
    async def run_initial_analysis(self, services: Dict) -> None:
        """Run initial trend analysis to populate the system."""
        logger.info("📊 Running initial trend analysis...")
        
        try:
            # Run comprehensive trend analysis
            trends = await services["trend_analyzer"].analyze_all_trends()
            
            # Generate initial personalization data
            await services["personalization_engine"].generate_user_segments()
            
            # Start signal monitoring
            await services["signal_listener"].start_monitoring()
            
            logger.info(f"✅ Initial analysis complete: {len(trends)} trends identified")
            
        except Exception as e:
            logger.error(f"❌ Initial analysis failed: {e}")
            raise
    
    def create_systemd_service(self) -> None:
        """Create systemd service file for production deployment."""
        service_content = f"""[Unit]
Description=KindleMint Consumer Trends Integration
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={Path.cwd()}
Environment=PATH={os.getenv('PATH')}
ExecStart=/usr/bin/python3 {Path.cwd()}/scripts/run_consumer_trends_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/etc/systemd/system/kindlemint-trends.service")
        if service_path.parent.exists():
            with open(service_path, 'w') as f:
                f.write(service_content)
            logger.info(f"✅ Systemd service created: {service_path}")
        else:
            logger.warning("⚠️  Cannot create systemd service (not running as root)")
    
    def create_docker_compose(self) -> None:
        """Create Docker Compose configuration for containerized deployment."""
        compose_content = """version: '3.8'

services:
  kindlemint-trends:
    build:
      context: .
      dockerfile: Dockerfile.trends
    environment:
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - TIKTOK_ACCESS_TOKEN=${TIKTOK_ACCESS_TOKEN}
      - GOOGLE_TRENDS_API_KEY=${GOOGLE_TRENDS_API_KEY}
      - AMAZON_PRODUCT_API_KEY=${AMAZON_PRODUCT_API_KEY}
      - AMAZON_PRODUCT_SECRET=${AMAZON_PRODUCT_SECRET}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - S3_BUCKET=${S3_BUCKET}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
        
        compose_path = Path("docker-compose.trends.yml")
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        
        logger.info(f"✅ Docker Compose config created: {compose_path}")
    
    def create_monitoring_dashboard(self) -> None:
        """Create monitoring dashboard configuration."""
        dashboard_config = {
            "title": "KindleMint Consumer Trends Dashboard",
            "refresh_interval": 300,
            "panels": [
                {
                    "title": "Trend Analysis Status",
                    "type": "stat",
                    "targets": ["trend_analyzer.health", "trend_analyzer.active_trends"]
                },
                {
                    "title": "Personalization Metrics",
                    "type": "graph",
                    "targets": ["personalization.user_segments", "personalization.content_variations"]
                },
                {
                    "title": "Signal Monitoring",
                    "type": "alert",
                    "targets": ["signal_listener.alerts", "signal_listener.response_time"]
                }
            ]
        }
        
        dashboard_path = Path("config/trends_dashboard.json")
        dashboard_path.parent.mkdir(exist_ok=True)
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
        
        logger.info(f"✅ Monitoring dashboard config created: {dashboard_path}")
    
    async def deploy(self) -> bool:
        """Main deployment orchestration."""
        logger.info("🚀 Starting Consumer Trends Integration deployment...")
        
        try:
            # Step 1: Validate environment
            if not self.validate_environment():
                return False
            
            # Step 2: Create production configuration
            config = self.create_production_config()
            
            # Step 3: Initialize services
            services = await self.initialize_services(config)
            
            # Step 4: Run initial analysis
            await self.run_initial_analysis(services)
            
            # Step 5: Create deployment artifacts
            self.create_systemd_service()
            self.create_docker_compose()
            self.create_monitoring_dashboard()
            
            logger.info("🎉 Consumer Trends Integration deployed successfully!")
            logger.info("📋 Next steps:")
            logger.info("   1. Start the service: sudo systemctl start kindlemint-trends")
            logger.info("   2. Enable auto-start: sudo systemctl enable kindlemint-trends")
            logger.info("   3. Check status: sudo systemctl status kindlemint-trends")
            logger.info("   4. View logs: sudo journalctl -u kindlemint-trends -f")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False

async def main():
    """Main deployment entry point."""
    deployer = ConsumerTrendsDeployer()
    success = await deployer.deploy()
    
    if success:
        print("\n🎉 Consumer Trends Integration is now production-ready!")
        print("📊 The system will automatically:")
        print("   • Monitor trends across Reddit, TikTok, Google Trends, and Amazon")
        print("   • Generate personalized content recommendations")
        print("   • Alert you to emerging opportunities")
        print("   • Scale across multiple niches for maximum market coverage")
    else:
        print("\n❌ Deployment failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 