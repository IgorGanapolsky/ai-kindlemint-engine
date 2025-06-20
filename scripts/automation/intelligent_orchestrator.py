#!/usr/bin/env python3
"""
Intelligent Orchestrator with State-Checking Logic
Prevents duplicate work by checking portfolio state before generation
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from security import safe_command

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger
from scripts.portfolio_state_checker import PortfolioStateChecker

class IntelligentOrchestrator:
    def __init__(self):
        self.logger = get_logger('intelligent_orchestrator')
        self.state_checker = PortfolioStateChecker()
        
    def orchestrate_book_generation(self, series_name, target_volumes=None, force_regenerate=False):
        """
        Intelligently orchestrate book generation with state checking
        """
        self.logger.info(f"🧠 Starting intelligent orchestration for: {series_name}")
        
        if target_volumes:
            volumes_to_process = target_volumes
        else:
            # Find next volume that needs generation
            next_vol = self.state_checker.get_next_volume_to_generate(series_name, 10)
            if next_vol is None:
                self.logger.info("✅ All volumes already complete - no work needed")
                return True
            volumes_to_process = [next_vol]
        
        generated_count = 0
        skipped_count = 0
        
        for vol_num in volumes_to_process:
            self.logger.info(f"🔍 Checking state for Volume {vol_num}...")
            
            # MANDATORY STATE CHECK - This prevents all duplication
            state = self.state_checker.check_volume_state(series_name, vol_num)
            
            if state['already_exists'] and not force_regenerate:
                self.logger.info(f"⏭️ Skipping Volume {vol_num} - work already complete ({state['status']})")
                skipped_count += 1
                continue
            
            # Volume needs generation
            self.logger.info(f"🚀 Generating Volume {vol_num}...")
            
            # Update state to IN_PROGRESS
            self.state_checker.update_volume_state(
                series_name, vol_num, 'GENERATING',
                {'StartTime': datetime.now().isoformat()}
            )
            
            try:
                # Generate the volume
                success = self._generate_volume(series_name, vol_num)
                
                if success:
                    # Update state to GENERATED
                    self.state_checker.update_volume_state(
                        series_name, vol_num, 'GENERATED',
                        {'CompletionTime': datetime.now().isoformat()}
                    )
                    generated_count += 1
                    self.logger.info(f"✅ Volume {vol_num} generated successfully")
                else:
                    # Update state to FAILED
                    self.state_checker.update_volume_state(
                        series_name, vol_num, 'GENERATION_FAILED',
                        {'FailureTime': datetime.now().isoformat()}
                    )
                    self.logger.error(f"❌ Volume {vol_num} generation failed")
                    
            except Exception as e:
                self.logger.error(f"❌ Exception generating Volume {vol_num}: {e}")
                self.state_checker.update_volume_state(
                    series_name, vol_num, 'GENERATION_ERROR',
                    {'ErrorTime': datetime.now().isoformat(), 'Error': str(e)}
                )
        
        # Report results
        self.logger.info(f"📊 Orchestration complete: {generated_count} generated, {skipped_count} skipped")
        return generated_count > 0 or skipped_count > 0
    
    def _generate_volume(self, series_name, vol_num):
        """Generate a single volume using existing scripts"""
        try:
            # Import and use existing generation logic
            import subprocess
            
            # Convert series name to script format
            if "crossword" in series_name.lower():
                # Use existing Gemini generation script
                cmd = [
                    'python', 'scripts/generate_with_gemini.py',
                    '--volume', str(vol_num)
                ]
                
                result = safe_command.run(subprocess.run, cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Volume {vol_num} content generated")
                    
                    # Generate professional cover using new two-stage pipeline
                    self._generate_professional_cover(vol_num)
                    
                    return True
                else:
                    self.logger.error(f"❌ Generation failed: {result.stderr}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Generation exception: {e}")
            return False
    
    def _generate_professional_cover(self, vol_num):
        """Generate professional cover using new two-stage pipeline"""
        try:
            self.logger.info(f"🎨 Generating professional two-stage cover for Volume {vol_num}")
            
            # Use new professional cover generator
            import subprocess
            result = subprocess.run([
                'python', 'scripts/professional_cover_generator.py',
                '--volume', str(vol_num), '--force'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Professional cover generated for Volume {vol_num}")
            else:
                self.logger.warning(f"⚠️ Professional cover generation failed for Volume {vol_num}: {result.stderr}")
                
                # Fallback to old method if new one fails
                self.logger.info(f"🔄 Attempting fallback cover generation...")
                fallback_result = subprocess.run([
                    'python', 'scripts/generate_dalle_covers.py',
                    '--volume', str(vol_num)
                ], capture_output=True, text=True)
                
                if fallback_result.returncode == 0:
                    self.logger.info(f"✅ Fallback cover generated for Volume {vol_num}")
                else:
                    self.logger.error(f"❌ All cover generation methods failed for Volume {vol_num}")
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Professional cover generation failed: {e}")

def main():
    """Main orchestrator function"""
    parser = argparse.ArgumentParser(description='Intelligent Book Generation Orchestrator')
    parser.add_argument('--series', type=str, default='Large_Print_Crossword_Masters', 
                       help='Series name to generate')
    parser.add_argument('--volumes', type=str, help='Specific volumes to generate (comma-separated)')
    parser.add_argument('--force', action='store_true', help='Force regeneration even if exists')
    
    args = parser.parse_args()
    
    # Parse volumes if specified
    target_volumes = None
    if args.volumes:
        try:
            target_volumes = [int(v.strip()) for v in args.volumes.split(',')]
        except:
            print("❌ Invalid volumes format. Use comma-separated numbers like: 1,2,3")
            return False
    
    print("=" * 60)
    print("🧠 INTELLIGENT ORCHESTRATOR WITH STATE CHECKING")
    print("=" * 60)
    print(f"📚 Series: {args.series}")
    print(f"🎯 Volumes: {target_volumes or 'Auto-detect next'}")
    print(f"🔄 Force: {args.force}")
    print("=" * 60)
    
    orchestrator = IntelligentOrchestrator()
    success = orchestrator.orchestrate_book_generation(
        args.series, target_volumes, args.force
    )
    
    print("=" * 60)
    if success:
        print("🎉 ORCHESTRATION COMPLETED SUCCESSFULLY")
    else:
        print("❌ ORCHESTRATION FAILED")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
