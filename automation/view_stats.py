#!/usr/bin/env python3
"""
Simple statistics viewer for passive income tracking
"""
import sqlite3
import os
from datetime import datetime

def view_stats():
    """Display comprehensive passive income statistics"""
    db_path = 'passive_income.db'
    
    if not os.path.exists(db_path):
        print("No statistics available yet. Run automation first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("AI KINDLEMINT PASSIVE INCOME STATS")
    print("=" * 40)
    
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
    
    print(f"Total Books Generated: {total_books}")
    print(f"Books This Month: {books_this_month}")
    print(f"Estimated Revenue: ${total_revenue:.2f}")
    print(f"Average per Book: ${total_revenue/max(1,total_books):.2f}")
    
    # Recent books
    print("\nRECENT BOOKS:")
    print("-" * 40)
    cursor.execute("""
        SELECT title, topic, generated_date, estimated_revenue 
        FROM books 
        ORDER BY generated_date DESC 
        LIMIT 10
    """)
    
    for book in cursor.fetchall():
        date = book[2][:10] if book[2] else "Unknown"
        print(f"{date} | ${book[3]:.2f} | {book[0]}")
    
    # Automation log
    print("\nRECENT AUTOMATION ACTIVITY:")
    print("-" * 40)
    cursor.execute("""
        SELECT timestamp, action, status 
        FROM automation_log 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    
    for log in cursor.fetchall():
        timestamp = log[0][:16] if log[0] else "Unknown"
        print(f"{timestamp} | {log[1]} | {log[2]}")
    
    conn.close()

if __name__ == '__main__':
    view_stats()