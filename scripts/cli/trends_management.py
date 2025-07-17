#!/usr/bin/env python3
"""
Consumer Trends Management CLI

Command-line interface for managing Consumer Trends Integration in production.
"""

import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

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

class TrendsManager:
    """CLI manager for Consumer Trends Integration."""
    
    def __init__(self):
        self.config_path = Path("config/consumer_trends_production.json")
        self.data_manager = None
        self.trend_analyzer = None
        self.personalization_engine = None
        self.signal_listener = None
        
        # Load configuration
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
    
    async def initialize_services(self) -> None:
        """Initialize Consumer Trends services."""
        # Initialize data manager
        self.data_manager = DataManager(
            storage_type=self.config["storage"]["type"],
            bucket_name=self.config["storage"]["bucket"],
            region=self.config["storage"]["region"]
        )
        
        # Initialize trend analyzer
        self.trend_analyzer = PredictiveTrendAnalyzer(
            data_manager=self.data_manager,
            config=self.config["trend_analysis"]
        )
        
        # Initialize personalization engine
        self.personalization_engine = PersonalizationEngine(
            data_manager=self.data_manager,
            config=self.config["personalization"]
        )
        
        # Initialize signal listener
        self.signal_listener = SignalListener(
            data_manager=self.data_manager,
            config=self.config["signal_monitoring"]
        )
    
    async def cmd_status(self) -> None:
        """Show system status."""
        print("🔍 Consumer Trends Integration Status")
        print("=" * 50)
        
        try:
            await self.initialize_services()
            
            # Check trend analyzer status
            trends = await self.trend_analyzer.analyze_all_trends()
            print(f"📊 Active Trends: {len(trends)}")
            
            # Check personalization status
            segments = await self.personalization_engine.generate_user_segments()
            print(f"🎯 User Segments: {len(segments)}")
            
            # Check signal monitoring status
            signals = await self.signal_listener.monitor_signals()
            print(f"🔍 Active Signals: {len(signals)}")
            
            # Show recent activity
            await self.show_recent_activity()
            
        except Exception as e:
            print(f"❌ Status check failed: {e}")
    
    async def show_recent_activity(self) -> None:
        """Show recent system activity."""
        print("\n📈 Recent Activity:")
        print("-" * 30)
        
        try:
            # Get recent trend analysis results
            trend_files = await self.data_manager.list_data("trend_analysis/")
            if trend_files:
                latest_trend = sorted(trend_files)[-1]
                trend_data = await self.data_manager.load_data(latest_trend)
                print(f"📊 Last Trend Analysis: {trend_data.get('timestamp', 'Unknown')}")
                print(f"   Trends Found: {len(trend_data.get('trends', []))}")
            
            # Get recent personalization data
            personalization_files = await self.data_manager.list_data("personalization/")
            if personalization_files:
                latest_personalization = sorted(personalization_files)[-1]
                personalization_data = await self.data_manager.load_data(latest_personalization)
                print(f"🎯 Last Personalization: {personalization_data.get('timestamp', 'Unknown')}")
                print(f"   Segments Created: {len(personalization_data.get('segments', []))}")
            
        except Exception as e:
            print(f"   Unable to load recent activity: {e}")
    
    async def cmd_analyze(self, args) -> None:
        """Run trend analysis."""
        print("📊 Running Consumer Trends Analysis...")
        
        try:
            await self.initialize_services()
            
            # Run analysis
            trends = await self.trend_analyzer.analyze_all_trends()
            insights = await self.trend_analyzer.generate_insights(trends)
            
            # Display results
            print(f"\n✅ Analysis Complete: {len(trends)} trends found")
            print("\n📈 Top Trends:")
            print("-" * 40)
            
            # Sort by priority
            sorted_trends = sorted(trends, key=lambda x: x.get("priority", 0), reverse=True)
            
            for i, trend in enumerate(sorted_trends[:10], 1):
                print(f"{i}. {trend.get('name', 'Unknown')}")
                print(f"   Priority: {trend.get('priority', 0):.2f}")
                print(f"   Confidence: {trend.get('confidence', 0):.2f}")
                print(f"   Source: {trend.get('source', 'Unknown')}")
                print()
            
            # Save results
            timestamp = datetime.now().isoformat()
            results = {
                "timestamp": timestamp,
                "trends": trends,
                "insights": insights
            }
            
            await self.data_manager.save_data(
                f"trend_analysis/{timestamp}.json",
                results
            )
            
            print(f"💾 Results saved to trend_analysis/{timestamp}.json")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    async def cmd_personalize(self, args) -> None:
        """Run personalization analysis."""
        print("🎯 Running Personalization Analysis...")
        
        try:
            await self.initialize_services()
            
            # Generate user segments
            segments = await self.personalization_engine.generate_user_segments()
            
            # Create content variations
            variations = await self.personalization_engine.create_content_variations()
            
            # Display results
            print(f"\n✅ Personalization Complete: {len(segments)} segments created")
            print("\n👥 User Segments:")
            print("-" * 30)
            
            for i, segment in enumerate(segments[:5], 1):
                print(f"{i}. {segment.get('name', 'Unknown')}")
                print(f"   Size: {segment.get('size', 0)} users")
                print(f"   Interests: {', '.join(segment.get('interests', [])[:3])}")
                print()
            
            print(f"\n📝 Content Variations: {len(variations)} created")
            
            # Save results
            timestamp = datetime.now().isoformat()
            results = {
                "timestamp": timestamp,
                "segments": segments,
                "variations": variations
            }
            
            await self.data_manager.save_data(
                f"personalization/{timestamp}.json",
                results
            )
            
            print(f"💾 Results saved to personalization/{timestamp}.json")
            
        except Exception as e:
            print(f"❌ Personalization failed: {e}")
    
    async def cmd_monitor(self, args) -> None:
        """Monitor signals."""
        print("🔍 Starting Signal Monitoring...")
        
        try:
            await self.initialize_services()
            
            # Start monitoring
            await self.signal_listener.start_monitoring()
            
            print("✅ Signal monitoring started")
            print("Press Ctrl+C to stop monitoring")
            
            # Keep monitoring running
            while True:
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping signal monitoring...")
            await self.signal_listener.stop_monitoring()
            print("✅ Signal monitoring stopped")
        except Exception as e:
            print(f"❌ Signal monitoring failed: {e}")
    
    async def cmd_report(self, args) -> None:
        """Generate comprehensive report."""
        print("📋 Generating Consumer Trends Report...")
        
        try:
            await self.initialize_services()
            
            # Collect data
            trends = await self.trend_analyzer.analyze_all_trends()
            segments = await self.personalization_engine.generate_user_segments()
            signals = await self.signal_listener.monitor_signals()
            
            # Generate report
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_trends": len(trends),
                    "total_segments": len(segments),
                    "active_signals": len(signals),
                    "high_priority_trends": len([t for t in trends if t.get("priority", 0) > 0.8])
                },
                "top_trends": sorted(trends, key=lambda x: x.get("priority", 0), reverse=True)[:10],
                "user_segments": segments[:5],
                "recommendations": await self.generate_recommendations(trends, segments)
            }
            
            # Display report
            print("\n📊 Consumer Trends Report")
            print("=" * 50)
            print(f"Generated: {report['generated_at']}")
            print(f"Total Trends: {report['summary']['total_trends']}")
            print(f"User Segments: {report['summary']['total_segments']}")
            print(f"Active Signals: {report['summary']['active_signals']}")
            print(f"High Priority Trends: {report['summary']['high_priority_trends']}")
            
            print("\n🏆 Top Trends:")
            print("-" * 30)
            for i, trend in enumerate(report['top_trends'][:5], 1):
                print(f"{i}. {trend.get('name', 'Unknown')} (Priority: {trend.get('priority', 0):.2f})")
            
            print("\n💡 Recommendations:")
            print("-" * 30)
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"{i}. {rec}")
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = f"reports/consumer_trends_report_{timestamp}.json"
            
            await self.data_manager.save_data(report_path, report)
            print(f"\n💾 Report saved to {report_path}")
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
    
    async def generate_recommendations(self, trends: List[Dict], segments: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # High priority trend recommendations
        high_priority_trends = [t for t in trends if t.get("priority", 0) > 0.8]
        if high_priority_trends:
            recommendations.append(f"Focus on {len(high_priority_trends)} high-priority trends for immediate content creation")
        
        # Market opportunity recommendations
        emerging_trends = [t for t in trends if t.get("growth_rate", 0) > 0.5]
        if emerging_trends:
            recommendations.append(f"Monitor {len(emerging_trends)} emerging trends for future opportunities")
        
        # Personalization recommendations
        if len(segments) > 5:
            recommendations.append("Consider creating targeted content for specific user segments")
        
        # Competition recommendations
        low_competition_trends = [t for t in trends if t.get("competition", "high") == "low"]
        if low_competition_trends:
            recommendations.append(f"Explore {len(low_competition_trends)} low-competition niches")
        
        return recommendations
    
    async def cmd_deploy(self, args) -> None:
        """Deploy Consumer Trends Integration."""
        print("🚀 Deploying Consumer Trends Integration...")
        
        try:
            # Import deployment script
            from scripts.deploy_consumer_trends import ConsumerTrendsDeployer
            
            deployer = ConsumerTrendsDeployer()
            success = await deployer.deploy()
            
            if success:
                print("✅ Consumer Trends Integration deployed successfully!")
            else:
                print("❌ Deployment failed")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Consumer Trends Integration Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    subparsers.add_parser("status", help="Show system status")
    
    # Analyze command
    subparsers.add_parser("analyze", help="Run trend analysis")
    
    # Personalize command
    subparsers.add_parser("personalize", help="Run personalization analysis")
    
    # Monitor command
    subparsers.add_parser("monitor", help="Monitor signals")
    
    # Report command
    subparsers.add_parser("report", help="Generate comprehensive report")
    
    # Deploy command
    subparsers.add_parser("deploy", help="Deploy Consumer Trends Integration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create manager and run command
    manager = TrendsManager()
    
    if args.command == "status":
        asyncio.run(manager.cmd_status())
    elif args.command == "analyze":
        asyncio.run(manager.cmd_analyze(args))
    elif args.command == "personalize":
        asyncio.run(manager.cmd_personalize(args))
    elif args.command == "monitor":
        asyncio.run(manager.cmd_monitor(args))
    elif args.command == "report":
        asyncio.run(manager.cmd_report(args))
    elif args.command == "deploy":
        asyncio.run(manager.cmd_deploy(args))

if __name__ == "__main__":
    main() 