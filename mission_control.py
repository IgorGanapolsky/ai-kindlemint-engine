#!/usr/bin/env python3
"""
Mission Control - AI-Powered Content Creation Automation System

This script coordinates three AI agents:
- CTO: Content creation and book generation
- CMO: Marketing content and distribution  
- CFO: Logging, analytics, and financial tracking

Usage:
    python mission_control.py [book_topic]
    python mission_control.py --agent cto "Your Book Topic"
    python mission_control.py --summary
    python mission_control.py --help
"""

import sys
import argparse
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Import agents
from agents.cto_agent import CTOAgent
from agents.cmo_agent import CMOAgent
from agents.cfo_agent import CFOAgent
from utils.logger import MissionLogger
import config

class MissionControl:
    """Main Mission Control coordinator"""
    
    def __init__(self):
        self.logger = MissionLogger("MissionControl")
        self.cto = CTOAgent()
        self.cmo = CMOAgent()
        self.cfo = CFOAgent()
    
    def execute_full_mission(self, book_topic: str) -> Dict[str, Any]:
        """Execute complete mission with all agents"""
        mission_start = time.time()
        self.logger.info("=" * 60)
        self.logger.info("🚀 MISSION CONTROL ACTIVATED")
        self.logger.info("=" * 60)
        self.logger.info(f"📚 Book Topic: {book_topic}")
        self.logger.info(f"⏰ Mission Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'mission_topic': book_topic,
            'mission_start_time': mission_start,
            'agents_results': {},
            'mission_success': False
        }
        
        try:
            # Phase 1: CTO - Content Creation
            self.logger.info("\n🎯 PHASE 1: CONTENT CREATION (CTO)")
            self.logger.info("-" * 40)
            cto_result = self.cto.run_cto_tasks(book_topic)
            results['agents_results']['cto'] = cto_result
            
            if not cto_result['success']:
                self.logger.error("❌ CTO Phase failed - Mission aborted")
                return results
            
            # Phase 2: CMO - Marketing Content
            self.logger.info("\n📈 PHASE 2: MARKETING CONTENT (CMO)")
            self.logger.info("-" * 40)
            cmo_result = self.cmo.run_cmo_tasks(book_topic)
            results['agents_results']['cmo'] = cmo_result
            
            if not cmo_result['success']:
                self.logger.warning("⚠️ CMO Phase failed - Continuing with mission")
            
            # Phase 3: CFO - Logging and Analytics
            self.logger.info("\n📊 PHASE 3: LOGGING & ANALYTICS (CFO)")
            self.logger.info("-" * 40)
            
            # Prepare comprehensive activity data
            activity_data = {
                'book_topic': book_topic,
                'cto_success': cto_result['success'],
                'cmo_success': cmo_result['success'],
                'total_files_created': self._count_generated_files(cto_result, cmo_result),
                'mission_duration': time.time() - mission_start,
                'content_types': ['book_outline', 'chapters', 'blog_posts', 'social_media'],
                'estimated_word_count': cto_result.get('content', {}).get('metadata', {}).get('estimated_word_count', 0)
            }
            
            cfo_result = self.cfo.run_cfo_tasks(
                f"Completed full mission cycle for '{book_topic}'",
                activity_data
            )
            results['agents_results']['cfo'] = cfo_result
            
            # Phase 4: Publishing to KDP (Publisher Agent)
            self.logger.info("\n🚀 PHASE 4: PUBLISHING TO KDP (PublisherAgent)")
            self.logger.info("-" * 40)
            try:
                from agents.publisher_agent import PublisherAgent
                publisher_agent = PublisherAgent()
                
                # Get the path to the generated book file from the CTO's results
                book_file_path = cto_result.get('kpf_path')
                if book_file_path:
                    publishing_result = publisher_agent.publish_to_kdp(book_file_path)
                    results['agents_results']['publisher'] = publishing_result
                    
                    if publishing_result['success']:
                        self.logger.info("✅ Book successfully submitted to KDP for review.")
                    else:
                        self.logger.error("❌ KDP Publishing failed.")
                else:
                    self.logger.warning("⚠️ No book file found to publish.")
                    results['agents_results']['publisher'] = {
                        'success': False, 
                        'error': 'No book file path available for publishing'
                    }
            except Exception as e:
                self.logger.error(f"💥 Publishing Phase failed: {e}")
                results['agents_results']['publisher'] = {'success': False, 'error': str(e)}
            
            # Mission completion
            mission_duration = time.time() - mission_start
            results['mission_duration'] = mission_duration
            results['mission_success'] = cto_result['success']  # Mission success depends on CTO
            
            self.logger.info("\n" + "=" * 60)
            if results['mission_success']:
                self.logger.info("✅ MISSION CONTROL CYCLE COMPLETE - SUCCESS")
            else:
                self.logger.info("⚠️ MISSION CONTROL CYCLE COMPLETE - PARTIAL SUCCESS")
            self.logger.info("=" * 60)
            self.logger.info(f"⏱️ Total Mission Duration: {mission_duration:.2f} seconds")
            self.logger.info(f"📁 Output Files Created: {activity_data['total_files_created']}")
            
            # Print summary including publisher results
            self._print_mission_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"💥 MISSION CONTROL CRITICAL ERROR: {e}")
            results['mission_error'] = str(e)
            results['mission_duration'] = time.time() - mission_start
            return results
    
    def execute_single_agent(self, agent_name: str, topic: str) -> Dict[str, Any]:
        """Execute single agent task"""
        self.logger.info(f"🎯 Executing single agent: {agent_name.upper()}")
        
        if agent_name.lower() == 'cto':
            return self.cto.run_cto_tasks(topic)
        elif agent_name.lower() == 'cmo':
            return self.cmo.run_cmo_tasks(topic)
        elif agent_name.lower() == 'cfo':
            return self.cfo.run_cfo_tasks(f"Single agent execution: {agent_name}", {'topic': topic})
        elif agent_name.lower() == 'publisher':
            from agents.publisher_agent import PublisherAgent
            import glob
            import os
            publisher = PublisherAgent()
            # Find latest book file
            book_files = glob.glob("output/*.kpf") + glob.glob("output/*.docx")
            if book_files:
                latest_file = max(book_files, key=os.path.getmtime)
                return publisher.publish_to_kdp(latest_file)
            else:
                return {'success': False, 'error': 'No book files found to publish'}
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report"""
        self.logger.info("📊 Generating summary report...")
        return self.cfo.generate_summary_report()
    
    def _count_generated_files(self, cto_result: Dict, cmo_result: Dict) -> int:
        """Count total files generated across all agents"""
        count = 0
        
        # Count CTO files
        if cto_result.get('success'):
            cto_content = cto_result.get('content', {})
            count += 1  # outline
            count += len(cto_content.get('chapters', []))  # chapters
            count += 1  # summary
        
        # Count CMO files
        if cmo_result.get('success'):
            cmo_content = cmo_result.get('content', {})
            count += len(cmo_content.get('blog_posts', []))  # blog posts
            count += len(cmo_content.get('social_posts', {}).keys())  # social platforms
            count += 1  # strategy
        
        return count
    
    def _print_mission_summary(self, results: Dict[str, Any]):
        """Print detailed mission summary"""
        print("\n" + "🎯 MISSION SUMMARY" + "\n" + "=" * 50)
        
        # Agent summaries
        for agent_name, agent_result in results['agents_results'].items():
            status = "✅ SUCCESS" if agent_result.get('success') else "❌ FAILED"
            duration = agent_result.get('duration', 0)
            print(f"{agent_name.upper()}: {status} (Duration: {duration:.2f}s)")
            
            if not agent_result.get('success') and 'error' in agent_result:
                print(f"  Error: {agent_result['error']}")
        
        # File locations
        print(f"\n📁 OUTPUT LOCATIONS:")
        if 'cto' in results['agents_results'] and results['agents_results']['cto'].get('success'):
            print(f"  📚 Books: {results['agents_results']['cto'].get('output_path', 'N/A')}")
        
        if 'cmo' in results['agents_results'] and results['agents_results']['cmo'].get('success'):
            print(f"  📈 Marketing: {results['agents_results']['cmo'].get('output_path', 'N/A')}")
        
        if 'cfo' in results['agents_results'] and results['agents_results']['cfo'].get('success'):
            print(f"  📊 Analytics: {results['agents_results']['cfo'].get('analytics_file', 'N/A')}")

def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(
        description="Mission Control - AI-Powered Content Creation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mission_control.py "Kid's Puzzle Adventures: The Lost Temple"
  python mission_control.py --agent cto "Space Adventure Stories"
  python mission_control.py --agent cmo "Detective Mystery Book"
  python mission_control.py --summary
        """
    )
    
    parser.add_argument(
        'topic',
        nargs='?',
        default="Kid's Puzzle Adventures: The Lost Temple",
        help='Book topic for content generation (default: "Kid\'s Puzzle Adventures: The Lost Temple")'
    )
    
    parser.add_argument(
        '--agent',
        choices=['cto', 'cmo', 'cfo', 'publisher'],
        help='Run single agent instead of full mission'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate and display summary report'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate system configuration'
    )
    
    args = parser.parse_args()
    
    # Initialize Mission Control
    try:
        mission_control = MissionControl()
    except Exception as e:
        print(f"❌ Failed to initialize Mission Control: {e}")
        print("💡 Check your configuration and API keys")
        sys.exit(1)
    
    # Handle different execution modes
    try:
        if args.validate:
            print("🔍 Validating system configuration...")
            print(f"✅ Gemini API Key: {'Configured' if config.GEMINI_API_KEY else '❌ Missing'}")
            print(f"✅ Output Directories: {'Ready' if config.OUTPUT_DIR.exists() else '❌ Missing'}")
            print(f"✅ Logs Directory: {'Ready' if config.LOGS_DIR.exists() else '❌ Missing'}")
            sys.exit(0)
        
        elif args.summary:
            report = mission_control.generate_summary_report()
            print(report)
        
        elif args.agent:
            print(f"🎯 Running single agent: {args.agent.upper()}")
            result = mission_control.execute_single_agent(args.agent, args.topic)
            
            if result['success']:
                print(f"✅ {args.agent.upper()} agent completed successfully")
            else:
                print(f"❌ {args.agent.upper()} agent failed: {result.get('error', 'Unknown error')}")
        
        else:
            # Full mission execution
            if not args.topic.strip():
                print("❌ Book topic cannot be empty")
                sys.exit(1)
            
            # Validate API key
            if not config.GEMINI_API_KEY:
                print("❌ Gemini API key not configured")
                print("💡 Set GEMINI_API_KEY environment variable")
                sys.exit(1)
            
            print(f"🚀 Starting Mission Control for: '{args.topic}'")
            result = mission_control.execute_full_mission(args.topic)
            
            # Exit with appropriate code
            sys.exit(0 if result['mission_success'] else 1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Mission Control interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"💥 Mission Control encountered an error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()