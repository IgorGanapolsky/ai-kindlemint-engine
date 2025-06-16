"""
Email notification system for Mission Control
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_notification(subject, body, to=None):
    """Send email notification when books are published"""
    
    # Get email credentials from environment
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_password:
        print("⚠️ Email credentials not configured - notification skipped")
        return False
    
    if not to:
        to = "iganapolsky@gmail.com"
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject
        
        # Add timestamp to body
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_body = f"{body}\n\nSent: {timestamp}\nFrom: AI KindleMint Engine"
        
        msg.attach(MIMEText(full_body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to, text)
        server.quit()
        
        print(f"📧 Email notification sent to {to}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def send_book_published_notification(book_title, kdp_file_path):
    """Send notification when a book is published to KDP"""
    subject = "✅ Book Published to Amazon KDP"
    body = f"""
Your AI KindleMint Engine has successfully published a new book!

Book Title: {book_title}
File: {kdp_file_path}
Status: Live on Amazon KDP (pending review)
Expected: Available within 24-72 hours

Your automated publishing system is working perfectly.
Check your KDP dashboard for confirmation.

Happy publishing!
"""
    return send_notification(subject, body)

def send_mission_complete_notification(book_title, files_created, duration):
    """Send notification when a complete mission cycle finishes"""
    subject = "🚀 Mission Control Complete"
    body = f"""
Mission Control has completed a full automation cycle!

Book Generated: {book_title}
Files Created: {files_created}
Duration: {duration:.1f} seconds
Status: Ready for publishing

Your AI-powered book creation system generated:
- Complete manuscript
- Marketing content
- Social media posts
- Analytics reports

Next step: Publish to Amazon KDP via webhook or manual upload.
"""
    return send_notification(subject, body)

def send_weekly_report(books_published, total_files, revenue_estimate):
    """Send weekly analytics report"""
    subject = "📊 Weekly KindleMint Report"
    body = f"""
Weekly AI KindleMint Engine Report

Books Published: {books_published}
Total Files Generated: {total_files}
Estimated Revenue Potential: ${revenue_estimate:.2f}

Your automated publishing pipeline is generating consistent content.
Keep up the great work!

System Status: All agents operational
Next Scheduled Run: In 7 days
"""
    return send_notification(subject, body)