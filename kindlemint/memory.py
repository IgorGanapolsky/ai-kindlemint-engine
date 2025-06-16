"""
Memory-Driven Publishing Engine - DynamoDB Memory Operations
Handles all interactions with the KDP_Business_Memory table for data-driven publishing decisions.
"""

import boto3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class KDPMemory:
    """Handles all DynamoDB operations for the KDP Business Memory system."""
    
    def __init__(self, region_name: str = 'us-east-2', profile_name: Optional[str] = 'kindlemint-keys'):
        """Initialize DynamoDB connection."""
        session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.dynamodb = session.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table('KDP_Business_Memory')
    
    def store_book_record(self, book_id: str, topic: str, niche: str, metadata: Optional[Dict] = None) -> bool:
        """Store a new book record in memory."""
        try:
            item = {
                'book_id': book_id,
                'topic': topic,
                'niche': niche,
                'creation_date': datetime.now(timezone.utc).isoformat(),
                'kdp_sales_count': Decimal('0'),
                'kenp_read_count': Decimal('0'),
                'calculated_roi': Decimal('0.0'),
                'marketing_campaign_effectiveness': {}
            }
            
            if metadata:
                item.update(metadata)
            
            self.table.put_item(Item=item)
            logger.info(f"Stored book record: {book_id} in niche: {niche}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store book record {book_id}: {str(e)}")
            return False
    
    def update_sales_data(self, book_id: str, kdp_sales: int, kenp_reads: int) -> bool:
        """Update sales data for a book and recalculate ROI."""
        try:
            # Calculate basic ROI (placeholder formula)
            estimated_revenue = (kdp_sales * Decimal('2.50')) + (kenp_reads * Decimal('0.004'))
            estimated_cost = Decimal('50.0')  # Placeholder production cost
            roi = (estimated_revenue - estimated_cost) / estimated_cost if estimated_cost > 0 else Decimal('0')
            
            self.table.update_item(
                Key={'book_id': book_id},
                UpdateExpression='SET kdp_sales_count = :sales, kenp_read_count = :reads, calculated_roi = :roi',
                ExpressionAttributeValues={
                    ':sales': Decimal(str(kdp_sales)),
                    ':reads': Decimal(str(kenp_reads)),
                    ':roi': roi
                }
            )
            logger.info(f"Updated sales data for {book_id}: {kdp_sales} sales, {kenp_reads} KENP reads, ROI: {roi}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sales data for {book_id}: {str(e)}")
            return False
    
    def get_top_performing_niches(self, limit: int = 5) -> List[Dict]:
        """Get niches with highest average ROI."""
        try:
            response = self.table.scan()
            items = response['Items']
            
            # Group by niche and calculate average ROI
            niche_performance = {}
            for item in items:
                niche = item['niche']
                roi = float(item.get('calculated_roi', 0))
                
                if niche not in niche_performance:
                    niche_performance[niche] = {'total_roi': 0, 'count': 0, 'books': []}
                
                niche_performance[niche]['total_roi'] += roi
                niche_performance[niche]['count'] += 1
                niche_performance[niche]['books'].append(item['book_id'])
            
            # Calculate averages and sort
            niche_rankings = []
            for niche, data in niche_performance.items():
                avg_roi = data['total_roi'] / data['count'] if data['count'] > 0 else 0
                niche_rankings.append({
                    'niche': niche,
                    'average_roi': avg_roi,
                    'book_count': data['count'],
                    'books': data['books']
                })
            
            # Sort by average ROI descending
            niche_rankings.sort(key=lambda x: x['average_roi'], reverse=True)
            return niche_rankings[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top performing niches: {str(e)}")
            return []
    
    def get_niche_marketing_insights(self, niche: str) -> Dict:
        """Get marketing effectiveness data for a specific niche."""
        try:
            response = self.table.scan(
                FilterExpression='niche = :niche',
                ExpressionAttributeValues={':niche': niche}
            )
            
            marketing_data = {}
            for item in response['Items']:
                campaign_data = item.get('marketing_campaign_effectiveness', {})
                for campaign_type, effectiveness in campaign_data.items():
                    if campaign_type not in marketing_data:
                        marketing_data[campaign_type] = []
                    marketing_data[campaign_type].append(effectiveness)
            
            # Calculate averages
            insights = {}
            for campaign_type, values in marketing_data.items():
                insights[campaign_type] = {
                    'average_effectiveness': sum(values) / len(values),
                    'sample_size': len(values)
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get marketing insights for niche {niche}: {str(e)}")
            return {}
    
    def update_marketing_effectiveness(self, book_id: str, campaign_type: str, effectiveness_score: float) -> bool:
        """Update marketing campaign effectiveness for a book."""
        try:
            self.table.update_item(
                Key={'book_id': book_id},
                UpdateExpression='SET marketing_campaign_effectiveness.#ct = :score',
                ExpressionAttributeNames={'#ct': campaign_type},
                ExpressionAttributeValues={':score': Decimal(str(effectiveness_score))}
            )
            logger.info(f"Updated marketing effectiveness for {book_id}: {campaign_type} = {effectiveness_score}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update marketing effectiveness for {book_id}: {str(e)}")
            return False
    
    def get_book_record(self, book_id: str) -> Optional[Dict]:
        """Get a specific book record."""
        try:
            response = self.table.get_item(Key={'book_id': book_id})
            return response.get('Item')
            
        except Exception as e:
            logger.error(f"Failed to get book record {book_id}: {str(e)}")
            return None
    
    def list_all_books(self) -> List[Dict]:
        """List all books in memory."""
        try:
            response = self.table.scan()
            return response['Items']
            
        except Exception as e:
            logger.error(f"Failed to list all books: {str(e)}")
            return []


def decimal_to_float(obj):
    """Helper function to convert DynamoDB Decimal types to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    return obj