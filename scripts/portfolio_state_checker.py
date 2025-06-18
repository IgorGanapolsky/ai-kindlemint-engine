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
        
        # Initialize DynamoDB
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.portfolio_table = self.dynamodb.Table('kindlemint-portfolio')
        except Exception as e:
            self.logger.warning(f"⚠️ DynamoDB connection failed: {e}")
            self.dynamodb = None
            self.portfolio_table = None
    
    def check_volume_state(self, series_name, volume_number):
        """Check if a volume has already been processed"""
        
        # First check local files for immediate feedback
        local_state = self._check_local_state(series_name, volume_number)
        if local_state['already_exists']:
            self.logger.info(f"📁 Volume {volume_number} already exists locally: {local_state['status']}")
            return local_state
        
        # Then check DynamoDB if available
        if self.portfolio_table:
            dynamo_state = self._check_dynamodb_state(series_name, volume_number)
            if dynamo_state['already_exists']:
                self.logger.info(f"☁️ Volume {volume_number} already tracked in DynamoDB: {dynamo_state['status']}")
                return dynamo_state
        
        # Volume is safe to generate
        return {
            'already_exists': False,
            'status': 'READY_TO_GENERATE',
            'source': 'new',
            'message': f'Volume {volume_number} ready for generation'
        }
    
    def _check_local_state(self, series_name, volume_number):
        """Check local file system for existing volumes"""
        books_dir = Path("output/generated_books")
        
        if not books_dir.exists():
            return {'already_exists': False, 'status': 'NO_LOCAL_FILES', 'source': 'local'}
        
        # Look for volume folders
        volume_folders = [f for f in books_dir.iterdir() 
                         if f.is_dir() and f"vol_{volume_number}_final" in f.name.lower()]
        
        if volume_folders:
            vol_folder = volume_folders[0]
            
            # Check completeness
            required_files = ['manuscript.txt', 'metadata.json']
            cover_files = list(vol_folder.glob('cover_vol_*.png'))
            
            has_all_files = all((vol_folder / file).exists() for file in required_files)
            has_cover = len(cover_files) > 0
            
            if has_all_files and has_cover:
                status = 'GENERATED'
            elif has_all_files:
                status = 'PARTIAL_GENERATED'
            else:
                status = 'INCOMPLETE'
            
            return {
                'already_exists': True,
                'status': status,
                'source': 'local',
                'folder_path': str(vol_folder),
                'message': f'Volume {volume_number} found locally with status: {status}'
            }
        
        return {'already_exists': False, 'status': 'NOT_FOUND_LOCALLY', 'source': 'local'}
    
    def _check_dynamodb_state(self, series_name, volume_number):
        """Check DynamoDB Portfolio Table for volume state"""
        try:
            # Create consistent key for volume lookup
            volume_key = f"{series_name}_Volume_{volume_number}"
            
            response = self.portfolio_table.get_item(
                Key={
                    'BookId': volume_key,
                    'SeriesName': series_name
                }
            )
            
            if 'Item' in response:
                item = response['Item']
                status = item.get('Status', 'UNKNOWN')
                
                # Don't generate if already in progress or complete
                if status in ['GENERATED', 'PUBLISHING', 'PUBLISHED', 'LIVE']:
                    return {
                        'already_exists': True,
                        'status': status,
                        'source': 'dynamodb',
                        'last_updated': item.get('LastUpdated', 'Unknown'),
                        'message': f'Volume {volume_number} already {status.lower()} in portfolio'
                    }
            
            return {'already_exists': False, 'status': 'NOT_IN_PORTFOLIO', 'source': 'dynamodb'}
            
        except Exception as e:
            self.logger.error(f"❌ DynamoDB query failed: {e}")
            return {'already_exists': False, 'status': 'DYNAMODB_ERROR', 'source': 'dynamodb'}
    
    def update_volume_state(self, series_name, volume_number, status, metadata=None):
        """Update volume state in DynamoDB"""
        if not self.portfolio_table:
            self.logger.warning("⚠️ Cannot update state - DynamoDB not available")
            return False
        
        try:
            volume_key = f"{series_name}_Volume_{volume_number}"
            
            item = {
                'BookId': volume_key,
                'SeriesName': series_name,
                'VolumeNumber': volume_number,
                'Status': status,
                'LastUpdated': datetime.now().isoformat(),
                'UpdatedBy': 'autonomous_system'
            }
            
            if metadata:
                item.update(metadata)
            
            self.portfolio_table.put_item(Item=item)
            self.logger.info(f"✅ Updated Volume {volume_number} status to: {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update portfolio state: {e}")
            return False
    
    def get_next_volume_to_generate(self, series_name, max_volumes=10):
        """Find the next volume number that needs to be generated"""
        
        for vol_num in range(1, max_volumes + 1):
            state = self.check_volume_state(series_name, vol_num)
            
            if not state['already_exists']:
                self.logger.info(f"🎯 Next volume to generate: {vol_num}")
                return vol_num
            else:
                self.logger.info(f"⏭️ Skipping Volume {vol_num} - {state['message']}")
        
        self.logger.warning(f"⚠️ All volumes 1-{max_volumes} already exist for {series_name}")
        return None

def main():
    """Test the state checker"""
    checker = PortfolioStateChecker()
    
    # Test current series
    series_name = "Large_Print_Crossword_Masters"
    
    print("=" * 60)
    print("🔍 PORTFOLIO STATE CHECKER")
    print("=" * 60)
    
    # Check all volumes
    for vol_num in range(1, 6):
        state = checker.check_volume_state(series_name, vol_num)
        status_icon = "✅" if state['already_exists'] else "🆕"
        print(f"{status_icon} Volume {vol_num}: {state['status']} ({state['source']})")
    
    # Find next volume to generate
    next_vol = checker.get_next_volume_to_generate(series_name, 10)
    if next_vol:
        print(f"\n🎯 Next volume to generate: {next_vol}")
    else:
        print(f"\n✅ All volumes complete for {series_name}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()