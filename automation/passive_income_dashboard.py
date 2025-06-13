"""
Passive Income Dashboard - Monitor your automated KDP business
"""
from flask import Flask, render_template, jsonify, request
import boto3
import json
import os
from datetime import datetime, timedelta
import sqlite3
from botocore.exceptions import ClientError

app = Flask(__name__)

class PassiveIncomeDashboard:
    def __init__(self):
        self.s3 = boto3.client('s3') if self._check_aws_config() else None
        self.bucket_name = 'ai-kindlemint-automation'
        self.db_path = 'passive_income.db'
        self._init_database()
    
    def _check_aws_config(self):
        """Check if AWS credentials are configured"""
        try:
            boto3.Session().get_credentials()
            return True
        except:
            return False
    
    def _init_database(self):
        """Initialize local database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                generated_date DATE NOT NULL,
                word_count INTEGER,
                published_date DATE,
                estimated_revenue REAL DEFAULT 0,
                status TEXT DEFAULT 'generated'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                books_generated INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0,
                automation_runs INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total books generated
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        # Get books this month
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute("SELECT COUNT(*) FROM books WHERE generated_date LIKE ?", (f"{current_month}%",))
        books_this_month = cursor.fetchone()[0]
        
        # Get estimated revenue
        cursor.execute("SELECT SUM(estimated_revenue) FROM books")
        total_revenue = cursor.fetchone()[0] or 0
        
        # Get recent books
        cursor.execute("""
            SELECT title, topic, generated_date, status 
            FROM books 
            ORDER BY generated_date DESC 
            LIMIT 10
        """)
        recent_books = cursor.fetchall()
        
        conn.close()
        
        # Check AWS S3 if configured
        s3_books = 0
        if self.s3:
            try:
                response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix='books/')
                s3_books = len(response.get('Contents', []))
            except ClientError:
                s3_books = 0
        
        return {
            'total_books': total_books,
            'books_this_month': books_this_month,
            'estimated_revenue': round(total_revenue, 2),
            's3_books': s3_books,
            'recent_books': recent_books,
            'automation_status': 'active' if self.s3 else 'local_only',
            'last_updated': datetime.now().isoformat()
        }
    
    def log_book_generation(self, title, topic, word_count=0):
        """Log a new book generation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estimate revenue based on genre and word count
        estimated_revenue = self._calculate_estimated_revenue(topic, word_count)
        
        cursor.execute("""
            INSERT INTO books (title, topic, generated_date, word_count, estimated_revenue)
            VALUES (?, ?, ?, ?, ?)
        """, (title, topic, datetime.now().date(), word_count, estimated_revenue))
        
        # Update daily stats
        today = datetime.now().date()
        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats (date, books_generated, total_revenue, automation_runs)
            VALUES (?, 
                COALESCE((SELECT books_generated FROM daily_stats WHERE date = ?), 0) + 1,
                COALESCE((SELECT total_revenue FROM daily_stats WHERE date = ?), 0) + ?,
                COALESCE((SELECT automation_runs FROM daily_stats WHERE date = ?), 0) + 1
            )
        """, (today, today, today, estimated_revenue, today))
        
        conn.commit()
        conn.close()
    
    def _calculate_estimated_revenue(self, topic, word_count):
        """Calculate estimated revenue based on book characteristics"""
        base_revenue = 2.50  # Base $2.50 per book
        
        # Bonus for longer books
        if word_count > 5000:
            base_revenue += 1.00
        elif word_count > 3000:
            base_revenue += 0.50
        
        # Bonus for popular topics
        popular_topics = ['puzzle', 'adventure', 'mystery', 'space', 'dinosaur']
        if any(topic.lower() in topic.lower() for topic in popular_topics):
            base_revenue += 0.75
        
        return base_revenue

dashboard = PassiveIncomeDashboard()

@app.route('/')
def index():
    """Main dashboard view"""
    stats = dashboard.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    return jsonify(dashboard.get_dashboard_stats())

@app.route('/api/trigger-generation', methods=['POST'])
def trigger_generation():
    """Manually trigger book generation"""
    data = request.get_json()
    topic = data.get('topic', 'Random Adventure Quest')
    
    # Import and run mission control
    try:
        from mission_control import MissionControl
        mc = MissionControl()
        results = mc.execute_full_mission(topic)
        
        # Log the generation
        dashboard.log_book_generation(
            title=results.get('book_title', topic),
            topic=topic,
            word_count=results.get('word_count', 3000)
        )
        
        return jsonify({
            'success': True,
            'message': f'Book "{topic}" generated successfully',
            'files_created': len(results.get('files_created', []))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Generation failed: {str(e)}'
        }), 500

@app.route('/api/books')
def api_books():
    """Get list of all generated books"""
    conn = sqlite3.connect(dashboard.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, topic, generated_date, word_count, estimated_revenue, status
        FROM books 
        ORDER BY generated_date DESC
    """)
    
    books = []
    for row in cursor.fetchall():
        books.append({
            'title': row[0],
            'topic': row[1],
            'generated_date': row[2],
            'word_count': row[3],
            'estimated_revenue': row[4],
            'status': row[5]
        })
    
    conn.close()
    return jsonify(books)

if __name__ == '__main__':
    print("🚀 Starting Passive Income Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("💰 Monitor your automated KDP business in real-time")
    app.run(host='0.0.0.0', port=5000, debug=True)