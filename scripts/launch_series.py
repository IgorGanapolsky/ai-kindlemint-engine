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

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kindlemint.utils.logger import get_logger

# Import the publisher class directly
sys.path.append(str(project_root / "scripts" / "publishing"))
from autonomous_kdp_publisher import AutonomousKDPPublisher

class SeriesLauncher:
    def __init__(self):
        self.logger = get_logger('series_launcher')
        self.series_name = "Large Print Crossword Masters"
        self.brand_name = "Senior Puzzle Studio"
        
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
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
    
    def launch_series(self, volumes_to_publish='1', skip_series_creation=False):
        """Master launch sequence: Step A → Step B"""
        launch_time = datetime.now()
        
        self.logger.info("🎯" * 20)
        self.logger.info("🤖 KINDLEMINT EMPIRE - FULL AUTOMATION LAUNCH")
        self.logger.info("🎯" * 20)
        self.logger.info(f"📚 Series: {self.series_name}")
        self.logger.info(f"🏭 Brand: {self.brand_name}")
        self.logger.info(f"📖 Volumes to publish: {volumes_to_publish}")
        self.logger.info(f"⏰ Launch time: {launch_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("🎯" * 20)
        
        success_log = []
        failure_log = []
        
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
        
        # Final report
        self.print_final_report(success_log, failure_log, launch_time)
        
        return len(failure_log) == 0
    
    def print_final_report(self, success_log, failure_log, launch_time):
        """Print final automation report"""
        completion_time = datetime.now()
        duration = completion_time - launch_time
        
        self.logger.info("🏁" * 20)
        self.logger.info("📊 AUTOMATION COMPLETION REPORT")
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