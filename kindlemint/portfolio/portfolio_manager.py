"""
KindleMint Portfolio Manager - Central series tracking and management
"""
import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SeriesStatus(Enum):
    """Portfolio series status enumeration"""
    RESEARCHING = "RESEARCHING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL" 
    APPROVED = "APPROVED"
    PUBLISHING_VOL_1 = "PUBLISHING_VOL_1"
    PUBLISHING_VOL_2 = "PUBLISHING_VOL_2"
    PUBLISHING_VOL_3 = "PUBLISHING_VOL_3"
    PUBLISHING_VOL_4 = "PUBLISHING_VOL_4"
    PUBLISHING_VOL_5 = "PUBLISHING_VOL_5"
    SERIES_COMPLETE = "SERIES_COMPLETE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

class PortfolioManager:
    """Manages the entire KindleMint series portfolio"""
    
    def __init__(self, table_name: str = "KindleMint_Portfolio_Tracker"):
        """Initialize portfolio manager."""
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        
    def add_new_opportunity(self, niche_data: Dict[str, Any]) -> str:
        """Add new niche opportunity awaiting approval."""
        try:
            series_id = f"series_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create portfolio entry
            portfolio_item = {
                'series_id': series_id,
                'brand_name': niche_data.get('suggested_brand', 'Unknown Studio'),
                'niche_topic': niche_data['niche'],
                'micro_niche': niche_data['topic'],
                'status': SeriesStatus.AWAITING_APPROVAL.value,
                'next_action_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'daily_revenue': 0.0,
                'total_books_published': 0,
                'market_score': niche_data.get('market_score', 0),
                'estimated_daily_revenue': niche_data.get('estimated_revenue', 0),
                'research_data': json.dumps(niche_data),
                'created_date': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            self.table.put_item(Item=portfolio_item)
            logger.info(f"✅ Added new opportunity: {series_id} - {niche_data['niche']}")
            
            return series_id
            
        except Exception as e:
            logger.error(f"Failed to add opportunity: {e}")
            raise
    
    def approve_series(self, series_id: str) -> bool:
        """Approve a series for production."""
        try:
            # Update status to approved and set next action
            next_action = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
            
            self.table.update_item(
                Key={'series_id': series_id},
                UpdateExpression='SET #status = :status, next_action_date = :next_action, last_updated = :updated',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': SeriesStatus.APPROVED.value,
                    ':next_action': next_action,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"✅ Series approved: {series_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve series {series_id}: {e}")
            return False
    
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get all series requiring action based on status and date."""
        try:
            current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            
            # Scan for series needing action
            response = self.table.scan(
                FilterExpression='next_action_date <= :current_time AND #status <> :cancelled AND #status <> :complete',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':current_time': current_datetime,
                    ':cancelled': SeriesStatus.CANCELLED.value,
                    ':complete': SeriesStatus.SERIES_COMPLETE.value
                }
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Failed to get pending actions: {e}")
            return []
    
    def update_series_status(self, series_id: str, new_status: SeriesStatus, 
                           next_action_hours: int = 24) -> bool:
        """Update series status and schedule next action."""
        try:
            next_action = (datetime.utcnow() + timedelta(hours=next_action_hours)).strftime('%Y-%m-%d %H:%M')
            
            self.table.update_item(
                Key={'series_id': series_id},
                UpdateExpression='SET #status = :status, next_action_date = :next_action, last_updated = :updated',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': new_status.value,
                    ':next_action': next_action,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"✅ Updated {series_id}: {new_status.value} (next action: {next_action})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update series status: {e}")
            return False
    
    def update_revenue(self, series_id: str, daily_revenue: float) -> bool:
        """Update daily revenue for a series."""
        try:
            self.table.update_item(
                Key={'series_id': series_id},
                UpdateExpression='SET daily_revenue = :revenue, last_updated = :updated',
                ExpressionAttributeValues={
                    ':revenue': daily_revenue,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"💰 Updated revenue for {series_id}: ${daily_revenue:.2f}/day")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update revenue: {e}")
            return False
    
    def increment_book_count(self, series_id: str) -> bool:
        """Increment the published book count for a series."""
        try:
            self.table.update_item(
                Key={'series_id': series_id},
                UpdateExpression='SET total_books_published = total_books_published + :inc, last_updated = :updated',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"📚 Incremented book count for {series_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment book count: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary for CEO dashboard."""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Calculate summary metrics
            total_series = len(items)
            active_series = len([item for item in items if item['status'] not in [
                SeriesStatus.CANCELLED.value, SeriesStatus.SERIES_COMPLETE.value
            ]])
            total_daily_revenue = sum(float(item.get('daily_revenue', 0)) for item in items)
            total_books = sum(int(item.get('total_books_published', 0)) for item in items)
            
            # Group by status
            status_breakdown = {}
            for item in items:
                status = item['status']
                if status not in status_breakdown:
                    status_breakdown[status] = 0
                status_breakdown[status] += 1
            
            # Top performers
            top_performers = sorted(
                [item for item in items if float(item.get('daily_revenue', 0)) > 0],
                key=lambda x: float(x.get('daily_revenue', 0)),
                reverse=True
            )[:5]
            
            return {
                'total_series': total_series,
                'active_series': active_series,
                'total_daily_revenue': total_daily_revenue,
                'total_books_published': total_books,
                'status_breakdown': status_breakdown,
                'top_performers': top_performers,
                'full_portfolio': items,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}")
            return {}
    
    def get_awaiting_approval(self) -> List[Dict[str, Any]]:
        """Get all series awaiting CEO approval."""
        try:
            response = self.table.query(
                IndexName='StatusIndex',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': SeriesStatus.AWAITING_APPROVAL.value}
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Failed to get awaiting approval: {e}")
            return []