#!/usr/bin/env python3
"""
Cover Workflow Orchestrator - Human-in-the-Loop Cover Creation
Manages the two-stage cover creation process with workflow pause/resume.

WORKFLOW:
1. Generate detailed cover prompt → PAUSE
2. Wait for human cover creation → RESUME  
3. Continue automated KDP publishing
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.agents.prompt_copilot_agent import PromptCoPilotAgent
from kindlemint.notifications.slack_notifier import SlackNotifier

class CoverWorkflowOrchestrator:
    """Orchestrates human-in-the-loop cover creation workflow."""
    
    def __init__(self):
        self.logger = get_logger('cover_workflow_orchestrator')
        self.prompt_agent = PromptCoPilotAgent()
        self.slack_notifier = SlackNotifier()
        
        # Workflow state management
        self.state_file_name = "cover_workflow_state.json"
    
    def execute_cover_workflow(self, book_data: Dict[str, Any], output_dir: Path, 
                             resume_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute the complete cover workflow with human intervention.
        
        Args:
            book_data: Book information for cover creation
            output_dir: Directory for book assets
            resume_callback: Function to call when workflow resumes
            
        Returns:
            Workflow execution results
        """
        try:
            self.logger.info(f"🎨 Starting cover workflow for: {book_data.get('title', 'Unknown')}")
            
            # Stage 1: Generate cover prompt
            prompt_file = self.prompt_agent.generate_cover_prompt(book_data, output_dir)
            
            # Save workflow state
            workflow_state = {
                'book_data': book_data,
                'output_dir': str(output_dir),
                'prompt_file': prompt_file,
                'stage': 'waiting_for_cover',
                'created_at': datetime.now().isoformat(),
                'resume_callback': resume_callback.__name__ if resume_callback else None
            }
            
            self._save_workflow_state(output_dir, workflow_state)
            
            self.logger.info("⏸️ Workflow PAUSED - Waiting for cover creation")
            
            return {
                'status': 'paused',
                'stage': 'waiting_for_cover',
                'prompt_file': prompt_file,
                'message': 'Cover prompt generated. Waiting for human cover creation.'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Cover workflow failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_and_resume_workflow(self, output_dir: Path) -> Dict[str, Any]:
        """Check if cover is ready and resume workflow if possible.
        
        Args:
            output_dir: Directory to check for completed cover
            
        Returns:
            Resume status and next steps
        """
        try:
            # Check if cover exists
            if not self.prompt_agent.check_cover_completion(output_dir):
                return {
                    'status': 'waiting',
                    'message': 'Cover not yet detected. Workflow still paused.'
                }
            
            # Load workflow state
            workflow_state = self._load_workflow_state(output_dir)
            if not workflow_state:
                return {
                    'status': 'error',
                    'message': 'No workflow state found. Cannot resume.'
                }
            
            # Resume workflow
            self.logger.info("▶️ Workflow RESUMED - Cover detected, continuing automation")
            
            # Clean up workflow state
            self._cleanup_workflow_state(output_dir)
            
            return {
                'status': 'resumed',
                'book_data': workflow_state['book_data'],
                'message': 'Cover detected. Workflow resumed for KDP publishing.'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to check/resume workflow: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def monitor_pending_workflows(self, base_output_dir: Path, timeout_hours: int = 24) -> Dict[str, Any]:
        """Monitor all pending workflows and check for completion.
        
        Args:
            base_output_dir: Base directory containing all book outputs
            timeout_hours: Hours to wait before timing out workflows
            
        Returns:
            Summary of monitoring results
        """
        try:
            self.logger.info("🔍 Monitoring pending cover workflows...")
            
            resumed_workflows = []
            pending_workflows = []
            timed_out_workflows = []
            
            # Search for workflow state files
            for state_file in base_output_dir.rglob(self.state_file_name):
                output_dir = state_file.parent
                
                # Load and check workflow state
                workflow_state = self._load_workflow_state(output_dir)
                if not workflow_state:
                    continue
                
                # Check if workflow has timed out
                created_time = datetime.fromisoformat(workflow_state['created_at'])
                if datetime.now() - created_time > timedelta(hours=timeout_hours):
                    timed_out_workflows.append({
                        'book': workflow_state['book_data'].get('title', 'Unknown'),
                        'directory': str(output_dir),
                        'created_at': workflow_state['created_at']
                    })
                    self._cleanup_workflow_state(output_dir)
                    continue
                
                # Check if cover is ready
                resume_result = self.check_and_resume_workflow(output_dir)
                
                if resume_result['status'] == 'resumed':
                    resumed_workflows.append({
                        'book': workflow_state['book_data'].get('title', 'Unknown'),
                        'directory': str(output_dir)
                    })
                elif resume_result['status'] == 'waiting':
                    pending_workflows.append({
                        'book': workflow_state['book_data'].get('title', 'Unknown'),
                        'directory': str(output_dir),
                        'waiting_since': workflow_state['created_at']
                    })
            
            # Send monitoring summary
            self._send_monitoring_summary(resumed_workflows, pending_workflows, timed_out_workflows)
            
            return {
                'resumed': len(resumed_workflows),
                'pending': len(pending_workflows),
                'timed_out': len(timed_out_workflows),
                'resumed_workflows': resumed_workflows,
                'pending_workflows': pending_workflows
            }
            
        except Exception as e:
            self.logger.error(f"❌ Workflow monitoring failed: {e}")
            return {'error': str(e)}
    
    def _save_workflow_state(self, output_dir: Path, state: Dict[str, Any]):
        """Save workflow state to file."""
        state_file = output_dir / self.state_file_name
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(f"Workflow state saved: {state_file}")
    
    def _load_workflow_state(self, output_dir: Path) -> Optional[Dict[str, Any]]:
        """Load workflow state from file."""
        state_file = output_dir / self.state_file_name
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load workflow state: {e}")
            return None
    
    def _cleanup_workflow_state(self, output_dir: Path):
        """Clean up workflow state file after completion."""
        state_file = output_dir / self.state_file_name
        
        if state_file.exists():
            state_file.unlink()
            self.logger.debug(f"Workflow state cleaned up: {state_file}")
    
    def _send_monitoring_summary(self, resumed: list, pending: list, timed_out: list):
        """Send Slack summary of workflow monitoring."""
        try:
            if not (resumed or pending or timed_out):
                return  # No workflows to report
            
            message_parts = ["📊 **COVER WORKFLOW MONITORING SUMMARY**\\n"]
            
            if resumed:
                message_parts.append(f"✅ **Resumed Workflows**: {len(resumed)}")
                for workflow in resumed:
                    message_parts.append(f"  • {workflow['book']}")
                message_parts.append("")
            
            if pending:
                message_parts.append(f"⏸️ **Pending Workflows**: {len(pending)}")
                for workflow in pending:
                    message_parts.append(f"  • {workflow['book']} (waiting since {workflow['waiting_since'][:10]})")
                message_parts.append("")
            
            if timed_out:
                message_parts.append(f"⏰ **Timed Out Workflows**: {len(timed_out)}")
                for workflow in timed_out:
                    message_parts.append(f"  • {workflow['book']} (abandoned)")
                message_parts.append("")
            
            message_parts.append("🔄 Next monitoring cycle in 30 minutes")
            
            self.slack_notifier.send_notification(
                message="\\n".join(message_parts),
                title="Cover Workflow Monitoring",
                color="good" if resumed else "warning"
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to send monitoring summary: {e}")

def main():
    """Test the Cover Workflow Orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test cover workflow orchestrator')
    parser.add_argument('--command', choices=['start', 'check', 'monitor'], 
                      default='start', help='Command to execute')
    parser.add_argument('--output', type=str, 
                      default='output/test_workflow',
                      help='Output directory')
    parser.add_argument('--title', type=str, 
                      default='Large Print Crossword Masters',
                      help='Book title')
    parser.add_argument('--volume', type=int, default=1,
                      help='Volume number')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎯 COVER WORKFLOW ORCHESTRATOR TEST")
    print("=" * 70)
    
    orchestrator = CoverWorkflowOrchestrator()
    output_dir = Path(args.output)
    
    if args.command == 'start':
        # Test workflow start
        book_data = {
            'title': args.title,
            'volume': args.volume,
            'series': 'Large Print Crossword Masters',
            'brand': 'Senior Puzzle Studio'
        }
        
        result = orchestrator.execute_cover_workflow(book_data, output_dir)
        print(f"Workflow started: {result}")
        
    elif args.command == 'check':
        # Test workflow check/resume
        result = orchestrator.check_and_resume_workflow(output_dir)
        print(f"Workflow check: {result}")
        
    elif args.command == 'monitor':
        # Test workflow monitoring
        base_dir = Path('output')
        result = orchestrator.monitor_pending_workflows(base_dir)
        print(f"Monitoring results: {result}")

if __name__ == "__main__":
    main()