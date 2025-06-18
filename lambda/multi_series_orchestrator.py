"""
Multi-Series Portfolio Orchestrator - Manages multiple series concurrently
Scans portfolio table and executes appropriate actions for each series
"""
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Multi-Series Orchestrator Lambda handler.
    Runs hourly to manage portfolio of series.
    """
    try:
        logger.info("🏭 MULTI-SERIES ORCHESTRATOR ACTIVATED")
        logger.info(f"Event received: {json.dumps(event, indent=2)}")
        
        # Import dependencies
        from kindlemint.portfolio.portfolio_manager import PortfolioManager, SeriesStatus
        
        # Initialize portfolio manager
        portfolio = PortfolioManager()
        
        # Get all series requiring action
        pending_actions = portfolio.get_pending_actions()
        logger.info(f"📋 Found {len(pending_actions)} series requiring action")
        
        if not pending_actions:
            logger.info("✅ No series require action at this time")
            return create_success_response([], "No actions required")
        
        # Process each series
        execution_results = []
        for series_data in pending_actions:
            try:
                result = process_series_action(series_data, portfolio)
                execution_results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process series {series_data.get('series_id', 'Unknown')}: {e}")
                execution_results.append({
                    'series_id': series_data.get('series_id', 'Unknown'),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate summary
        successful_actions = len([r for r in execution_results if r['status'] == 'success'])
        failed_actions = len(execution_results) - successful_actions
        
        logger.info(f"✅ Portfolio orchestration completed: {successful_actions} success, {failed_actions} failed")
        
        return create_success_response(execution_results, 
                                     f"Processed {len(execution_results)} series actions")
        
    except Exception as e:
        logger.error(f"❌ Multi-series orchestration failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Multi-series orchestration failed: {str(e)}',
                'source': event.get('source', 'scheduled'),
                'version': '3.0'
            })
        }

def process_series_action(series_data: Dict[str, Any], portfolio: PortfolioManager) -> Dict[str, Any]:
    """Process the required action for a specific series."""
    series_id = series_data['series_id']
    current_status = series_data['status']
    
    logger.info(f"🎯 Processing {series_id}: {current_status}")
    
    # Route to appropriate action based on status
    if current_status == SeriesStatus.APPROVED.value:
        return start_volume_1_production(series_data, portfolio)
    
    elif current_status.startswith('PUBLISHING_VOL_'):
        # Extract volume number and proceed to next volume
        volume_num = int(current_status.split('_')[-1])
        if volume_num < 5:
            return start_next_volume_production(series_data, portfolio, volume_num + 1)
        else:
            return complete_series(series_data, portfolio)
    
    elif current_status == SeriesStatus.AWAITING_APPROVAL.value:
        # Skip - requires manual CEO approval
        logger.info(f"⏳ {series_id} awaiting CEO approval - skipping")
        return {
            'series_id': series_id,
            'status': 'skipped',
            'message': 'Awaiting CEO approval'
        }
    
    else:
        logger.warning(f"⚠️ Unknown status for {series_id}: {current_status}")
        return {
            'series_id': series_id,
            'status': 'error', 
            'error': f'Unknown status: {current_status}'
        }

def start_volume_1_production(series_data: Dict[str, Any], portfolio: PortfolioManager) -> Dict[str, Any]:
    """Start Volume 1 production for approved series."""
    series_id = series_data['series_id']
    
    try:
        logger.info(f"📚 Starting Volume 1 production for {series_id}")
        
        # Parse research data
        research_data = json.loads(series_data.get('research_data', '{}'))
        
        # Prepare book generation payload
        book_payload = {
            'series_id': series_id,
            'volume': 1,
            'brand': series_data['brand_name'],
            'niche': series_data['niche_topic'],
            'micro_niche': series_data['micro_niche'],
            'source': 'multi_series_orchestrator',
            'research_data': research_data
        }
        
        # Invoke book generation
        success = invoke_book_generation(book_payload)
        
        if success:
            # Update portfolio status
            portfolio.update_series_status(
                series_id, 
                SeriesStatus.PUBLISHING_VOL_1,
                next_action_hours=24  # Check tomorrow for completion
            )
            
            return {
                'series_id': series_id,
                'status': 'success',
                'action': 'volume_1_started',
                'next_action': 'Check Volume 1 completion in 24 hours'
            }
        else:
            return {
                'series_id': series_id,
                'status': 'error',
                'error': 'Book generation invocation failed'
            }
            
    except Exception as e:
        logger.error(f"Failed to start Volume 1 for {series_id}: {e}")
        return {
            'series_id': series_id,
            'status': 'error',
            'error': str(e)
        }

def start_next_volume_production(series_data: Dict[str, Any], portfolio: PortfolioManager, 
                                volume_num: int) -> Dict[str, Any]:
    """Start production of the next volume in the series."""
    series_id = series_data['series_id']
    
    try:
        logger.info(f"📚 Starting Volume {volume_num} production for {series_id}")
        
        # Parse research data
        research_data = json.loads(series_data.get('research_data', '{}'))
        
        # Prepare book generation payload
        book_payload = {
            'series_id': series_id,
            'volume': volume_num,
            'brand': series_data['brand_name'],
            'niche': series_data['niche_topic'],
            'micro_niche': series_data['micro_niche'],
            'source': 'multi_series_orchestrator',
            'research_data': research_data
        }
        
        # Invoke book generation
        success = invoke_book_generation(book_payload)
        
        if success:
            # Update portfolio status
            new_status = getattr(SeriesStatus, f'PUBLISHING_VOL_{volume_num}')
            portfolio.update_series_status(
                series_id,
                new_status,
                next_action_hours=24  # Check tomorrow for completion
            )
            
            return {
                'series_id': series_id,
                'status': 'success',
                'action': f'volume_{volume_num}_started',
                'next_action': f'Check Volume {volume_num} completion in 24 hours'
            }
        else:
            return {
                'series_id': series_id,
                'status': 'error',
                'error': 'Book generation invocation failed'
            }
            
    except Exception as e:
        logger.error(f"Failed to start Volume {volume_num} for {series_id}: {e}")
        return {
            'series_id': series_id,
            'status': 'error',
            'error': str(e)
        }

def complete_series(series_data: Dict[str, Any], portfolio: PortfolioManager) -> Dict[str, Any]:
    """Mark series as complete."""
    series_id = series_data['series_id']
    
    try:
        logger.info(f"🎉 Completing series {series_id}")
        
        # Update to completed status
        portfolio.update_series_status(
            series_id,
            SeriesStatus.SERIES_COMPLETE,
            next_action_hours=8760  # 1 year (no further action needed)
        )
        
        # Send completion notification
        send_series_completion_notification(series_data)
        
        return {
            'series_id': series_id,
            'status': 'success',
            'action': 'series_completed',
            'message': 'All 5 volumes published successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to complete series {series_id}: {e}")
        return {
            'series_id': series_id,
            'status': 'error',
            'error': str(e)
        }

def invoke_book_generation(payload: Dict[str, Any]) -> bool:
    """Invoke the book generation Lambda."""
    try:
        import boto3
        
        lambda_client = boto3.client('lambda')
        
        # Invoke the V3 orchestrator for book generation
        response = lambda_client.invoke(
            FunctionName='kindlemint-v3-orchestrator',
            InvocationType='Event',  # Async invocation
            Payload=json.dumps(payload)
        )
        
        if response['StatusCode'] == 202:
            logger.info(f"✅ Book generation invoked successfully")
            return True
        else:
            logger.error(f"Book generation invocation failed: {response['StatusCode']}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to invoke book generation: {e}")
        return False

def send_series_completion_notification(series_data: Dict[str, Any]):
    """Send notification about series completion."""
    try:
        import requests
        
        slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        if not slack_webhook:
            return
        
        message = {
            "text": "🎉 SERIES COMPLETED",
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {
                            "title": "Series Completed",
                            "value": f"*{series_data['brand_name']}*\n{series_data['niche_topic']}",
                            "short": True
                        },
                        {
                            "title": "Total Books",
                            "value": "5 volumes published",
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        requests.post(slack_webhook, json=message, timeout=10)
        
    except Exception as e:
        logger.error(f"Failed to send completion notification: {e}")

def create_success_response(results: List[Dict], message: str) -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'success',
            'message': message,
            'results': results,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '3.0'
        })
    }

if __name__ == "__main__":
    # For local testing
    test_event = {
        "source": "manual_test"
    }
    
    class MockContext:
        def __init__(self):
            self.function_name = "multi-series-orchestrator"
            self.memory_limit_in_mb = 1024
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))