#!/usr/bin/env python3
"""
Daily Market Insights Runner
Orchestrates all market research activities and ensures data freshness
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.reddit_market_scraper import RedditMarketScraper
from scripts.orchestration.market_insights_orchestrator import MarketInsightsOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyMarketInsightsRunner:
    """Runs all market research activities in sequence"""
    
    def __init__(self):
        self.data_dir = Path('data/market-insights')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_daily_collection(self):
        """Run the complete daily market insights collection"""
        logger.info("🌅 Starting Daily Market Insights Collection")
        logger.info("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'steps': {}
        }
        
        try:
            # Step 1: Reddit Market Scraper
            logger.info("\n📱 Step 1: Reddit Market Research")
            reddit_success = await self.run_reddit_scraper()
            results['steps']['reddit'] = {
                'status': 'success' if reddit_success else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 2: Market Insights Orchestrator
            logger.info("\n🎯 Step 2: Market Insights Orchestration")
            orchestration_success = await self.run_market_orchestrator()
            results['steps']['orchestration'] = {
                'status': 'success' if orchestration_success else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 3: Generate Daily Summary
            logger.info("\n📊 Step 3: Generating Daily Summary")
            summary_success = await self.generate_daily_summary()
            results['steps']['summary'] = {
                'status': 'success' if summary_success else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Overall status
            all_success = all(
                step['status'] == 'success' 
                for step in results['steps'].values()
            )
            results['overall_status'] = 'success' if all_success else 'partial_failure'
            
            # Save run results
            self.save_run_results(results)
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Daily Market Insights Collection Complete!")
            logger.info(f"📊 Overall Status: {results['overall_status']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Critical error in daily collection: {e}")
            results['overall_status'] = 'failed'
            results['error'] = str(e)
            self.save_run_results(results)
            raise
    
    async def run_reddit_scraper(self) -> bool:
        """Run Reddit market scraper"""
        try:
            scraper = RedditMarketScraper()
            insights = scraper.collect_market_insights()
            scraper.save_insights(insights)
            
            logger.info(f"✅ Reddit scraper completed: {insights['summary']['total_posts_analyzed']} posts analyzed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Reddit scraper failed: {e}")
            return False
    
    async def run_market_orchestrator(self) -> bool:
        """Run the main market insights orchestrator"""
        try:
            orchestrator = MarketInsightsOrchestrator()
            insights = await orchestrator.collect_all_insights()
            orchestrator.save_insights(insights)
            
            logger.info(f"✅ Market orchestration completed: {len(insights['recommendations'])} recommendations generated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Market orchestration failed: {e}")
            return False
    
    async def generate_daily_summary(self) -> bool:
        """Generate consolidated daily summary"""
        try:
            summary_path = self.data_dir / 'daily_summary.json'
            
            # Load today's data
            today = datetime.now().strftime('%Y%m%d')
            reddit_file = self.data_dir / f"reddit_insights_{today}.json"
            
            summary = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().isoformat(),
                'data_sources': [],
                'key_findings': [],
                'action_items': []
            }
            
            # Add Reddit findings
            if reddit_file.exists():
                with open(reddit_file, 'r') as f:
                    reddit_data = json.load(f)
                    summary['data_sources'].append('reddit')
                    
                    # Extract key findings
                    if reddit_data.get('top_keywords'):
                        top_keyword = list(reddit_data['top_keywords'].keys())[0]
                        summary['key_findings'].append(
                            f"Top trending keyword: {top_keyword}"
                        )
            
            # Add orchestrator findings
            exec_summary = self.reports_dir / f"executive_summary_{today}.md"
            if exec_summary.exists():
                summary['data_sources'].append('market_orchestrator')
            
            # Check data freshness
            summary['data_freshness'] = {
                'reddit': 'fresh' if 'reddit' in summary['data_sources'] else 'stale',
                'trends': 'fresh' if 'market_orchestrator' in summary['data_sources'] else 'stale'
            }
            
            # Save summary
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info("✅ Daily summary generated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            return False
    
    def save_run_results(self, results: Dict):
        """Save results of this run for monitoring"""
        run_history_file = self.data_dir / 'run_history.json'
        
        # Load existing history
        if run_history_file.exists():
            with open(run_history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add this run
        history.append(results)
        
        # Keep last 30 runs
        history = history[-30:]
        
        with open(run_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    @property
    def reports_dir(self):
        """Get reports directory"""
        return Path('reports/market-insights')


async def main():
    """Main entry point"""
    runner = DailyMarketInsightsRunner()
    
    try:
        results = await runner.run_daily_collection()
        
        # Exit code based on status
        if results['overall_status'] == 'success':
            return 0
        elif results['overall_status'] == 'partial_failure':
            return 1
        else:
            return 2
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)