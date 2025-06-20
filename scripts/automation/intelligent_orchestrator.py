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
        self.logger.info(f"📋 CLASS INIT: IntelligentOrchestrator starting initialization")
        
        self.logger.debug(f"🔗 DEPENDENCY: Creating PortfolioStateChecker instance")
        self.state_checker = PortfolioStateChecker()
        
        self.logger.info(f"✅ CLASS INIT COMPLETE: IntelligentOrchestrator ready for book generation orchestration")
        
    def orchestrate_book_generation(self, series_name, target_volumes=None, force_regenerate=False):
        """
        Intelligently orchestrate book generation with state checking
        """
        self.logger.info(f"📋 FUNCTION ENTRY: orchestrate_book_generation(series='{series_name}', target={target_volumes}, force={force_regenerate})")
        self.logger.info(f"🧠 ORCHESTRATION: Starting intelligent orchestration for series: {series_name}")
        
        # Determine volumes to process
        if target_volumes:
            volumes_to_process = target_volumes
            self.logger.info(f"🎯 TARGET VOLUMES: Processing specific volumes: {target_volumes}")
        else:
            # Find next volume that needs generation
            self.logger.debug(f"🔍 AUTO-DETECT: Finding next volume that needs generation")
            next_vol = self.state_checker.get_next_volume_to_generate(series_name, 10)
            if next_vol is None:
                self.logger.info("✅ COMPLETE: All volumes already complete - no work needed")
                self.logger.info(f"📤 FUNCTION EXIT: orchestrate_book_generation() -> True (no work needed)")
                return True
            volumes_to_process = [next_vol]
            self.logger.info(f"🎯 AUTO-SELECTED: Will process volume {next_vol}")
        
        generated_count = 0
        skipped_count = 0
        
        self.logger.info(f"🔄 PROCESSING: Will process {len(volumes_to_process)} volumes: {volumes_to_process}")
        
        for i, vol_num in enumerate(volumes_to_process, 1):
            self.logger.info(f"🔍 VOLUME CHECK: [{i}/{len(volumes_to_process)}] Checking state for Volume {vol_num}")
            
            # MANDATORY STATE CHECK - This prevents all duplication
            self.logger.debug(f"🚫 DUPLICATION PREVENTION: Running mandatory state check")
            state = self.state_checker.check_volume_state(series_name, vol_num)
            self.logger.debug(f"📊 STATE RESULT: Volume {vol_num} -> {state['status']} from {state['source']}")
            
            if state['already_exists'] and not force_regenerate:
                self.logger.info(f"⏭️ SKIPPING: Volume {vol_num} - work already complete ({state['status']})")
                self.logger.debug(f"🔍 SKIP REASON: already_exists=True, force_regenerate={force_regenerate}")
                skipped_count += 1
                continue
            
            # Volume needs generation
            self.logger.info(f"🚀 GENERATION: Starting generation for Volume {vol_num}")
            
            # Update state to IN_PROGRESS
            start_time = datetime.now().isoformat()
            self.logger.debug(f"📊 STATE UPDATE: Marking Volume {vol_num} as GENERATING")
            self.state_checker.update_volume_state(
                series_name, vol_num, 'GENERATING',
                {'StartTime': start_time}
            )
            
            try:
                # Generate the volume
                self.logger.debug(f"🎯 DELEGATING: Calling _generate_volume for Volume {vol_num}")
                success = self._generate_volume(series_name, vol_num)
                
                if success:
                    # Update state to GENERATED
                    completion_time = datetime.now().isoformat()
                    self.logger.debug(f"📊 STATE UPDATE: Marking Volume {vol_num} as GENERATED")
                    self.state_checker.update_volume_state(
                        series_name, vol_num, 'GENERATED',
                        {'CompletionTime': completion_time, 'StartTime': start_time}
                    )
                    generated_count += 1
                    self.logger.info(f"✅ SUCCESS: Volume {vol_num} generated successfully")
                else:
                    # Update state to FAILED
                    failure_time = datetime.now().isoformat()
                    self.logger.error(f"❌ GENERATION FAILED: Volume {vol_num} generation failed")
                    self.state_checker.update_volume_state(
                        series_name, vol_num, 'GENERATION_FAILED',
                        {'FailureTime': failure_time, 'StartTime': start_time}
                    )
                    
            except Exception as e:
                self.logger.error(f"❌ EXCEPTION: Exception generating Volume {vol_num}: {e}")
                error_time = datetime.now().isoformat()
                self.state_checker.update_volume_state(
                    series_name, vol_num, 'GENERATION_ERROR',
                    {'ErrorTime': error_time, 'StartTime': start_time, 'Error': str(e)}
                )
        
        # Report results
        total_processed = generated_count + skipped_count
        self.logger.info(f"📊 ORCHESTRATION COMPLETE: {generated_count} generated, {skipped_count} skipped, {total_processed} total")
        
        success = generated_count > 0 or skipped_count > 0
        self.logger.debug(f"🔍 SUCCESS CRITERIA: generated_count={generated_count} OR skipped_count={skipped_count} -> {success}")
        self.logger.info(f"📤 FUNCTION EXIT: orchestrate_book_generation() -> {success}")
        return success
    
    def _generate_volume(self, series_name, vol_num):
        """Generate a single volume using existing scripts"""
        self.logger.debug(f"📋 FUNCTION ENTRY: _generate_volume(series='{series_name}', volume={vol_num})")
        
        try:
            # Import and use existing generation logic
            self.logger.debug(f"📦 IMPORT: Loading subprocess module for script execution")
            import subprocess
            
            # Convert series name to script format
            self.logger.debug(f"🔍 SCRIPT SELECTION: Determining generation script for series '{series_name}'")
            if "crossword" in series_name.lower():
                # Use existing Gemini generation script
                cmd = [
                    'python', 'scripts/generate_with_gemini.py',
                    '--volume', str(vol_num)
                ]
                self.logger.info(f"📝 CONTENT GENERATION: Using Gemini script for crossword content")
                self.logger.debug(f"💻 COMMAND: {' '.join(cmd)}")
                
                self.logger.debug(f"🚀 EXTERNAL CALL: Executing content generation script")
                result = safe_command.run(subprocess.run, cmd, capture_output=True, text=True)
                
                self.logger.debug(f"📊 SCRIPT RESULT: Return code {result.returncode}")
                if result.returncode == 0:
                    self.logger.info(f"✅ CONTENT SUCCESS: Volume {vol_num} content generated successfully")
                    
                    # Generate professional cover using new two-stage pipeline
                    self.logger.debug(f"🎨 COVER GENERATION: Starting cover generation for Volume {vol_num}")
                    self._generate_professional_cover(vol_num)
                    
                    self.logger.debug(f"📤 FUNCTION EXIT: _generate_volume() -> True")
                    return True
                else:
                    self.logger.error(f"❌ SCRIPT FAILED: Generation script failed with return code {result.returncode}")
                    self.logger.error(f"❌ STDERR: {result.stderr[:500]}..." if result.stderr else "No stderr output")
                    self.logger.debug(f"📤 FUNCTION EXIT: _generate_volume() -> False")
                    return False
            else:
                self.logger.error(f"❌ UNSUPPORTED: No generation script available for series type '{series_name}'")
                self.logger.debug(f"📤 FUNCTION EXIT: _generate_volume() -> False (unsupported)")
                return False
                    
        except Exception as e:
            self.logger.error(f"❌ EXCEPTION: Generation exception: {e}")
            self.logger.error(f"❌ ERROR DETAILS: Exception during volume generation for series '{series_name}', volume {vol_num}")
            self.logger.debug(f"📤 FUNCTION EXIT: _generate_volume() -> False (exception)")
            return False
    
    def _generate_professional_cover(self, vol_num):
        """Generate professional cover using new two-stage pipeline"""
        self.logger.debug(f"📋 FUNCTION ENTRY: _generate_professional_cover(volume={vol_num})")
        
        try:
            self.logger.info(f"🎨 COVER GENERATION: Generating professional two-stage cover for Volume {vol_num}")
            
            # Use new professional cover generator
            import subprocess
            primary_cmd = [
                'python', 'scripts/professional_cover_generator.py',
                '--volume', str(vol_num), '--force'
            ]
            self.logger.debug(f"💻 PRIMARY COMMAND: {' '.join(primary_cmd)}")
            
            self.logger.debug(f"🚀 EXTERNAL CALL: Executing professional cover generator")
            result = subprocess.run(primary_cmd, capture_output=True, text=True)
            
            self.logger.debug(f"📊 PRIMARY RESULT: Return code {result.returncode}")
            if result.returncode == 0:
                self.logger.info(f"✅ COVER SUCCESS: Professional cover generated for Volume {vol_num}")
                self.logger.debug(f"📤 FUNCTION EXIT: _generate_professional_cover() -> success")
            else:
                self.logger.warning(f"⚠️ PRIMARY FAILED: Professional cover generation failed for Volume {vol_num}")
                self.logger.debug(f"⚠️ PRIMARY STDERR: {result.stderr[:300]}..." if result.stderr else "No stderr")
                
                # Fallback to old method if new one fails
                self.logger.info(f"🔄 FALLBACK: Attempting fallback cover generation")
                fallback_cmd = [
                    'python', 'scripts/generate_dalle_covers.py',
                    '--volume', str(vol_num)
                ]
                self.logger.debug(f"💻 FALLBACK COMMAND: {' '.join(fallback_cmd)}")
                
                fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)
                
                self.logger.debug(f"📊 FALLBACK RESULT: Return code {fallback_result.returncode}")
                if fallback_result.returncode == 0:
                    self.logger.info(f"✅ FALLBACK SUCCESS: Fallback cover generated for Volume {vol_num}")
                    self.logger.debug(f"📤 FUNCTION EXIT: _generate_professional_cover() -> fallback success")
                else:
                    self.logger.error(f"❌ ALL FAILED: All cover generation methods failed for Volume {vol_num}")
                    self.logger.error(f"❌ FALLBACK STDERR: {fallback_result.stderr[:300]}..." if fallback_result.stderr else "No stderr")
                    self.logger.debug(f"📤 FUNCTION EXIT: _generate_professional_cover() -> all failed")
                        
        except Exception as e:
            self.logger.error(f"❌ EXCEPTION: Professional cover generation failed with exception: {e}")
            self.logger.error(f"❌ ERROR DETAILS: Exception during cover generation for Volume {vol_num}")
            self.logger.debug(f"📤 FUNCTION EXIT: _generate_professional_cover() -> exception")

