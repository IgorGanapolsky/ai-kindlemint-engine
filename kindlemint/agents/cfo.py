"""
CFO Agent - KDP Sales Analyzer and Report Ingestor
Processes KDP sales reports and updates memory with performance data.
"""

import logging
import os
import csv
import io
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import boto3
from decimal import Decimal

from ..memory import KDPMemory

logger = logging.getLogger(__name__)


class CFOAgent:
    """CFO Agent for processing KDP sales reports and financial analysis."""
    
    def __init__(
        self,
        region_name: str = 'us-east-2',
        profile_name: Optional[str] = 'kindlemint-keys'
    ):
        """Initialize the CFO Agent.
        
        Args:
            region_name: AWS region name
            profile_name: AWS profile name for credentials
        """
        self.region_name = region_name
        self.profile_name = profile_name
        
        # Initialize AWS services
        session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.s3 = session.client('s3', region_name=region_name)
        self.ses = session.client('ses', region_name=region_name)
        
        # Initialize memory system
        try:
            self.memory = KDPMemory(region_name=region_name, profile_name=profile_name)
            logger.info("CFO Agent initialized with memory system")
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            raise
    
    def process_kdp_report_csv(self, csv_content: str, report_date: str) -> Dict[str, Any]:
        """Process KDP sales report CSV content.
        
        Args:
            csv_content: Raw CSV content from KDP report
            report_date: Report date in YYYY-MM-DD format
            
        Returns:
            Dict with processing results
        """
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            processed_books = []
            total_sales = 0
            total_pages_read = 0
            total_royalties = Decimal('0.0')
            
            for row in csv_reader:
                # Extract book data from CSV row
                # Note: Actual KDP CSV format may vary - adjust field names as needed
                book_data = self._extract_book_data_from_row(row)
                
                if book_data:
                    # Update memory with sales data
                    success = self.memory.update_sales_data(
                        book_id=book_data['book_id'],
                        kdp_sales=book_data['sales_count'],
                        kenp_reads=book_data['pages_read']
                    )
                    
                    if success:
                        processed_books.append(book_data)
                        total_sales += book_data['sales_count']
                        total_pages_read += book_data['pages_read']
                        total_royalties += Decimal(str(book_data['royalties']))
                        
                        logger.info(f"Updated sales data for book: {book_data['book_id']}")
                    else:
                        logger.warning(f"Failed to update sales data for book: {book_data['book_id']}")
            
            result = {
                'report_date': report_date,
                'books_processed': len(processed_books),
                'total_sales': total_sales,
                'total_pages_read': total_pages_read,
                'total_royalties': float(total_royalties),
                'processing_timestamp': datetime.now(timezone.utc).isoformat(),
                'success': True
            }
            
            logger.info(f"Processed KDP report: {len(processed_books)} books, {total_sales} sales, ${total_royalties:.2f} royalties")
            return result
            
        except Exception as e:
            logger.error(f"Error processing KDP report: {str(e)}")
            return {
                'error': str(e),
                'success': False,
                'processing_timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _extract_book_data_from_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract and normalize book data from CSV row.
        
        Note: KDP CSV format may vary. Adjust field mappings as needed.
        Common fields: Title, ASIN, ISBN, Sales, Pages Read, Royalties, etc.
        """
        try:
            # Map CSV fields to our data structure
            # These field names may need adjustment based on actual KDP CSV format
            title = row.get('Title', '').strip()
            asin = row.get('ASIN', '').strip()
            
            # Use ASIN as book_id if available, otherwise generate from title
            book_id = asin if asin else self._generate_book_id_from_title(title)
            
            if not book_id or not title:
                logger.warning(f"Skipping row with missing book_id or title: {row}")
                return None
            
            # Extract numeric fields with error handling
            sales_count = self._safe_int_conversion(row.get('Units Sold', '0'))
            pages_read = self._safe_int_conversion(row.get('Pages Read', '0'))
            royalties = self._safe_decimal_conversion(row.get('Royalties', '0.0'))
            
            return {
                'book_id': book_id,
                'title': title,
                'asin': asin,
                'sales_count': sales_count,
                'pages_read': pages_read,
                'royalties': royalties,
                'raw_row': row  # Keep original data for debugging
            }
            
        except Exception as e:
            logger.warning(f"Error extracting data from row: {e}")
            return None
    
    def _generate_book_id_from_title(self, title: str) -> str:
        """Generate a consistent book_id from title when ASIN is not available."""
        import hashlib
        normalized_title = title.lower().strip().replace(' ', '_')
        # Create a short hash for uniqueness
        hash_suffix = hashlib.md5(title.encode()).hexdigest()[:8]
        return f"{normalized_title}_{hash_suffix}"
    
    def _safe_int_conversion(self, value: str) -> int:
        """Safely convert string to int."""
        try:
            # Remove any non-numeric characters except negative sign
            cleaned = ''.join(c for c in value if c.isdigit() or c == '-')
            return int(cleaned) if cleaned else 0
        except (ValueError, TypeError):
            return 0
    
    def _safe_decimal_conversion(self, value: str) -> Decimal:
        """Safely convert string to Decimal."""
        try:
            # Remove currency symbols and other non-numeric characters
            cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
            return Decimal(cleaned) if cleaned else Decimal('0.0')
        except (ValueError, TypeError, Exception):
            return Decimal('0.0')
    
    def generate_financial_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate financial performance report from memory data.
        
        Args:
            days: Number of days to include in the report
            
        Returns:
            Dict with financial metrics and insights
        """
        try:
            # Get all books from memory
            all_books = self.memory.list_all_books()
            
            if not all_books:
                return {
                    'message': 'No books found in memory',
                    'total_books': 0,
                    'success': True
                }
            
            # Calculate aggregate metrics
            total_sales = sum(int(book.get('kdp_sales_count', 0)) for book in all_books)
            total_pages_read = sum(int(book.get('kenp_read_count', 0)) for book in all_books)
            total_roi = sum(float(book.get('calculated_roi', 0)) for book in all_books)
            
            # Find top performers
            top_books = sorted(
                all_books,
                key=lambda x: float(x.get('calculated_roi', 0)),
                reverse=True
            )[:5]
            
            # Get niche performance
            niche_performance = self.memory.get_top_performing_niches(limit=10)
            
            report = {
                'report_date': datetime.now(timezone.utc).isoformat(),
                'total_books': len(all_books),
                'total_sales': total_sales,
                'total_pages_read': total_pages_read,
                'average_roi': total_roi / len(all_books) if all_books else 0,
                'top_performing_books': [
                    {
                        'book_id': book['book_id'],
                        'topic': book.get('topic', 'Unknown'),
                        'niche': book.get('niche', 'Unknown'),
                        'roi': float(book.get('calculated_roi', 0)),
                        'sales': int(book.get('kdp_sales_count', 0))
                    }
                    for book in top_books
                ],
                'niche_performance': niche_performance,
                'success': True
            }
            
            logger.info(f"Generated financial report: {len(all_books)} books, {total_sales} total sales")
            return report
            
        except Exception as e:
            logger.error(f"Error generating financial report: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    def identify_profitable_opportunities(self) -> Dict[str, Any]:
        """Identify profitable publishing opportunities based on memory data."""
        try:
            # Get top performing niches
            top_niches = self.memory.get_top_performing_niches(limit=5)
            
            opportunities = []
            for niche_data in top_niches:
                niche = niche_data['niche']
                avg_roi = niche_data['average_roi']
                book_count = niche_data['book_count']
                
                # Calculate opportunity score
                opportunity_score = avg_roi * (1 + (book_count / 10))  # Bonus for proven niches
                
                opportunities.append({
                    'niche': niche,
                    'average_roi': avg_roi,
                    'book_count': book_count,
                    'opportunity_score': opportunity_score,
                    'recommendation': self._generate_niche_recommendation(niche, avg_roi, book_count)
                })
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            return {
                'opportunities': opportunities,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error identifying opportunities: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _generate_niche_recommendation(self, niche: str, avg_roi: float, book_count: int) -> str:
        """Generate a recommendation for a niche based on performance data."""
        if avg_roi > 1.0:
            if book_count >= 3:
                return f"HIGH PRIORITY: Proven profitable niche with {avg_roi:.1%} ROI. Continue investing."
            else:
                return f"EXPAND: Promising niche with {avg_roi:.1%} ROI. Consider increasing volume."
        elif avg_roi > 0.5:
            return f"MONITOR: Moderate performance ({avg_roi:.1%} ROI). Optimize existing books."
        else:
            return f"RECONSIDER: Low performance ({avg_roi:.1%} ROI). May need different approach."


# Lambda handler function for AWS deployment
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for KDP Report Ingestor.
    
    Expected event structure:
    {
        "action": "process_report|generate_report|identify_opportunities",
        "csv_content": "...",  # For process_report action
        "report_date": "YYYY-MM-DD",  # For process_report action
        "days": 30  # For generate_report action
    }
    """
    try:
        # Initialize CFO Agent (use environment variables for Lambda)
        cfo = CFOAgent(
            region_name=os.getenv('AWS_REGION', 'us-east-2'),
            profile_name=None  # Use IAM role in Lambda
        )
        
        action = event.get('action', 'generate_report')
        
        if action == 'process_report':
            csv_content = event.get('csv_content', '')
            report_date = event.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            
            if not csv_content:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'csv_content is required for process_report action'})
                }
            
            result = cfo.process_kdp_report_csv(csv_content, report_date)
            
        elif action == 'generate_report':
            days = event.get('days', 30)
            result = cfo.generate_financial_report(days)
            
        elif action == 'identify_opportunities':
            result = cfo.identify_profitable_opportunities()
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown action: {action}'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        }