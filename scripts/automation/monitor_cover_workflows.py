#!/usr/bin/env python3
"""
Cover Workflow Monitor - Automatic Resume Detection
Monitors for completed covers and resumes paused workflows automatically.

DEPLOYMENT: Run as cron job every 5 minutes to check for completed covers
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.core.cover_workflow_orchestrator import CoverWorkflowOrchestrator
from lambda.v3_orchestrator import V3Orchestrator

class CoverWorkflowMonitor:
    """Monitors and automatically resumes cover workflows."""
    
    def __init__(self):
        self.logger = get_logger('cover_workflow_monitor')
        self.orchestrator = CoverWorkflowOrchestrator()
        self.v3_orchestrator = V3Orchestrator()
        
    def monitor_and_resume_workflows(self, base_output_dir: str = "output") -> Dict[str, Any]:
        """Monitor all pending workflows and resume when covers are ready.
        
        Args:
            base_output_dir: Base directory to scan for pending workflows
            
        Returns:
            Summary of monitoring results
        """
        try:
            self.logger.info("🔍 Starting cover workflow monitoring cycle")
            
            base_path = Path(base_output_dir)
            if not base_path.exists():
                self.logger.warning(f"Output directory not found: {base_output_dir}")
                return {'status': 'no_output_directory'}
            
            # Scan for pending workflows
            monitoring_result = self.orchestrator.monitor_pending_workflows(base_path)
            
            # Resume workflows that are ready
            resumed_count = 0
            for workflow in monitoring_result.get('resumed_workflows', []):
                try:
                    self._resume_specific_workflow(workflow)
                    resumed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to resume workflow {workflow['book']}: {e}")
            
            return {
                'status': 'completed',
                'monitoring_result': monitoring_result,
                'resumed_workflows': resumed_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Workflow monitoring failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _resume_specific_workflow(self, workflow_info: Dict[str, Any]):
        """Resume a specific workflow that has a completed cover.
        
        Args:
            workflow_info: Information about the workflow to resume
        """
        try:
            directory = Path(workflow_info['directory'])
            
            # Load workflow state to get original parameters
            state_file = directory / "cover_workflow_state.json"
            if not state_file.exists():
                self.logger.warning(f"No state file found for {workflow_info['book']}")
                return
            
            with open(state_file, 'r') as f:
                workflow_state = json.load(f)
            
            book_data = workflow_state['book_data']
            
            # Extract book ID from directory name
            book_id = directory.name
            
            # Load content assets if they exist
            content_assets = self._load_content_assets(directory)
            
            # Resume the V3 orchestrator workflow
            self.logger.info(f"▶️ Resuming workflow for: {book_data.get('title', 'Unknown')}")
            
            resume_result = self.v3_orchestrator.resume_workflow_after_cover(
                book_id=book_id,
                topic_data={
                    'topic': book_data.get('topic', book_data.get('title')),
                    'niche': book_data.get('niche', 'General')
                },
                content_assets=content_assets
            )
            
            self.logger.info(f"✅ Workflow resumed successfully for {book_data.get('title')}")
            
        except Exception as e:
            self.logger.error(f"Failed to resume workflow: {e}")
            raise
    
    def _load_content_assets(self, directory: Path) -> Dict[str, Any]:
        """Load content assets from the book directory.
        
        Args:
            directory: Book output directory
            
        Returns:
            Content assets dictionary
        """
        try:
            # Look for common content files
            content_assets = {}
            
            # Check for manuscript
            manuscript_file = directory / "manuscript.txt"
            if manuscript_file.exists():
                content_assets['manuscript_path'] = str(manuscript_file)
            
            # Check for metadata
            metadata_file = directory / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    content_assets.update(metadata)
            
            # Check for marketing content
            marketing_file = directory / "marketing_content.txt"
            if marketing_file.exists():
                content_assets['marketing_content_path'] = str(marketing_file)
            
            return content_assets
            
        except Exception as e:
            self.logger.warning(f"Failed to load content assets: {e}")
            return {}

def run_monitoring_cycle():
    """Run a single monitoring cycle."""
    print("🔍 KindleMint Cover Workflow Monitor")
    print("=" * 50)
    
    monitor = CoverWorkflowMonitor()
    result = monitor.monitor_and_resume_workflows()
    
    print(f"Status: {result['status']}")
    
    if result['status'] == 'completed':
        monitoring = result['monitoring_result']
        print(f"Resumed workflows: {result['resumed_workflows']}")
        print(f"Pending workflows: {monitoring.get('pending', 0)}")
        print(f"Timed out workflows: {monitoring.get('timed_out', 0)}")
    elif result['status'] == 'error':
        print(f"Error: {result['error']}")
    
    return result

def main():
    """Main monitoring function with options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor and resume cover workflows')
    parser.add_argument('--mode', choices=['once', 'daemon'], default='once',
                      help='Run once or as continuous daemon')
    parser.add_argument('--interval', type=int, default=300,
                      help='Monitoring interval in seconds (default: 5 minutes)')
    parser.add_argument('--output-dir', type=str, default='output',
                      help='Base output directory to monitor')
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        # Run single monitoring cycle
        result = run_monitoring_cycle()
        sys.exit(0 if result['status'] != 'error' else 1)
        
    elif args.mode == 'daemon':
        # Run continuous monitoring
        print(f"Starting daemon mode - checking every {args.interval} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                result = run_monitoring_cycle()
                print(f"Next check in {args.interval} seconds...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\\nMonitoring stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"Daemon failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()