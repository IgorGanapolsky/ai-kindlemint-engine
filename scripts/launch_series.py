#!/usr/bin/env python3
"""
Launch Series - Master Automation Script
Fully autonomous series creation and publishing orchestrator
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from security import safe_command

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kindlemint.utils.logger import get_logger

# Import foundation modules (Phase 1 requirements)
try:
    from kindlemint.utils.sentry_config import init_sentry, capture_business_event, SentryPerformanceTracker
    from kindlemint.agents.cost_tracker import start_tracking, finish_tracking, get_series_summary
    from kindlemint.agents.sales_data_ingestion import run_daily_ingestion
    from kindlemint.agents.profit_margin_calculator import analyze_series, generate_report
    FOUNDATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Foundation modules not available: {e}")
    FOUNDATION_AVAILABLE = False

# Import the publisher class directly
sys.path.append(str(project_root / "scripts" / "publishing"))
from autonomous_kdp_publisher import AutonomousKDPPublisher

class SeriesLauncher:
    def __init__(self):
        self.logger = get_logger('series_launcher')
        self.series_name = "Large Print Crossword Masters"
        self.brand_name = "Senior Puzzle Studio"
        
        # Initialize foundation monitoring (Phase 1 requirement)
        self.sentry_enabled = False
        if FOUNDATION_AVAILABLE:
            self.sentry_enabled = init_sentry("series-launcher", 
                                            custom_tags={"operation": "series_launch"})
            if self.sentry_enabled:
                self.logger.info("✅ Sentry monitoring initialized for series launch")
        
        # Session tracking
        self.launch_session_id = f"launch_{int(time.time())}"
        
    def step_a_create_kdp_series(self):
        """Step A: Create or verify KDP Series exists"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 STEP A: CREATING/VERIFYING KDP SERIES")
        self.logger.info("=" * 60)
        
        try:
            # Initialize KDP publisher for series creation only
            publisher = AutonomousKDPPublisher()
            
            # Setup browser
            if not publisher.setup_browser():
                self.logger.error("❌ Failed to setup browser")
                return False
            
            try:
                # Login to KDP
                if not publisher.login_to_kdp():
                    self.logger.error("❌ Failed to login to KDP")
                    return False
                
                # Create or verify series
                if not publisher.create_or_verify_kdp_series(self.series_name, self.brand_name):
                    self.logger.error("❌ Failed to create/verify series")
                    return False
                
                self.logger.info("✅ Step A completed successfully - Series ready!")
                return True
                
            finally:
                # Cleanup browser
                if hasattr(publisher, 'browser'):
                    publisher.browser.close()
                if hasattr(publisher, 'playwright'):
                    publisher.playwright.stop()
                    
        except Exception as e:
            self.logger.error(f"❌ Step A failed: {e}")
            return False
    
    def step_b_trigger_github_workflow(self, volumes_to_publish='1'):
        """Step B: Trigger GitHub Actions workflow remotely"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 STEP B: TRIGGERING GITHUB ACTIONS WORKFLOW")
        self.logger.info("=" * 60)
        
        try:
            # Check if gh CLI is available
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error("❌ GitHub CLI (gh) not installed or not authenticated")
                self.logger.error("💡 Install with: brew install gh && gh auth login")
                return False
            
            self.logger.info("✅ GitHub CLI detected and ready")
            
            # Trigger the workflow
            workflow_file = 'autonomous_publishing.yml'
            cmd = [
                'gh', 'workflow', 'run', workflow_file,
                '-f', f'volumes_to_publish={volumes_to_publish}'
            ]
            
            self.logger.info(f"🔥 Triggering workflow: {' '.join(cmd)}")
            
            result = safe_command.run(subprocess.run, cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                self.logger.info("✅ Step B completed successfully - Workflow triggered!")
                self.logger.info("🌐 Check workflow status at: https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions")
                return True
            else:
                self.logger.error(f"❌ Failed to trigger workflow: {result.stderr}")
                self.logger.error(f"Command output: {result.stdout}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Step B failed: {e}")
            return False
    
    def step_c_foundation_analysis(self):
        """Step C: Run foundation data collection and profit analysis (Phase 1)"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 STEP C: FOUNDATION DATA COLLECTION & ANALYSIS")
        self.logger.info("=" * 60)
        
        if not FOUNDATION_AVAILABLE:
            self.logger.warning("⚠️ Foundation modules not available - skipping analysis")
            return True
        
        try:
            analysis_results = {}
            
            # 1. Sales Data Ingestion
            self.logger.info("📊 Running sales data ingestion...")
            try:
                sales_result = run_daily_ingestion()
                analysis_results['sales_ingestion'] = sales_result
                if sales_result.get('success'):
                    self.logger.info(f"✅ Sales ingestion completed - {sales_result.get('records_processed', 0)} records")
                else:
                    self.logger.warning(f"⚠️ Sales ingestion had issues: {sales_result.get('error', 'Unknown error')}")
            except Exception as e:
                self.logger.error(f"❌ Sales ingestion failed: {e}")
                analysis_results['sales_ingestion'] = {'success': False, 'error': str(e)}
            
            # 2. Cost Analysis
            self.logger.info("💰 Analyzing production costs...")
            try:
                cost_summary = get_series_summary(self.series_name.replace(' ', '_'))
                analysis_results['cost_analysis'] = cost_summary
                if cost_summary:
                    total_cost = cost_summary.get('total_production_cost', 0)
                    volume_count = cost_summary.get('total_volumes', 0)
                    self.logger.info(f"✅ Cost analysis completed - ${total_cost:.2f} total cost for {volume_count} volumes")
                else:
                    self.logger.info("ℹ️ No cost data available yet (expected for new series)")
            except Exception as e:
                self.logger.error(f"❌ Cost analysis failed: {e}")
                analysis_results['cost_analysis'] = {'error': str(e)}
            
            # 3. Profit Analysis
            self.logger.info("📈 Running profit margin analysis...")
            try:
                series_analysis = analyze_series(self.series_name.replace(' ', '_'))
                analysis_results['profit_analysis'] = series_analysis
                if series_analysis:
                    profit = series_analysis.total_net_profit
                    margin = series_analysis.series_profit_margin_percent
                    self.logger.info(f"✅ Profit analysis completed - ${profit:.2f} profit ({margin:.1f}% margin)")
                else:
                    self.logger.info("ℹ️ No profit data available yet (expected for new series)")
            except Exception as e:
                self.logger.error(f"❌ Profit analysis failed: {e}")
                analysis_results['profit_analysis'] = {'error': str(e)}
            
            # 4. Generate Comprehensive Report
            self.logger.info("📋 Generating foundation report...")
            try:
                profit_report = generate_report(self.series_name.replace(' ', '_'))
                analysis_results['comprehensive_report'] = profit_report
                
                # Save session analysis
                session_file = Path(f"output/foundation_analysis/launch_session_{self.launch_session_id}.json")
                session_file.parent.mkdir(parents=True, exist_ok=True)
                with open(session_file, 'w') as f:
                    json.dump(analysis_results, f, indent=2, default=str)
                
                self.logger.info(f"✅ Foundation analysis saved to {session_file}")
                
            except Exception as e:
                self.logger.error(f"❌ Report generation failed: {e}")
                analysis_results['comprehensive_report'] = {'error': str(e)}
            
            # Send to Sentry for business intelligence
            if self.sentry_enabled:
                capture_business_event("foundation_analysis_completed",
                                     f"Foundation analysis for {self.series_name} completed",
                                     extra_data=analysis_results)
            
            self.logger.info("✅ Step C completed - Foundation analysis finished!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Step C failed: {e}")
            if self.sentry_enabled:
                capture_business_event("foundation_analysis_failed", str(e), level='error')
            return False

    def launch_series(self, volumes_to_publish='1', skip_series_creation=False):
        """Master launch sequence: Step A → Step B → Step C (Foundation Analysis)"""
        launch_time = datetime.now()
        
        self.logger.info("🎯" * 20)
        self.logger.info("🤖 KINDLEMINT EMPIRE - FULL AUTOMATION LAUNCH (Phase 1)")
        self.logger.info("🎯" * 20)
        self.logger.info(f"📚 Series: {self.series_name}")
        self.logger.info(f"🏭 Brand: {self.brand_name}")
        self.logger.info(f"📖 Volumes to publish: {volumes_to_publish}")
        self.logger.info(f"⏰ Launch time: {launch_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"🔍 Foundation monitoring: {'✅ Enabled' if FOUNDATION_AVAILABLE else '❌ Disabled'}")
        self.logger.info("🎯" * 20)
        
        success_log = []
        failure_log = []
        
        # Track launch performance
        performance_tracker = None
        if self.sentry_enabled:
            performance_tracker = SentryPerformanceTracker("series_launch", 
                                                         {"series": self.series_name, 
                                                          "volumes": volumes_to_publish})
        
        # Step A: Create/verify KDP Series
        if not skip_series_creation:
            step_a_success = self.step_a_create_kdp_series()
            if step_a_success:
                success_log.append("✅ Step A: KDP Series created/verified")
            else:
                failure_log.append("❌ Step A: Failed to create KDP Series")
                self.print_final_report(success_log, failure_log, launch_time)
                return False
        else:
            self.logger.info("⏭️ Skipping Step A (series creation) as requested")
            success_log.append("⏭️ Step A: Skipped series creation")
        
        # Brief pause between steps
        time.sleep(2)
        
        # Step B: Trigger GitHub Actions workflow
        step_b_success = self.step_b_trigger_github_workflow(volumes_to_publish)
        if step_b_success:
            success_log.append("✅ Step B: GitHub Actions workflow triggered")
        else:
            failure_log.append("❌ Step B: Failed to trigger workflow")
        
        # Brief pause between steps
        time.sleep(2)
        
        # Step C: Foundation Data Collection & Analysis (Phase 1 requirement)
        step_c_success = self.step_c_foundation_analysis()
        if step_c_success:
            success_log.append("✅ Step C: Foundation analysis completed")
        else:
            failure_log.append("❌ Step C: Foundation analysis failed")
        
        # Final report
        self.print_final_report(success_log, failure_log, launch_time)
        
        # Close performance tracking
        if performance_tracker:
            performance_tracker.__exit__(None, None, None)
        
        return len(failure_log) == 0
    
    def print_final_report(self, success_log, failure_log, launch_time):
        """Print final automation report"""
        completion_time = datetime.now()
        duration = completion_time - launch_time
        
        self.logger.info("🏁" * 20)
        self.logger.info("📊 PHASE 1 FOUNDATION LAUNCH REPORT")
        self.logger.info("🏁" * 20)
        
        for success in success_log:
            self.logger.info(success)
        
        for failure in failure_log:
            self.logger.error(failure)
        
        self.logger.info(f"⏱️ Total execution time: {duration.total_seconds():.1f} seconds")
        
        if not failure_log:
            self.logger.info("🎉 FULL AUTOMATION SUCCESSFUL!")
            self.logger.info("🚀 Your KDP empire is launching autonomously!")
            self.logger.info("🌐 Monitor progress: https://github.com/IgorGanapolsky/ai-kindlemint-engine/actions")
        else:
            self.logger.error("⚠️ AUTOMATION INCOMPLETE - Manual intervention required")
            
        self.logger.info("🏁" * 20)

def main():
    """Main function for series launch automation"""
    parser = argparse.ArgumentParser(description='Launch Series - Full KDP Automation')
    parser.add_argument('--volumes', type=str, default='1', 
                       help='Volumes to publish (comma-separated or single number)')
    parser.add_argument('--skip-series', action='store_true', 
                       help='Skip series creation (Step A) and go directly to workflow trigger')
    
    args = parser.parse_args()
    
    try:
        launcher = SeriesLauncher()
        success = launcher.launch_series(
            volumes_to_publish=args.volumes,
            skip_series_creation=args.skip_series
        )
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Series launch failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
