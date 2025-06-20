#!/usr/bin/env python3
"""
Portfolio State Checker - Prevents duplicate work by checking DynamoDB state
"""

import os
import sys
import json
import boto3
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

class PortfolioStateChecker:
    def __init__(self):
        self.logger = get_logger('portfolio_state_checker')
        self.logger.info(f"📋 CLASS INIT: PortfolioStateChecker starting initialization")
        
        # Initialize DynamoDB
        self.logger.debug(f"☁️ EXTERNAL INIT: Attempting DynamoDB connection to region 'us-east-1'")
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.portfolio_table = self.dynamodb.Table('kindlemint-portfolio')
            self.logger.info(f"✅ SUCCESS: DynamoDB connection established to 'kindlemint-portfolio' table")
        except Exception as e:
            self.logger.warning(f"⚠️ FALLBACK: DynamoDB connection failed: {e}")
            self.logger.warning(f"⚠️ IMPACT: Will operate in local-only mode (no remote state tracking)")
            self.dynamodb = None
            self.portfolio_table = None
        
        self.logger.info(f"✅ CLASS INIT COMPLETE: PortfolioStateChecker ready for operations")
    
    def check_volume_state(self, series_name, volume_number):
        """Check if a volume has already been processed"""
        self.logger.info(f"📋 FUNCTION ENTRY: check_volume_state(series={series_name}, volume={volume_number})")
        
        # First check local files for immediate feedback
        self.logger.info(f"🔍 DECISION POINT: Checking local file state first for immediate feedback")
        local_state = self._check_local_state(series_name, volume_number)
        self.logger.debug(f"📁 Local state check result: {local_state}")
        
        if local_state['already_exists']:
            self.logger.info(f"✅ SUCCESS: Volume {volume_number} already exists locally: {local_state['status']}")
            self.logger.info(f"📤 FUNCTION EXIT: check_volume_state -> existing local volume")
            return local_state
        
        # Then check DynamoDB if available
        self.logger.info(f"🔍 DECISION POINT: Local check negative, proceeding to DynamoDB check")
        if self.portfolio_table:
            self.logger.debug(f"☁️ DynamoDB connection available, checking remote state")
            dynamo_state = self._check_dynamodb_state(series_name, volume_number)
            self.logger.debug(f"☁️ DynamoDB state check result: {dynamo_state}")
            
            if dynamo_state['already_exists']:
                self.logger.info(f"✅ SUCCESS: Volume {volume_number} already tracked in DynamoDB: {dynamo_state['status']}")
                self.logger.info(f"📤 FUNCTION EXIT: check_volume_state -> existing DynamoDB volume")
                return dynamo_state
        else:
            self.logger.warning(f"⚠️ DynamoDB not available - cannot check remote state")
        
        # Volume is safe to generate
        result = {
            'already_exists': False,
            'status': 'READY_TO_GENERATE',
            'source': 'new',
            'message': f'Volume {volume_number} ready for generation'
        }
        self.logger.info(f"✅ SUCCESS: Volume {volume_number} ready for generation - no conflicts found")
        self.logger.info(f"📤 FUNCTION EXIT: check_volume_state -> ready to generate")
        return result
    
    def _check_local_state(self, series_name, volume_number):
        """Check local file system for existing volumes"""
        self.logger.debug(f"📋 FUNCTION ENTRY: _check_local_state(series={series_name}, volume={volume_number})")
        
        books_dir = Path("output/generated_books")
        self.logger.debug(f"📁 FILE OPERATION: Checking directory existence: {books_dir}")
        
        if not books_dir.exists():
            self.logger.info(f"📁 NO LOCAL FILES: Directory {books_dir} does not exist")
            result = {'already_exists': False, 'status': 'NO_LOCAL_FILES', 'source': 'local'}
            self.logger.debug(f"📤 FUNCTION EXIT: _check_local_state -> {result}")
            return result
        
        # Look for volume folders
        self.logger.debug(f"🔍 DECISION POINT: Scanning for volume folders matching pattern 'vol_{volume_number}_final'")
        try:
            all_folders = list(books_dir.iterdir())
            self.logger.debug(f"📁 FILE OPERATION: Found {len(all_folders)} total items in {books_dir}")
            
            volume_folders = [f for f in all_folders 
                             if f.is_dir() and f"vol_{volume_number}_final" in f.name.lower()]
            self.logger.debug(f"🔍 SEARCH RESULT: Found {len(volume_folders)} matching volume folders")
            
        except Exception as e:
            self.logger.error(f"❌ ERROR: Failed to scan books directory: {e}")
            return {'already_exists': False, 'status': 'SCAN_ERROR', 'source': 'local'}
        
        if volume_folders:
            vol_folder = volume_folders[0]
            self.logger.info(f"📁 FOUND: Volume folder at {vol_folder}")
            
            # Check completeness
            required_files = ['manuscript.txt', 'metadata.json']
            self.logger.debug(f"🔍 DECISION POINT: Checking for required files: {required_files}")
            
            file_status = {}
            for file in required_files:
                file_path = vol_folder / file
                exists = file_path.exists()
                file_status[file] = exists
                self.logger.debug(f"📁 FILE CHECK: {file} -> {'EXISTS' if exists else 'MISSING'} at {file_path}")
            
            has_all_files = all(file_status.values())
            self.logger.debug(f"📊 FILE COMPLETENESS: {sum(file_status.values())}/{len(required_files)} required files present")
            
            # Check for cover files
            self.logger.debug(f"🔍 DECISION POINT: Checking for cover files with pattern 'cover_vol_*.png'")
            try:
                cover_files = list(vol_folder.glob('cover_vol_*.png'))
                has_cover = len(cover_files) > 0
                self.logger.debug(f"🎨 COVER CHECK: Found {len(cover_files)} cover files")
            except Exception as e:
                self.logger.warning(f"⚠️ WARNING: Failed to check cover files: {e}")
                has_cover = False
            
            # Determine status based on completeness
            if has_all_files and has_cover:
                status = 'GENERATED'
                self.logger.info(f"✅ COMPLETE: Volume {volume_number} has all required files and cover")
            elif has_all_files:
                status = 'PARTIAL_GENERATED'
                self.logger.warning(f"⚠️ PARTIAL: Volume {volume_number} has manuscript but missing cover")
            else:
                status = 'INCOMPLETE'
                missing_files = [f for f, exists in file_status.items() if not exists]
                self.logger.warning(f"⚠️ INCOMPLETE: Volume {volume_number} missing files: {missing_files}")
            
            result = {
                'already_exists': True,
                'status': status,
                'source': 'local',
                'folder_path': str(vol_folder),
                'message': f'Volume {volume_number} found locally with status: {status}',
                'file_details': file_status,
                'cover_count': len(cover_files) if 'cover_files' in locals() else 0
            }
            self.logger.debug(f"📤 FUNCTION EXIT: _check_local_state -> {result}")
            return result
        
        self.logger.info(f"🔍 NOT FOUND: No volume folders found for volume {volume_number}")
        result = {'already_exists': False, 'status': 'NOT_FOUND_LOCALLY', 'source': 'local'}
        self.logger.debug(f"📤 FUNCTION EXIT: _check_local_state -> {result}")
        return result
    
    def _check_dynamodb_state(self, series_name, volume_number):
        """Check DynamoDB Portfolio Table for volume state"""
        self.logger.debug(f"📋 FUNCTION ENTRY: _check_dynamodb_state(series={series_name}, volume={volume_number})")
        
        try:
            # Create consistent key for volume lookup
            volume_key = f"{series_name}_Volume_{volume_number}"
            self.logger.debug(f"🔑 KEY GENERATION: Using volume key '{volume_key}' for DynamoDB lookup")
            
            self.logger.debug(f"☁️ EXTERNAL CALL: Querying DynamoDB portfolio table")
            query_params = {
                'BookId': volume_key,
                'SeriesName': series_name
            }
            self.logger.debug(f"📊 QUERY PARAMS: {query_params}")
            
            response = self.portfolio_table.get_item(Key=query_params)
            self.logger.debug(f"☁️ EXTERNAL RESPONSE: DynamoDB returned {len(str(response))} chars")
            
            if 'Item' in response:
                item = response['Item']
                status = item.get('Status', 'UNKNOWN')
                last_updated = item.get('LastUpdated', 'Unknown')
                
                self.logger.info(f"📊 FOUND: Volume {volume_number} exists in portfolio with status '{status}'")
                self.logger.debug(f"📅 LAST UPDATED: {last_updated}")
                
                # Business rule: Don't generate if already in progress or complete
                blocking_statuses = ['GENERATED', 'PUBLISHING', 'PUBLISHED', 'LIVE']
                self.logger.debug(f"🔍 DECISION POINT: Checking if status '{status}' is in blocking list: {blocking_statuses}")
                
                if status in blocking_statuses:
                    self.logger.info(f"🚫 BLOCKED: Volume {volume_number} status '{status}' prevents regeneration")
                    result = {
                        'already_exists': True,
                        'status': status,
                        'source': 'dynamodb',
                        'last_updated': last_updated,
                        'message': f'Volume {volume_number} already {status.lower()} in portfolio',
                        'item_details': item
                    }
                    self.logger.debug(f"📤 FUNCTION EXIT: _check_dynamodb_state -> {result}")
                    return result
                else:
                    self.logger.info(f"✅ ALLOWED: Volume {volume_number} status '{status}' allows regeneration")
            else:
                self.logger.info(f"🔍 NOT FOUND: Volume {volume_number} not found in DynamoDB portfolio")
            
            result = {'already_exists': False, 'status': 'NOT_IN_PORTFOLIO', 'source': 'dynamodb'}
            self.logger.debug(f"📤 FUNCTION EXIT: _check_dynamodb_state -> {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ERROR: DynamoDB query failed with exception: {e}")
            self.logger.error(f"❌ ERROR DETAILS: Query attempted for series='{series_name}', volume={volume_number}")
            result = {'already_exists': False, 'status': 'DYNAMODB_ERROR', 'source': 'dynamodb', 'error': str(e)}
            self.logger.debug(f"📤 FUNCTION EXIT: _check_dynamodb_state -> {result}")
            return result
    
    def update_volume_state(self, series_name, volume_number, status, metadata=None):
        """Update volume state in DynamoDB"""
        self.logger.info(f"📋 FUNCTION ENTRY: update_volume_state(series={series_name}, volume={volume_number}, status={status})")
        
        if not self.portfolio_table:
            self.logger.warning("⚠️ BLOCKED: Cannot update state - DynamoDB not available")
            self.logger.info(f"📤 FUNCTION EXIT: update_volume_state -> False (no DynamoDB)")
            return False
        
        try:
            volume_key = f"{series_name}_Volume_{volume_number}"
            self.logger.debug(f"🔑 KEY GENERATION: Using volume key '{volume_key}' for DynamoDB update")
            
            # Build item for DynamoDB
            item = {
                'BookId': volume_key,
                'SeriesName': series_name,
                'VolumeNumber': volume_number,
                'Status': status,
                'LastUpdated': datetime.now().isoformat(),
                'UpdatedBy': 'autonomous_system'
            }
            
            if metadata:
                self.logger.debug(f"📊 METADATA: Adding {len(metadata)} metadata fields")
                item.update(metadata)
            
            self.logger.debug(f"📊 ITEM TO SAVE: {len(str(item))} chars with keys: {list(item.keys())}")
            
            self.logger.debug(f"☁️ EXTERNAL CALL: Writing to DynamoDB portfolio table")
            self.portfolio_table.put_item(Item=item)
            
            self.logger.info(f"✅ SUCCESS: Updated Volume {volume_number} status to '{status}' in DynamoDB")
            self.logger.debug(f"📅 TIMESTAMP: Last updated set to {item['LastUpdated']}")
            self.logger.info(f"📤 FUNCTION EXIT: update_volume_state -> True")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERROR: Failed to update portfolio state with exception: {e}")
            self.logger.error(f"❌ ERROR DETAILS: Attempted to update series='{series_name}', volume={volume_number}, status='{status}'")
            self.logger.info(f"📤 FUNCTION EXIT: update_volume_state -> False (error)")
            return False
    
    def get_next_volume_to_generate(self, series_name, max_volumes=10):
        """Find the next volume number that needs to be generated"""
        self.logger.info(f"📋 FUNCTION ENTRY: get_next_volume_to_generate(series={series_name}, max={max_volumes})")
        
        self.logger.info(f"🎯 SEARCH STRATEGY: Scanning volumes 1-{max_volumes} to find first available slot")
        
        for vol_num in range(1, max_volumes + 1):
            self.logger.debug(f"🔍 CHECKING: Volume {vol_num} of {max_volumes}")
            state = self.check_volume_state(series_name, vol_num)
            
            if not state['already_exists']:
                self.logger.info(f"🎯 SUCCESS: Found next volume to generate: {vol_num}")
                self.logger.info(f"✅ DECISION: Volume {vol_num} is available and ready for generation")
                self.logger.info(f"📤 FUNCTION EXIT: get_next_volume_to_generate -> {vol_num}")
                return vol_num
            else:
                self.logger.info(f"⏭️ SKIPPING: Volume {vol_num} - {state['message']}")
                self.logger.debug(f"📊 SKIP REASON: Status={state['status']}, Source={state['source']}")
        
        self.logger.warning(f"⚠️ NO VOLUMES AVAILABLE: All volumes 1-{max_volumes} already exist for {series_name}")
        self.logger.info(f"🏁 COMPLETION: Series appears to be fully generated")
        self.logger.info(f"📤 FUNCTION EXIT: get_next_volume_to_generate -> None")
        return None

