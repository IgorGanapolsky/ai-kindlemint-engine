#!/usr/bin/env python3
"""
Simple Passive Income Automation - No AWS Required
Runs locally with full automation for daily book generation and KDP publishing
"""
import schedule
import time
import subprocess
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import random

class SimplePassiveIncome:
    """Local passive income automation system"""
    
    def __init__(self):
        self.db_path = 'passive_income.db'
        self.running = False
        self._init_database()
        self.topics_pool = [
            "Space Adventure Puzzles for Kids",
            "Underwater Mystery Quest", 
            "Jungle Explorer Challenges",
            "Castle Secret Riddles",
            "Robot Friend Adventures",
            "Magic Forest Puzzles",
            "Pirate Treasure Hunt",
            "Dinosaur Discovery Quest",
            "Dragon Castle Adventures",
            "Time Travel Mysteries",
            "Superhero Training Academy",
            "Alien Planet Exploration"
        ]
    
    def _init_database(self):
        """Initialize tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                generated_date DATETIME NOT NULL,
                word_count INTEGER DEFAULT 3000,
                estimated_revenue REAL DEFAULT 2.50,
                status TEXT DEFAULT 'generated',
                file_path TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_action(self, action, status, details=""):
        """Log automation actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO automation_log (timestamp, action, status, details)
            VALUES (?, ?, ?, ?)
        """, (datetime.now(), action, status, details))
        
        conn.commit()
        conn.close()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {action}: {status}")
    
    def generate_daily_book(self):
        """Generate a book automatically"""
        self.log_action("Daily Book Generation", "Starting", "Automated daily generation")
        
        try:
            # Select random topic
            topic = random.choice(self.topics_pool)
            
            # Run mission control
            result = subprocess.run([
                'python', 'mission_control.py', topic
            ], capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                # Parse output for book details
                book_title = self._extract_book_title(result.stdout)
                word_count = self._extract_word_count(result.stdout)
                
                # Find generated files
                book_files = self._find_latest_book_files()
                
                # Log to database
                self._log_book_generation(book_title or topic, topic, word_count, book_files)
                
                self.log_action("Book Generation", "Success", f"Generated: {book_title or topic}")
                
                # Send notification
                self._send_success_notification(book_title or topic, len(book_files))
                
                return True
            else:
                self.log_action("Book Generation", "Failed", result.stderr[:200])
                return False
                
        except Exception as e:
            self.log_action("Book Generation", "Error", str(e)[:200])
            return False
    
    def _extract_book_title(self, output):
        """Extract book title from mission control output"""
        lines = output.split('\n')
        for line in lines:
            if 'Book Title:' in line or 'Generated book:' in line:
                return line.split(':', 1)[1].strip()
        return None
    
    def _extract_word_count(self, output):
        """Extract word count from output"""
        try:
            lines = output.split('\n')
            for line in lines:
                if 'word' in line.lower() and any(char.isdigit() for char in line):
                    words = line.split()
                    for word in words:
                        if word.isdigit():
                            return int(word)
        except:
            pass
        return 3000  # Default estimate
    
    def _find_latest_book_files(self):
        """Find most recently generated book files"""
        book_files = []
        output_dir = 'output'
        
        if os.path.exists(output_dir):
            # Get files modified in last 30 minutes
            cutoff_time = time.time() - 1800  # 30 minutes ago
            
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.getmtime(file_path) > cutoff_time:
                    if filename.endswith(('.kpf', '.docx')):
                        book_files.append(file_path)
        
        return book_files
    
    def _log_book_generation(self, title, topic, word_count, files):
        """Log book generation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate estimated revenue
        estimated_revenue = 2.50
        if word_count > 5000:
            estimated_revenue += 1.00
        elif word_count > 3000:
            estimated_revenue += 0.50
        
        cursor.execute("""
            INSERT INTO books (title, topic, generated_date, word_count, estimated_revenue, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, topic, datetime.now(), word_count, estimated_revenue, json.dumps(files)))
        
        conn.commit()
        conn.close()
    
    def _send_success_notification(self, title, file_count):
        """Send success notification via email"""
        try:
            from utils.emailer import send_book_published_notification
            send_book_published_notification(title, f"Generated {file_count} files")
        except Exception as e:
            self.log_action("Email Notification", "Failed", str(e)[:100])
    
    def get_stats(self):
        """Get comprehensive statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total books
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        # This month
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute("SELECT COUNT(*) FROM books WHERE generated_date LIKE ?", (f"{current_month}%",))
        books_this_month = cursor.fetchone()[0]
        
        # Revenue
        cursor.execute("SELECT SUM(estimated_revenue) FROM books")
        total_revenue = cursor.fetchone()[0] or 0
        
        # Recent books
        cursor.execute("""
            SELECT title, topic, generated_date, estimated_revenue 
            FROM books 
            ORDER BY generated_date DESC 
            LIMIT 5
        """)
        recent_books = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_books': total_books,
            'books_this_month': books_this_month,
            'estimated_revenue': round(total_revenue, 2),
            'recent_books': recent_books,
            'status': 'active' if self.running else 'stopped'
        }
    
    def start_automation(self):
        """Start the passive income automation"""
        print("🚀 Starting Simple Passive Income Automation")
        print("📅 Daily book generation scheduled for 6:00 AM")
        print("💰 Estimated revenue: $2.50-$4.00 per book")
        print("📊 Track progress with: python automation/view_stats.py")
        
        self.running = True
        self.log_action("Automation", "Started", "Simple passive income automation started")
        
        # Schedule daily generation
        schedule.every().day.at("06:00").do(self.generate_daily_book)
        
        # Schedule weekly summary
        schedule.every().monday.at("09:00").do(self._weekly_summary)
        
        # Optional: Generate a book immediately for testing
        if '--test' in sys.argv:
            print("🧪 Running test generation...")
            self.generate_daily_book()
        
        # Run scheduling loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.stop_automation()
    
    def _weekly_summary(self):
        """Generate weekly summary"""
        stats = self.get_stats()
        summary = f"""
Weekly Passive Income Summary
Books generated this month: {stats['books_this_month']}
Estimated revenue: ${stats['estimated_revenue']}
Total books: {stats['total_books']}
"""
        self.log_action("Weekly Summary", "Generated", summary.replace('\n', ' '))
    
    def publish_latest_book(self):
        """Publish the most recently generated book to KDP"""
        self.log_action("KDP Publishing", "Starting", "Publishing latest book")
        
        try:
            # Run mission control with publisher agent
            result = subprocess.run([
                'python', 'mission_control.py', '--agent', 'publisher', 'latest'
            ], capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                self.log_action("KDP Publishing", "Success", "Book published to KDP")
                return True
            else:
                self.log_action("KDP Publishing", "Failed", result.stderr[:200])
                return False
                
        except Exception as e:
            self.log_action("KDP Publishing", "Error", str(e)[:200])
            return False
    
    def stop_automation(self):
        """Stop the automation"""
        self.running = False
        self.log_action("Automation", "Stopped", "User requested stop")
        print("🛑 Passive income automation stopped")

def main():
    """Main entry point"""
    automation = SimplePassiveIncome()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            automation.start_automation()
        elif command == 'stats':
            stats = automation.get_stats()
            print(f"Total Books: {stats['total_books']}")
            print(f"This Month: {stats['books_this_month']}")
            print(f"Revenue: ${stats['estimated_revenue']}")
            print(f"Status: {stats['status']}")
        elif command == 'generate':
            print("Generating book now...")
            success = automation.generate_daily_book()
            print("✓ Success" if success else "✗ Failed")
        elif command == 'publish':
            print("Publishing latest book to KDP...")
            success = automation.publish_latest_book()
            print("✓ Success" if success else "✗ Failed")
        else:
            print("Usage: python automation/simple_passive_income.py [start|stats|generate]")
    else:
        automation.start_automation()

if __name__ == '__main__':
    main()