def main():
    """Main orchestrator function"""
    logger = get_logger('intelligent_orchestrator_main')
    logger.info(f"📋 MAIN FUNCTION ENTRY: Starting intelligent orchestrator main()")
    
    try:
        parser = argparse.ArgumentParser(description='Intelligent Book Generation Orchestrator')
        parser.add_argument('--series', type=str, default='Large_Print_Crossword_Masters', 
                           help='Series name to generate')
        parser.add_argument('--volumes', type=str, help='Specific volumes to generate (comma-separated)')
        parser.add_argument('--force', action='store_true', help='Force regeneration even if exists')
        
        args = parser.parse_args()
        logger.debug(f"📊 CLI ARGS: series='{args.series}', volumes='{args.volumes}', force={args.force}")
        
        # Parse volumes if specified
        target_volumes = None
        if args.volumes:
            logger.debug(f"🔢 VOLUME PARSING: Parsing volume list '{args.volumes}'")
            try:
                target_volumes = [int(v.strip()) for v in args.volumes.split(',')]
                logger.info(f"🎯 VOLUMES PARSED: {target_volumes}")
            except Exception as e:
                logger.error(f"❌ PARSE ERROR: Invalid volumes format '{args.volumes}': {e}")
                print("❌ Invalid volumes format. Use comma-separated numbers like: 1,2,3")
                return False
        
        print("=" * 60)
        print("🧠 INTELLIGENT ORCHESTRATOR WITH STATE CHECKING")
        print("=" * 60)
        print(f"📚 Series: {args.series}")
        print(f"🎯 Volumes: {target_volumes or 'Auto-detect next'}")
        print(f"🔄 Force: {args.force}")
        print("=" * 60)
        
        logger.info(f"🎯 EXECUTION: Starting orchestration with series='{args.series}', volumes={target_volumes}, force={args.force}")
        orchestrator = IntelligentOrchestrator()
        success = orchestrator.orchestrate_book_generation(
            args.series, target_volumes, args.force
        )
        
        print("=" * 60)
        if success:
            print("🎉 ORCHESTRATION COMPLETED SUCCESSFULLY")
            logger.info(f"✅ SUCCESS: Orchestration completed successfully")
        else:
            print("❌ ORCHESTRATION FAILED")
            logger.error(f"❌ FAILURE: Orchestration failed")
        print("=" * 60)
        
        logger.info(f"📤 MAIN FUNCTION EXIT: main() -> {success}")
        return success
        
    except Exception as e:
        logger.error(f"❌ EXCEPTION: Main function failed with exception: {e}")
        print(f"\n❌ Error: {e}")
        logger.info(f"📤 MAIN FUNCTION EXIT: main() -> False (exception)")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
