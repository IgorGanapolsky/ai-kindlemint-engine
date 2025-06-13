"""
Google Sheets Analytics Integration for Mission Control
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

class SheetsAnalytics:
    """Google Sheets integration for analytics logging"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.setup_sheets_connection()
    
    def setup_sheets_connection(self):
        """Setup Google Sheets connection using service account"""
        if not GSPREAD_AVAILABLE:
            print("⚠️ Google Sheets integration not available - gspread not installed")
            return False
        
        try:
            # Check for service account credentials
            creds_file = 'gspread_creds.json'
            if os.path.exists(creds_file):
                self.gc = gspread.service_account(filename=creds_file)
            else:
                # Alternative: use environment variable for credentials
                creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
                if creds_json:
                    creds_dict = json.loads(creds_json)
                    scope = ['https://spreadsheets.google.com/feeds',
                            'https://www.googleapis.com/auth/drive']
                    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
                    self.gc = gspread.authorize(credentials)
                else:
                    print("⚠️ Google Sheets credentials not configured")
                    return False
            
            # Open or create analytics spreadsheet
            try:
                self.sheet = self.gc.open("KindleMint Analytics").worksheet("Logs")
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                spreadsheet = self.gc.create("KindleMint Analytics")
                self.sheet = spreadsheet.sheet1
                self.sheet.update('A1:F1', [['Timestamp', 'Book Title', 'Word Count', 'Runtime', 'Files Created', 'Status']])
                print("📊 Created new KindleMint Analytics spreadsheet")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup Google Sheets: {e}")
            return False
    
    def log_mission_analytics(self, book_title: str, word_count: int, runtime: float, files_created: int, status: str = "Success"):
        """Log mission analytics to Google Sheets"""
        if not self.sheet:
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row_data = [timestamp, book_title, word_count, runtime, files_created, status]
            self.sheet.append_row(row_data)
            print(f"📊 Analytics logged to Google Sheets: {book_title}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log to Google Sheets: {e}")
            return False
    
    def log_book_generation(self, book_data: Dict[str, Any]):
        """Log book generation metrics"""
        word_count = book_data.get('word_count', 0)
        runtime = book_data.get('generation_time', 0)
        files_created = book_data.get('files_created', 0)
        title = book_data.get('title', 'Unknown Book')
        
        return self.log_mission_analytics(title, word_count, runtime, files_created)
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary analytics from Google Sheets"""
        if not self.sheet:
            return {}
        
        try:
            all_records = self.sheet.get_all_records()
            
            total_books = len(all_records)
            total_words = sum(int(record.get('Word Count', 0)) for record in all_records)
            avg_runtime = sum(float(record.get('Runtime', 0)) for record in all_records) / max(total_books, 1)
            total_files = sum(int(record.get('Files Created', 0)) for record in all_records)
            
            return {
                'total_books_generated': total_books,
                'total_word_count': total_words,
                'average_runtime': avg_runtime,
                'total_files_created': total_files,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to get analytics summary: {e}")
            return {}

def log_to_sheets(book_title: str, word_count: int, runtime: float, files_created: int = 18):
    """Convenience function to log analytics to Google Sheets"""
    analytics = SheetsAnalytics()
    return analytics.log_mission_analytics(book_title, word_count, runtime, files_created)