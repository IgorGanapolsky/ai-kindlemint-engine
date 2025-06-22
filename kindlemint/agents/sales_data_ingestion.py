#!/usr/bin/env python3
"""
SalesDataIngestion Agent - Automatic KDP sales and royalty report ingestion
Downloads KDP sales reports and stores performance data in DynamoDB for analysis
"""
import os
import json
import boto3
import time
import csv
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal
import requests
import io

# Browser automation for KDP portal
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Sentry integration
try:
    from ..utils.sentry_config import capture_business_event, SentryPerformanceTracker
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

@dataclass
class KDPSalesRecord:
    """Represents a single KDP sales record."""
    asin: str
    title: str
    author: str
    marketplace: str
    reporting_date: str
    units_sold: int
    units_refunded: int
    net_units_sold: int
    royalty_rate: float
    royalty_earned: Decimal
    currency: str
    
    # Metadata
    book_id: Optional[str] = None
    series_name: Optional[str] = None
    volume_number: Optional[int] = None
    ingestion_timestamp: Optional[str] = None

@dataclass  
class KDPRoyaltyRecord:
    """Represents a KDP royalty payment record."""
    payment_date: str
    marketplace: str
    currency: str
    beginning_balance: Decimal
    royalty_earned: Decimal
    other_transactions: Decimal
    total_royalty: Decimal
    marketplace_tax_withheld: Decimal
    us_tax_withheld: Decimal
    ending_balance: Decimal
    
    # Metadata
    ingestion_timestamp: Optional[str] = None

