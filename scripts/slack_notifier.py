#!/usr/bin/env python3
"""
Slack Notifier - Reusable Slack notification helper for KindleMint Engine
Provides rich notifications for batch processing, errors, and market research
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SlackNotifier")

# Try to import Sentry if available
try:
    from scripts.sentry_config import add_breadcrumb, capture_kdp_error
    SENTRY_AVAILABLE = True
except ImportError:
    logger.warning("Sentry integration not available")
    SENTRY_AVAILABLE = False
    
    # Stub functions if Sentry is not available
    def add_breadcrumb(*args, **kwargs):
        pass
    
    def capture_kdp_error(*args, **kwargs):
        pass

class SlackNotifier:
    """
    Reusable Slack notification helper for KindleMint Engine
    
    Usage:
        notifier = SlackNotifier()
        notifier.send_batch_complete(batch_results)
        notifier.send_error("Batch processing failed", error=e)
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize the Slack notifier with webhook URL"""
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            logger.warning("Slack notifications disabled - SLACK_WEBHOOK_URL not set")
        else:
            logger.info("Slack notifier initialized")
            
        if SENTRY_AVAILABLE:
            add_breadcrumb(
                "Slack notifier initialized", 
                category="notification",
                data={"enabled": self.enabled}
            )
    
    def send_message(self, 
                     text: str, 
                     blocks: Optional[List[Dict]] = None, 
                     color: str = "#2c3e50") -> bool:
        """
        Send a message to Slack
        
        Args:
            text: Main message text
            blocks: Slack Block Kit blocks (optional)
            color: Color for attachment (default: dark blue)
            
        Returns:
            bool: True if message was sent successfully
        """
        if not self.enabled:
            logger.info(f"Slack notification would have been sent: {text}")
            return False
        
        try:
            # Prepare message payload
            payload = {
                "text": text,
            }
            
            # Add blocks if provided
            if blocks:
                payload["blocks"] = blocks
                
            # Add attachment with color if no blocks
            elif color:
                payload["attachments"] = [{
                    "color": color,
                    "text": text
                }]
            
            if SENTRY_AVAILABLE:
                add_breadcrumb(
                    "Sending Slack notification", 
                    category="notification",
                    data={"text": text[:50] + "..." if len(text) > 50 else text}
                )
            
            # Send the message
            response = requests.post(
                self.webhook_url, 
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                if SENTRY_AVAILABLE:
                    capture_kdp_error(
                        Exception(f"Slack API error: {response.status_code}"), 
                        {"response": response.text}
                    )
                return False
            
            logger.info("Slack notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            if SENTRY_AVAILABLE:
                capture_kdp_error(e, {"operation": "slack_notification"})
            return False
    
    def send_batch_complete(self, batch_results: Dict) -> bool:
        """
        Send batch completion notification with rich formatting
        
        Args:
            batch_results: Batch processing results dictionary
            
        Returns:
            bool: True if message was sent successfully
        """
        # Extract key metrics
        batch_id = batch_results.get("batch_id", "unknown")
        books_processed = batch_results.get("books_processed", 0)
        books_succeeded = batch_results.get("books_succeeded", 0)
        books_failed = batch_results.get("books_failed", 0)
        success_rate = (books_succeeded / books_processed * 100) if books_processed > 0 else 0
        
        # Calculate time
        total_time = batch_results.get("total_time_seconds", 0)
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        seconds = total_time % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Determine color based on success rate
        if success_rate == 100:
            color = "#2ecc71"  # Green
            emoji = "✅"
        elif success_rate >= 80:
            color = "#f39c12"  # Orange
            emoji = "⚠️"
        else:
            color = "#e74c3c"  # Red
            emoji = "❌"
        
        # Create rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Batch Processing Complete: {batch_id}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Books Processed:*\n{books_processed}"},
                    {"type": "mrkdwn", "text": f"*Success Rate:*\n{success_rate:.1f}%"},
                    {"type": "mrkdwn", "text": f"*Succeeded:*\n{books_succeeded}"},
                    {"type": "mrkdwn", "text": f"*Failed:*\n{books_failed}"},
                    {"type": "mrkdwn", "text": f"*Total Time:*\n{time_str}"},
                    {"type": "mrkdwn", "text": f"*Batch ID:*\n{batch_id}"}
                ]
            }
        ]
        
        # Add book details section if there are failed books
        if books_failed > 0:
            failed_books = []
            for book_id, book_result in batch_results.get("book_results", {}).items():
                if book_result.get("status") != "complete":
                    error_msg = book_result.get("error", "Unknown error")
                    failed_books.append(f"• *{book_result.get('title', book_id)}*: {error_msg[:50]}...")
            
            if failed_books:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Failed Books:*\n" + "\n".join(failed_books[:5])
                    }
                })
                
                # Add note if there are more than 5 failed books
                if len(failed_books) > 5:
                    blocks.append({
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": f"_...and {len(failed_books) - 5} more failed books_"
                        }]
                    })
        
        # Add report link
        report_dir = Path(f"batch_reports/{batch_id}")
        if report_dir.exists():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Detailed Report:*\n`{report_dir}/batch_summary.md`"
                }
            })
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }]
        })
        
        # Send the notification
        return self.send_message(
            text=f"Batch Processing Complete: {books_succeeded}/{books_processed} books successful ({success_rate:.1f}%)",
            blocks=blocks,
            color=color
        )
    
    def send_error(self, 
                  message: str, 
                  error: Optional[Exception] = None, 
                  context: Optional[Dict] = None) -> bool:
        """
        Send error notification with rich formatting
        
        Args:
            message: Error message
            error: Exception object (optional)
            context: Additional context dictionary (optional)
            
        Returns:
            bool: True if message was sent successfully
        """
        # Create rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"❌ KindleMint Engine Error"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:* {message}"
                }
            }
        ]
        
        # Add exception details if provided
        if error:
            error_type = type(error).__name__
            error_msg = str(error)
            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Type:*\n{error_type}"},
                    {"type": "mrkdwn", "text": f"*Message:*\n{error_msg[:100]}..."}
                ]
            })
        
        # Add context if provided
        if context:
            context_items = []
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)[:50] + "..."
                context_items.append(f"• *{key}*: {value}")
            
            if context_items:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Context:*\n" + "\n".join(context_items[:5])
                    }
                })
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }]
        })
        
        # Send the notification
        return self.send_message(
            text=f"Error: {message}",
            blocks=blocks,
            color="#e74c3c"  # Red
        )
    
    def send_market_research(self, research_results: Dict) -> bool:
        """
        Send market research notification with rich formatting
        
        Args:
            research_results: Market research results dictionary
            
        Returns:
            bool: True if message was sent successfully
        """
        # Extract key metrics
        api_count = len([api for api in research_results.get('apis_tested', []) 
                        if 'SUCCESS' in api])
        products_found = research_results.get('amazon_products', 0)
        
        # Create rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔍 Market Research Complete"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*APIs Working:* {api_count}"},
                    {"type": "mrkdwn", "text": f"*Products Found:* {products_found}"},
                    {"type": "mrkdwn", "text": f"*Sentry Tracking:* {'✅ Active' if SENTRY_AVAILABLE else '❌ Inactive'}"}
                ]
            }
        ]
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }]
        })
        
        # Send the notification
        return self.send_message(
            text=f"Market Research Complete: {products_found} products found",
            blocks=blocks,
            color="#3498db"  # Blue
        )
    
    def send_book_complete(self, book_result: Dict) -> bool:
        """
        Send book completion notification with rich formatting
        
        Args:
            book_result: Book processing result dictionary
            
        Returns:
            bool: True if message was sent successfully
        """
        # Extract key metrics
        book_id = book_result.get("id", "unknown")
        title = book_result.get("title", book_id)
        status = book_result.get("status", "unknown")
        
        # Calculate time
        start_time = datetime.fromisoformat(book_result.get("start_time", datetime.now().isoformat()))
        end_time = datetime.fromisoformat(book_result.get("end_time", datetime.now().isoformat()))
        duration = (end_time - start_time).total_seconds()
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        # Determine color based on status
        if status == "complete":
            color = "#2ecc71"  # Green
            emoji = "✅"
        else:
            color = "#e74c3c"  # Red
            emoji = "❌"
            
        # Create rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Book Processing: {title}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Status:*\n{status.capitalize()}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{minutes}m {seconds}s"},
                    {"type": "mrkdwn", "text": f"*Steps Completed:*\n{len(book_result.get('steps_completed', []))}"},
                    {"type": "mrkdwn", "text": f"*Book ID:*\n{book_id}"}
                ]
            }
        ]
        
        # Add error if failed
        if status != "complete" and book_result.get("error"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:*\n{book_result.get('error')}"
                }
            })
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }]
        })
        
        # Send the notification
        return self.send_message(
            text=f"Book Processing {status.capitalize()}: {title}",
            blocks=blocks,
            color=color
        )


# Simple test function
def test_slack_notifier():
    """Test the Slack notifier with a simple message"""
    notifier = SlackNotifier()
    
    if not notifier.enabled:
        print("⚠️ Slack notifications disabled - set SLACK_WEBHOOK_URL environment variable to test")
        return False
    
    test_message = f"🧪 Test notification from KindleMint Engine at {datetime.now().strftime('%H:%M:%S')}"
    success = notifier.send_message(test_message, color="#3498db")
    
    if success:
        print("✅ Test notification sent successfully!")
    else:
        print("❌ Failed to send test notification")
    
    return success


if __name__ == "__main__":
    # Run test if executed directly
    test_slack_notifier()