def main():
    """Test the state checker"""
    logger = get_logger('portfolio_state_checker_main')
    logger.info(f"📋 MAIN FUNCTION ENTRY: Starting portfolio state checker test")
    
    try:
        checker = PortfolioStateChecker()
        
        # Test current series
        series_name = "Large_Print_Crossword_Masters"
        logger.info(f"📊 TEST PARAMETERS: series_name='{series_name}', volume_range=1-5")
        
        print("=" * 60)
        print("🔍 PORTFOLIO STATE CHECKER")
        print("=" * 60)
        
        # Check all volumes
        logger.info(f"🔍 STARTING: Individual volume state checks for series '{series_name}'")
        for vol_num in range(1, 6):
            logger.debug(f"🔍 CHECKING: Volume {vol_num} state")
            state = checker.check_volume_state(series_name, vol_num)
            status_icon = "✅" if state['already_exists'] else "🆕"
            print(f"{status_icon} Volume {vol_num}: {state['status']} ({state['source']})")
            logger.debug(f"📊 RESULT: Volume {vol_num} -> {state['status']} from {state['source']}")
        
        # Find next volume to generate
        logger.info(f"🎯 FINDING: Next available volume to generate")
        next_vol = checker.get_next_volume_to_generate(series_name, 10)
        if next_vol:
            print(f"\n🎯 Next volume to generate: {next_vol}")
            logger.info(f"✅ SUCCESS: Found next volume to generate: {next_vol}")
        else:
            print(f"\n✅ All volumes complete for {series_name}")
            logger.info(f"🏁 COMPLETE: All volumes already exist for series '{series_name}'")
        
        print("=" * 60)
        logger.info(f"✅ SUCCESS: Portfolio state checker test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ERROR: Main function failed with exception: {e}")
        print(f"\n❌ Error: {e}")
        raise
    finally:
        logger.info(f"📤 MAIN FUNCTION EXIT: Portfolio state checker test finished")

if __name__ == "__main__":
    main()