class SalesDataIngestion:
    """Handles automatic ingestion of KDP sales and royalty data."""
    
    def __init__(self):
        self.data_dir = Path("output/sales_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # DynamoDB setup
        self.dynamodb = boto3.resource('dynamodb')
        self.sales_table_name = 'KindleMint-SalesData'
        self.royalty_table_name = 'KindleMint-RoyaltyData'
        
        # KDP credentials
        self.kdp_email = os.getenv('KDP_EMAIL')
        self.kdp_password = os.getenv('KDP_PASSWORD')
        
        # Browser setup
        self.browser = None
        self.page = None
        
        # Initialize DynamoDB tables
        self.setup_dynamodb_tables()
        
    def setup_dynamodb_tables(self):
        """Create DynamoDB tables if they don't exist."""
        try:
            # Sales data table
            try:
                self.sales_table = self.dynamodb.Table(self.sales_table_name)
                self.sales_table.load()
                print(f"✅ Sales table exists: {self.sales_table_name}")
            except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
                print(f"📊 Creating sales table: {self.sales_table_name}")
                self.sales_table = self.dynamodb.create_table(
                    TableName=self.sales_table_name,
                    KeySchema=[
                        {'AttributeName': 'asin', 'KeyType': 'HASH'},
                        {'AttributeName': 'reporting_date', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'asin', 'AttributeType': 'S'},
                        {'AttributeName': 'reporting_date', 'AttributeType': 'S'},
                        {'AttributeName': 'series_name', 'AttributeType': 'S'},
                        {'AttributeName': 'marketplace', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'SeriesIndex',
                            'KeySchema': [
                                {'AttributeName': 'series_name', 'KeyType': 'HASH'},
                                {'AttributeName': 'reporting_date', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'},
                            'BillingMode': 'PAY_PER_REQUEST'
                        },
                        {
                            'IndexName': 'MarketplaceIndex', 
                            'KeySchema': [
                                {'AttributeName': 'marketplace', 'KeyType': 'HASH'},
                                {'AttributeName': 'reporting_date', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'},
                            'BillingMode': 'PAY_PER_REQUEST'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                self.sales_table.wait_until_exists()
                
            # Royalty data table
            try:
                self.royalty_table = self.dynamodb.Table(self.royalty_table_name)
                self.royalty_table.load()
                print(f"✅ Royalty table exists: {self.royalty_table_name}")
            except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
                print(f"💰 Creating royalty table: {self.royalty_table_name}")
                self.royalty_table = self.dynamodb.create_table(
                    TableName=self.royalty_table_name,
                    KeySchema=[
                        {'AttributeName': 'marketplace', 'KeyType': 'HASH'},
                        {'AttributeName': 'payment_date', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'marketplace', 'AttributeType': 'S'},
                        {'AttributeName': 'payment_date', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                self.royalty_table.wait_until_exists()
                
        except Exception as e:
            print(f"❌ DynamoDB setup failed: {e}")
            raise
    
    def start_browser_session(self):
        """Start browser session for KDP portal access."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available - install with: pip install playwright")
            
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=os.getenv('CI') == 'true',
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self.context = self.browser.new_context(
                viewport={'width': 1600, 'height': 900},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            self.page = self.context.new_page()
            print("🌐 Browser session started for KDP portal")
            
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            raise
    
    def login_to_kdp(self):
        """Login to KDP portal."""
        if not self.page:
            self.start_browser_session()
            
        try:
            print("🔐 Logging into KDP portal...")
            
            # Navigate to KDP
            self.page.goto('https://kdp.amazon.com')
            
            # Check if already logged in
            try:
                self.page.wait_for_selector('[data-testid="create-new-title"]', timeout=5000)
                print("✅ Already logged in to KDP")
                return True
            except:
                pass
            
            # Click sign in
            sign_in_button = self.page.wait_for_selector('a[href*="signin"]', timeout=10000)
            sign_in_button.click()
            
            # Enter email
            email_input = self.page.wait_for_selector('input[type="email"], input[name="email"], #ap_email', timeout=10000)
            email_input.fill(self.kdp_email)
            
            # Click continue
            continue_button = self.page.wait_for_selector('input[type="submit"], button[type="submit"], #continue', timeout=10000)
            continue_button.click()
            time.sleep(2)
            
            # Enter password
            password_input = self.page.wait_for_selector('input[type="password"], input[name="password"], #ap_password', timeout=10000)
            password_input.fill(self.kdp_password)
            
            # Sign in
            signin_button = self.page.wait_for_selector('input[type="submit"], button[type="submit"], #signInSubmit', timeout=10000)
            signin_button.click()
            
            # Wait for dashboard
            self.page.wait_for_selector('[data-testid="create-new-title"], .bookshelf-container', timeout=30000)
            
            print("✅ Successfully logged into KDP")
            return True
            
        except Exception as e:
            print(f"❌ KDP login failed: {e}")
            return False
    
    def download_sales_reports(self, start_date: str, end_date: str) -> List[str]:
        """Download sales reports from KDP for specified date range."""
        if not self.login_to_kdp():
            raise Exception("Failed to login to KDP")
            
        try:
            print(f"📥 Downloading sales reports from {start_date} to {end_date}")
            
            # Navigate to reports section
            self.page.goto('https://kdp.amazon.com/en_US/reports')
            time.sleep(3)
            
            # Switch to sales dashboard if needed
            try:
                sales_tab = self.page.wait_for_selector('a[href*="sales-dashboard"], .sales-dashboard-tab', timeout=5000)
                sales_tab.click()
                time.sleep(2)
            except:
                pass
            
            downloaded_files = []
            
            # Look for download options
            download_buttons = self.page.query_selector_all('button:has-text("Download"), a:has-text("Download"), .download-btn')
            
            for i, button in enumerate(download_buttons[:3]):  # Limit to first 3 download options
                try:
                    print(f"🔄 Attempting download {i+1}...")
                    
                    # Start download
                    with self.page.expect_download() as download_info:
                        button.click()
                        time.sleep(2)
                    
                    download = download_info.value
                    
                    # Save file
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"kdp_sales_report_{timestamp}_{i+1}.{download.suggested_filename.split('.')[-1]}"
                    filepath = self.data_dir / filename
                    
                    download.save_as(filepath)
                    downloaded_files.append(str(filepath))
                    
                    print(f"✅ Downloaded: {filename}")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️ Download {i+1} failed: {e}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Sales report download failed: {e}")
            return []
    
    def download_royalty_reports(self, start_date: str, end_date: str) -> List[str]:
        """Download royalty reports from KDP."""
        try:
            print(f"💰 Downloading royalty reports from {start_date} to {end_date}")
            
            # Navigate to royalty reports
            self.page.goto('https://kdp.amazon.com/en_US/royalty-payment-summary')
            time.sleep(3)
            
            downloaded_files = []
            
            # Look for download/export options
            export_buttons = self.page.query_selector_all('button:has-text("Export"), a:has-text("Export"), .export-btn, button:has-text("Download")')
            
            for i, button in enumerate(export_buttons[:2]):  # Limit to first 2 export options
                try:
                    print(f"🔄 Attempting royalty export {i+1}...")
                    
                    with self.page.expect_download() as download_info:
                        button.click()
                        time.sleep(2)
                    
                    download = download_info.value
                    
                    # Save file
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"kdp_royalty_report_{timestamp}_{i+1}.{download.suggested_filename.split('.')[-1]}"
                    filepath = self.data_dir / filename
                    
                    download.save_as(filepath)
                    downloaded_files.append(str(filepath))
                    
                    print(f"✅ Downloaded royalty report: {filename}")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️ Royalty export {i+1} failed: {e}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Royalty report download failed: {e}")
            return []
    
    def process_sales_csv(self, filepath: str) -> List[KDPSalesRecord]:
        """Process a sales CSV file and extract records."""
        records = []
        
        try:
            print(f"📊 Processing sales file: {Path(filepath).name}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                # Try to detect if it's a ZIP file
                if filepath.endswith('.zip'):
                    with zipfile.ZipFile(filepath, 'r') as zip_file:
                        csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                        if csv_files:
                            csv_content = zip_file.read(csv_files[0]).decode('utf-8')
                            csv_reader = csv.DictReader(io.StringIO(csv_content))
                        else:
                            print("⚠️ No CSV files found in ZIP")
                            return records
                else:
                    csv_reader = csv.DictReader(f)
                
                for row in csv_reader:
                    try:
                        # Map CSV columns to our data structure
                        # Note: Column names may vary - this is a best-guess mapping
                        record = KDPSalesRecord(
                            asin=row.get('ASIN', row.get('asin', '')),
                            title=row.get('Title', row.get('title', '')),
                            author=row.get('Author', row.get('author', '')),
                            marketplace=row.get('Marketplace', row.get('marketplace', 'Amazon.com')),
                            reporting_date=row.get('Reporting Date', row.get('reporting_date', '')),
                            units_sold=int(row.get('Units Sold', row.get('units_sold', 0))),
                            units_refunded=int(row.get('Units Refunded', row.get('units_refunded', 0))),
                            net_units_sold=int(row.get('Net Units Sold', row.get('net_units_sold', 0))),
                            royalty_rate=float(row.get('Royalty Rate', row.get('royalty_rate', 0.0))),
                            royalty_earned=Decimal(str(row.get('Royalty Earned', row.get('royalty_earned', '0.00')))),
                            currency=row.get('Currency', row.get('currency', 'USD')),
                            ingestion_timestamp=datetime.now().isoformat()
                        )
                        
                        # Try to identify book series and volume
                        self._enhance_record_metadata(record)
                        
                        records.append(record)
                        
                    except Exception as e:
                        print(f"⚠️ Failed to process row: {e}")
                        continue
                        
            print(f"✅ Processed {len(records)} sales records")
            
        except Exception as e:
            print(f"❌ Failed to process sales CSV: {e}")
            
        return records
    
    def _enhance_record_metadata(self, record: KDPSalesRecord):
        """Enhance record with series and volume metadata."""
        title_lower = record.title.lower()
        
        # Try to identify our series
        if 'large print crossword' in title_lower:
            record.series_name = 'Large_Print_Crossword_Masters'
            record.book_id = f"lpcm_{record.asin}"
            
            # Extract volume number
            import re
            volume_match = re.search(r'volume (\d+)', title_lower)
            if volume_match:
                record.volume_number = int(volume_match.group(1))
        
        # Add more series detection logic as needed
    
    def store_sales_records(self, records: List[KDPSalesRecord]):
        """Store sales records in DynamoDB."""
        try:
            print(f"💾 Storing {len(records)} sales records in DynamoDB...")
            
            with self.sales_table.batch_writer() as batch:
                for record in records:
                    # Convert to DynamoDB format
                    item = asdict(record)
                    
                    # Convert Decimal values
                    item['royalty_earned'] = str(item['royalty_earned'])
                    
                    batch.put_item(Item=item)
            
            print(f"✅ Stored {len(records)} sales records")
            
            # Send to Sentry
            if SENTRY_AVAILABLE:
                capture_business_event("sales_data_ingested",
                                     f"Ingested {len(records)} sales records",
                                     extra_data={"records_count": len(records)})
            
        except Exception as e:
            print(f"❌ Failed to store sales records: {e}")
            raise
    
    def get_sales_summary(self, series_name: str = None, date_range: int = 30) -> Dict[str, Any]:
        """Get sales summary for analysis."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            if series_name:
                # Query by series
                response = self.sales_table.query(
                    IndexName='SeriesIndex',
                    KeyConditionExpression='series_name = :series AND reporting_date BETWEEN :start AND :end',
                    ExpressionAttributeValues={
                        ':series': series_name,
                        ':start': start_date.strftime('%Y-%m-%d'),
                        ':end': end_date.strftime('%Y-%m-%d')
                    }
                )
            else:
                # Scan all recent records
                response = self.sales_table.scan(
                    FilterExpression='reporting_date BETWEEN :start AND :end',
                    ExpressionAttributeValues={
                        ':start': start_date.strftime('%Y-%m-%d'),
                        ':end': end_date.strftime('%Y-%m-%d')
                    }
                )
            
            records = response['Items']
            
            # Calculate summary
            total_units_sold = sum(int(r.get('net_units_sold', 0)) for r in records)
            total_royalties = sum(float(r.get('royalty_earned', 0)) for r in records)
            unique_titles = len(set(r.get('asin') for r in records))
            
            summary = {
                'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'series_name': series_name,
                'total_units_sold': total_units_sold,
                'total_royalties_earned': total_royalties,
                'unique_titles': unique_titles,
                'records_count': len(records),
                'average_royalty_per_unit': total_royalties / total_units_sold if total_units_sold > 0 else 0,
                'records': records
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Failed to get sales summary: {e}")
            return {}
    
    def run_daily_ingestion(self):
        """Run daily sales data ingestion."""
        try:
            with SentryPerformanceTracker("daily_sales_ingestion") if SENTRY_AVAILABLE else None:
                print("🔄 Starting daily sales data ingestion...")
                
                # Calculate date range (yesterday)
                yesterday = datetime.now() - timedelta(days=1)
                date_str = yesterday.strftime('%Y-%m-%d')
                
                # Download reports
                sales_files = self.download_sales_reports(date_str, date_str)
                royalty_files = self.download_royalty_reports(date_str, date_str)
                
                # Process sales files
                all_sales_records = []
                for filepath in sales_files:
                    records = self.process_sales_csv(filepath)
                    all_sales_records.extend(records)
                
                # Store in DynamoDB
                if all_sales_records:
                    self.store_sales_records(all_sales_records)
                else:
                    print("ℹ️ No sales records to process")
                
                # Generate summary
                summary = self.get_sales_summary()
                
                print(f"📊 Daily ingestion summary:")
                print(f"   Records processed: {len(all_sales_records)}")
                print(f"   Total units sold (30 days): {summary.get('total_units_sold', 0)}")
                print(f"   Total royalties (30 days): ${summary.get('total_royalties_earned', 0):.2f}")
                
                return {
                    'success': True,
                    'records_processed': len(all_sales_records),
                    'files_downloaded': len(sales_files) + len(royalty_files),
                    'summary': summary
                }
                
        except Exception as e:
            print(f"❌ Daily ingestion failed: {e}")
            if SENTRY_AVAILABLE:
                capture_business_event("sales_ingestion_failed", str(e), level='error')
            return {'success': False, 'error': str(e)}
        
        finally:
            # Close browser
            if self.browser:
                self.browser.close()
                self.playwright.stop()

# Global sales ingestion instance
sales_ingestion = SalesDataIngestion()

# Convenience functions
def run_daily_ingestion():
    """Run daily sales data ingestion."""
    return sales_ingestion.run_daily_ingestion()

def get_sales_summary(series_name: str = None, days: int = 30):
    """Get sales summary."""
    return sales_ingestion.get_sales_summary(series_name, days)

def download_latest_reports():
    """Download latest sales reports."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    return sales_ingestion.download_sales_reports(yesterday, yesterday)