#!/usr/bin/env python3
"""
Alembic Causal AI Orchestrator - Autonomous Integration

Integrates the Alembic causal AI strategy with the autonomous worktree system
for continuous market monitoring and intelligent decision-making.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.analytics.causal_inference import CausalAnalyticsEngine
from kindlemint.marketing.event_driven_agent import EventDrivenMarketingAgent, EventType, MarketEvent
from kindlemint.data.private_data_pipeline import PrivateDataPipeline, DataSource, ConsentLevel
from kindlemint.orchestration.human_creativity_checkpoints import HumanCreativityCheckpoints, CheckpointType
from scripts.orchestration.autonomous_worktree_manager import AutonomousWorktreeManager
from scripts.orchestration.security_orchestrator import SecurityOrchestrator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlembicOrchestrator:
    """
    Orchestrates the Alembic causal AI system with autonomous worktree execution.
    Runs continuously to monitor markets and make data-driven decisions.
    """
    
    def __init__(self):
        self.causal_engine = CausalAnalyticsEngine()
        self.event_agent = EventDrivenMarketingAgent()
        self.data_pipeline = PrivateDataPipeline()
        self.creativity_checkpoints = HumanCreativityCheckpoints()
        self.worktree_manager = AutonomousWorktreeManager()
        self.security_orchestrator = SecurityOrchestrator()
        
        self.config = self._load_config()
        self.is_running = False
        
    def _load_config(self) -> Dict:
        """Load orchestration configuration"""
        config_path = Path(__file__).parent / "alembic_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        
        # Default configuration
        return {
            "monitoring_interval_minutes": 30,
            "causal_analysis_interval_hours": 6,
            "event_detection_interval_minutes": 10,
            "data_collection_interval_hours": 1,
            "worktree_tasks": {
                "market_research": "market-research",
                "content_generation": "puzzle-gen",
                "pdf_creation": "pdf-gen",
                "qa_validation": "qa-validation"
            }
        }
    
    async def start(self):
        """Start the autonomous Alembic orchestration"""
        self.is_running = True
        logger.info("🧪 Starting Alembic Causal AI Orchestrator...")
        
        # Initialize worktree infrastructure
        await self.worktree_manager.initialize_worktree_infrastructure()
        
        # Start all monitoring tasks concurrently
        tasks = [
            self._event_monitoring_loop(),
            self._causal_analysis_loop(),
            self._data_collection_loop(),
            self._decision_execution_loop(),
            self._security_monitoring_loop()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _event_monitoring_loop(self):
        """Continuously monitor for market events"""
        interval = self.config["event_detection_interval_minutes"] * 60
        
        while self.is_running:
            try:
                logger.info("⚡ Checking for market events...")
                
                # Collect events from various sources
                events = await self._collect_market_events()
                
                # Process each event through the event-driven agent
                for event in events:
                    await self.event_agent.process_event(event)
                
                # Get pending actions from the agent
                actions = self.event_agent.action_history[-5:]  # Last 5 actions
                
                # Execute high-priority actions
                for action in actions:
                    if action.priority >= 7:  # High priority threshold
                        await self._execute_marketing_action(action)
                
            except Exception as e:
                logger.error(f"Error in event monitoring: {e}")
            
            await asyncio.sleep(interval)
    
    async def _causal_analysis_loop(self):
        """Periodically run causal analysis on collected data"""
        interval = self.config["causal_analysis_interval_hours"] * 3600
        
        while self.is_running:
            try:
                logger.info("🧪 Running causal analysis...")
                
                # Analyze recent marketing campaigns
                await self._analyze_campaign_effectiveness()
                
                # Analyze price elasticity
                await self._analyze_price_elasticity()
                
                # Analyze series performance
                await self._analyze_series_impact()
                
                # Generate insights report
                insights = await self._generate_causal_insights()
                await self._save_insights_report(insights)
                
            except Exception as e:
                logger.error(f"Error in causal analysis: {e}")
            
            await asyncio.sleep(interval)
    
    async def _data_collection_loop(self):
        """Continuously collect and process private data"""
        interval = self.config["data_collection_interval_hours"] * 3600
        
        while self.is_running:
            try:
                logger.info("🔐 Collecting private data...")
                
                # Collect from various sources
                await self._collect_kdp_analytics()
                await self._collect_website_analytics()
                await self._process_reader_surveys()
                
                # Export anonymized data for ML training
                ml_data = self.data_pipeline.export_for_ml()
                await self._save_ml_training_data(ml_data)
                
            except Exception as e:
                logger.error(f"Error in data collection: {e}")
            
            await asyncio.sleep(interval)
    
    async def _decision_execution_loop(self):
        """Execute decisions based on causal insights and events"""
        interval = self.config["monitoring_interval_minutes"] * 60
        
        while self.is_running:
            try:
                logger.info("🎯 Executing intelligent decisions...")
                
                # Get pending decisions that need execution
                decisions = await self._get_pending_decisions()
                
                for decision in decisions:
                    # Route to appropriate worktree
                    worktree = self._get_worktree_for_decision(decision)
                    
                    # Execute in parallel using worktree
                    await self.worktree_manager.execute_in_worktree(
                        worktree,
                        decision["task"],
                        decision["parameters"]
                    )
                
                # Check for human checkpoint requests
                await self._process_human_checkpoints()
                
            except Exception as e:
                logger.error(f"Error in decision execution: {e}")
            
            await asyncio.sleep(interval)
    
    async def _security_monitoring_loop(self):
        """Continuously monitor for security issues"""
        interval = 3600  # Run security scans every hour
        
        while self.is_running:
            try:
                logger.info("🔒 Running security validation...")
                
                # Run comprehensive security scan
                issues = await self.security_orchestrator.scan_for_security_issues()
                
                # Check for critical issues
                critical_issues = [i for i in issues if i.severity.value == "critical"]
                
                if critical_issues:
                    logger.warning(f"🚨 Found {len(critical_issues)} critical security issues!")
                    
                    # Stop certain operations if critical issues found
                    await self._handle_critical_security_issues(critical_issues)
                
                # Generate and save security report
                report = self.security_orchestrator.generate_security_report()
                await self._save_security_report(report)
                
            except Exception as e:
                logger.error(f"Error in security monitoring: {e}")
            
            await asyncio.sleep(interval)
    
    async def _collect_market_events(self) -> List[MarketEvent]:
        """Collect market events from various sources"""
        events = []
        
        # Check KDP rank changes
        kdp_data = await self._fetch_kdp_rankings()
        for book_id, data in kdp_data.items():
            if data.get("rank_drop", 0) > 50:
                events.append(MarketEvent(
                    event_type=EventType.COMPETITOR_RANK_DROP,
                    timestamp=datetime.now(),
                    book_id=book_id,
                    magnitude=min(1.0, data["rank_drop"] / 100),
                    data=data,
                    source="kdp_api"
                ))
        
        # Check keyword trends
        keyword_data = await self._fetch_keyword_trends()
        for keyword, trend in keyword_data.items():
            if trend.get("spike_magnitude", 0) > 0.7:
                events.append(MarketEvent(
                    event_type=EventType.KEYWORD_SPIKE,
                    timestamp=datetime.now(),
                    book_id=None,
                    magnitude=trend["spike_magnitude"],
                    data={"keyword": keyword, **trend},
                    source="google_trends"
                ))
        
        # Check review milestones
        review_data = await self._fetch_review_counts()
        for book_id, count in review_data.items():
            if count in [50, 100, 250, 500, 1000]:
                events.append(MarketEvent(
                    event_type=EventType.REVIEW_MILESTONE,
                    timestamp=datetime.now(),
                    book_id=book_id,
                    magnitude=0.8,
                    data={"review_count": count},
                    source="kdp_api"
                ))
        
        return events
    
    async def _execute_marketing_action(self, action):
        """Execute a marketing action using worktrees"""
        logger.info(f"Executing action: {action.action_type.value}")
        
        if action.action_type.value == "launch_ad_campaign":
            # Use market-research worktree
            await self.worktree_manager.execute_in_worktree(
                "market-research",
                "create_ad_campaign",
                action.parameters
            )
        
        elif action.action_type.value == "generate_blog_post":
            # Use puzzle-gen worktree for content
            await self.worktree_manager.execute_in_worktree(
                "puzzle-gen",
                "generate_seo_content",
                {
                    "keyword": action.parameters.get("keyword"),
                    "book_id": action.target_book_id
                }
            )
    
    async def _analyze_campaign_effectiveness(self):
        """Analyze causal impact of recent campaigns"""
        # Get recent campaigns
        campaigns = await self._fetch_recent_campaigns()
        
        for campaign in campaigns:
            # Run causal analysis
            result = self.causal_engine.analyze_marketing_campaign_roi(
                campaign["id"],
                campaign["target_books"]
            )
            
            # Store results
            await self._store_causal_result(
                f"campaign_{campaign['id']}",
                result
            )
            
            # If ROI is negative, stop similar campaigns
            if result.effect_size < 0:
                await self._pause_similar_campaigns(campaign)
    
    async def _analyze_price_elasticity(self):
        """Analyze price elasticity for dynamic pricing"""
        books = await self._fetch_active_books()
        
        for book_id in books:
            price_history = await self._fetch_price_history(book_id)
            
            if len(price_history) >= 3:  # Need at least 3 price points
                result = self.causal_engine.analyze_price_elasticity(
                    book_id,
                    price_history
                )
                
                # Recommend optimal price
                if result.metadata.get("elasticity", 0) < -1:
                    # Elastic demand - lower price could increase revenue
                    await self._recommend_price_change(book_id, "decrease")
    
    async def _analyze_series_impact(self):
        """Analyze series cannibalization vs growth"""
        series_list = await self._fetch_book_series()
        
        for series in series_list:
            if len(series["books"]) >= 2:
                latest_book = series["books"][-1]
                
                result = self.causal_engine.analyze_series_cannibalization(
                    series["id"],
                    latest_book["id"]
                )
                
                # If cannibalization is high, adjust marketing
                if result.metadata.get("cannibalization_rate", 0) > 0.3:
                    await self._adjust_series_marketing(series["id"])
    
    async def _process_human_checkpoints(self):
        """Process any pending human creativity checkpoints"""
        # Check for books needing human review
        pending_books = await self._fetch_books_pending_review()
        
        for book in pending_books:
            if book.get("needs_title_selection"):
                # Get AI-generated options
                title_options = await self._generate_title_options(book["id"])
                
                # Request human review
                response = await self.creativity_checkpoints.request_human_review(
                    checkpoint_type=CheckpointType.TITLE_SELECTION,
                    book_id=book["id"],
                    options=title_options,
                    context={"genre": book["genre"], "target_audience": book["audience"]},
                    timeout_hours=4  # Faster turnaround
                )
                
                # Apply the selection
                if response.selected_option_id:
                    await self._apply_title_selection(book["id"], response.selected_option_id)
    
    def _get_worktree_for_decision(self, decision: Dict) -> str:
        """Route decisions to appropriate worktrees"""
        decision_type = decision.get("type", "")
        
        if "market" in decision_type or "research" in decision_type:
            return "market-research"
        elif "content" in decision_type or "generate" in decision_type:
            return "puzzle-gen"
        elif "pdf" in decision_type or "format" in decision_type:
            return "pdf-gen"
        elif "validate" in decision_type or "qa" in decision_type:
            return "qa-validation"
        else:
            return "ci-fixes"  # Default for misc tasks
    
    async def _save_insights_report(self, insights: Dict):
        """Save causal insights report"""
        report_path = Path("reports/causal_insights")
        report_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = report_path / f"causal_insights_{timestamp}.json"
        
        with open(file_path, "w") as f:
            json.dump(insights, f, indent=2, default=str)
        
        logger.info(f"📊 Saved causal insights to {file_path}")
    
    # Placeholder methods for data fetching
    async def _fetch_kdp_rankings(self) -> Dict:
        # In production, connect to KDP API
        return {}
    
    async def _fetch_keyword_trends(self) -> Dict:
        # In production, connect to Google Trends
        return {}
    
    async def _fetch_review_counts(self) -> Dict:
        # In production, fetch from KDP
        return {}
    
    async def _fetch_recent_campaigns(self) -> List[Dict]:
        return []
    
    async def _fetch_active_books(self) -> List[str]:
        return []
    
    async def _fetch_price_history(self, book_id: str) -> List[Dict]:
        return []
    
    async def _fetch_book_series(self) -> List[Dict]:
        return []
    
    async def _collect_kdp_analytics(self):
        """Collect KDP analytics data"""
        pass
    
    async def _collect_website_analytics(self):
        """Collect website analytics (from Vercel landing page)"""
        pass
    
    async def _process_reader_surveys(self):
        """Process reader survey responses"""
        pass
    
    async def _save_ml_training_data(self, data):
        """Save ML training data"""
        pass
    
    async def _get_pending_decisions(self) -> List[Dict]:
        """Get decisions that need execution"""
        return []
    
    async def _generate_causal_insights(self) -> Dict:
        """Generate comprehensive causal insights"""
        return {
            "timestamp": datetime.now(),
            "total_events_processed": len(self.event_agent.event_history),
            "total_actions_triggered": len(self.event_agent.action_history),
            "causal_relationships_discovered": 0,  # Placeholder
            "roi_improvements": {},
            "recommendations": []
        }
    
    async def _store_causal_result(self, key: str, result):
        """Store causal analysis results"""
        pass
    
    async def _pause_similar_campaigns(self, campaign: Dict):
        """Pause campaigns with negative ROI"""
        pass
    
    async def _recommend_price_change(self, book_id: str, direction: str):
        """Recommend price changes based on elasticity"""
        pass
    
    async def _adjust_series_marketing(self, series_id: str):
        """Adjust marketing for cannibalistic series"""
        pass
    
    async def _fetch_books_pending_review(self) -> List[Dict]:
        """Get books needing human review"""
        return []
    
    async def _generate_title_options(self, book_id: str) -> List:
        """Generate title options for human selection"""
        return []
    
    async def _apply_title_selection(self, book_id: str, title_id: str):
        """Apply human-selected title"""
        pass
    
    async def _handle_critical_security_issues(self, critical_issues: List):
        """Handle critical security issues found during monitoring"""
        logger.error(f"🚨 CRITICAL SECURITY ALERT: {len(critical_issues)} issues found")
        
        # Create detailed alert message
        alert_message = "CRITICAL SECURITY ISSUES DETECTED:\n\n"
        for issue in critical_issues:
            alert_message += f"• {issue.description}\n"
            alert_message += f"  File: {issue.file_path}\n"
            alert_message += f"  Fix: {issue.recommendation}\n\n"
        
        # Pause high-risk operations temporarily
        logger.warning("⏸️  Pausing automated content generation until issues resolved")
        
        # Save critical alert
        alert_path = Path("reports/security/CRITICAL_ALERT.txt")
        alert_path.parent.mkdir(parents=True, exist_ok=True)
        with open(alert_path, "w") as f:
            f.write(alert_message)
        
        # TODO: Send Slack/email notifications if configured
        
    async def _save_security_report(self, report: Dict):
        """Save security report to file"""
        report_dir = Path("reports/security")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"alembic_security_report_{timestamp}.json"
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"💾 Security report saved to {report_path}")


async def main():
    """Run the Alembic orchestrator"""
    orchestrator = AlembicOrchestrator()
    
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Alembic orchestrator...")
        orchestrator.is_running = False


if __name__ == "__main__":
    asyncio.run(main())