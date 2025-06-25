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

# --------------------------------------------------------------------------- #
# Load environment variables from a .env file (if present)
# --------------------------------------------------------------------------- #
from dotenv import load_dotenv

# Assume the repository root contains `.env`
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

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
        
        # ------------------------------------------------------------------ #
        # Business / efficiency metrics — taken only if provided so that
        # older batch_result structures remain compatible.
        # ------------------------------------------------------------------ #
        avg_time_per_book = "N/A"
        if books_processed:
            avg_seconds = total_time / books_processed
            avg_time_per_book = f"{int(avg_seconds // 60)}m {int(avg_seconds % 60)}s"

        # Optional business metrics expected from BatchProcessor
        total_profit          = batch_results.get("total_profit")
        avg_profit_per_book   = batch_results.get("avg_profit_per_book")
        previous_success_rate = batch_results.get("previous_success_rate")  # e.g. read from history
        avg_qa_score          = batch_results.get("avg_qa_score")
        production_efficiency = batch_results.get("production_efficiency")
        kdp_ready_count       = batch_results.get("kdp_ready_count", 0)
        roi_percentage        = batch_results.get("roi_percentage")
        cost_per_book         = batch_results.get("cost_per_book")

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

        # Insert efficiency metrics
        efficiency_fields: List[Dict[str, str]] = []

        efficiency_fields.append({"type": "mrkdwn", "text": f"*Avg Time/Book:*\n{avg_time_per_book}"})

        if avg_qa_score is not None:
            efficiency_fields.append({"type": "mrkdwn", "text": f"*Avg QA Score:*\n{avg_qa_score}/100"})
        if avg_profit_per_book is not None:
            efficiency_fields.append({"type": "mrkdwn", "text": f"*Avg Profit/Book:*\n${avg_profit_per_book:.2f}"})
        if total_profit is not None:
            efficiency_fields.append({"type": "mrkdwn", "text": f"*Total Profit:*\n${total_profit:.2f}"})
        if previous_success_rate is not None:
            delta = success_rate - previous_success_rate
            sign  = "▲" if delta >= 0 else "▼"
            efficiency_fields.append(
                {"type": "mrkdwn",
                 "text": f"*Δ Success Rate:*\n{sign}{abs(delta):.1f}% vs last run"}
            )
        if roi_percentage is not None:
            efficiency_fields.append({"type": "mrkdwn", "text": f"*ROI:*\n{roi_percentage:.1f}%"})
        if cost_per_book is not None:
            efficiency_fields.append({"type": "mrkdwn", "text": f"*Cost/Book:*\n${cost_per_book:.2f}"})

        if efficiency_fields:
            blocks.append(
                {
                    "type": "section",
                    "fields": efficiency_fields
                }
            )
        
        # ------------------------------------------------------------------ #
        # Quality Assurance & Insights Section
        # ------------------------------------------------------------------ #
        qa_insights_fields: List[Dict[str, str]] = []
        qa_status_emoji = "❓"
        qa_status_text = "Unknown"

        if avg_qa_score is not None:
            if avg_qa_score >= 85:
                qa_status_emoji = "✅"
                qa_status_text = "Excellent"
            elif avg_qa_score >= 70:
                qa_status_emoji = "⚠️"
                qa_status_text = "Good, but needs review"
            else:
                qa_status_emoji = "❌"
                qa_status_text = "Critical issues found"
            
            qa_insights_fields.append({"type": "mrkdwn", "text": f"*Overall QA Score:*\n{avg_qa_score}/100 {qa_status_emoji}"})
            qa_insights_fields.append({"type": "mrkdwn", "text": f"*KDP Ready Books:*\n{kdp_ready_count}/{books_processed}"})
        else:
            qa_insights_fields.append({"type": "mrkdwn", "text": "*Overall QA Score:*\nN/A"})
            qa_insights_fields.append({"type": "mrkdwn", "text": "*KDP Ready Books:*\nN/A"})

        critical_issues_list = []
        for book_id, book_result in batch_results.get("book_results", {}).items():
            if book_result.get("status") == "failed" and book_result.get("qa_report"):
                qa_report = book_result["qa_report"]
                if "issues_found" in qa_report and qa_report["issues_found"]:
                    for issue in qa_report["issues_found"]:
                        critical_issues_list.append(f"• {book_result.get('title', book_id)}: {issue['description']}")
            elif book_result.get("qa_report") and book_result["qa_report"].get("issues_found"):
                for issue in book_result["qa_report"]["issues_found"]:
                    critical_issues_list.append(f"• {book_result.get('title', book_id)}: {issue['description']}")

        if critical_issues_list:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🚨 Critical QA Issues Found:*\n" + "\n".join(critical_issues_list[:5])
                }
            })
            if len(critical_issues_list) > 5:
                blocks.append({
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"_...and {len(critical_issues_list) - 5} more issues_"}]
                })
        
        if qa_insights_fields:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🎯 *Quality Assurance & Insights*"
                },
                "fields": qa_insights_fields
            })

        # ------------------------------------------------------------------ #
        # Actionable Insights & Production Status
        # ------------------------------------------------------------------ #
        action_items: List[str] = []
        production_status_fields: List[Dict[str, str]] = []

        if avg_qa_score is not None and avg_qa_score < 85:
            action_items.append("🚨 *Priority 1:* Review critical QA issues and fix content/layout problems.")
        if books_failed > 0:
            action_items.append("🔧 *Priority 2:* Investigate failed books and address root causes.")
        if production_efficiency is not None:
            if production_efficiency > 300:  # more than 5 minutes per book
                action_items.append("⚡ *Priority 3:* Optimize production efficiency (currently {:.1f}s/book).".format(production_efficiency))
            production_status_fields.append({"type": "mrkdwn", "text": f"*Production Efficiency:*\n{production_efficiency:.1f}s/book"})
        
        # Weekly production goals
        if books_processed > 0 and avg_profit_per_book is not None:
            weekly_target_books = 5  # Default weekly target
            weekly_profit_projection = weekly_target_books * avg_profit_per_book
            production_status_fields.append({"type": "mrkdwn", "text": f"*Weekly Goal:*\n{weekly_target_books} books (${weekly_profit_projection:.2f})"})
            
            # On track or not?
            if books_succeeded == books_processed:
                production_status_fields.append({"type": "mrkdwn", "text": f"*Status:*\nOn track ✅"})
            else:
                production_status_fields.append({"type": "mrkdwn", "text": f"*Status:*\nNeeds attention ⚠️"})

        if action_items:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "💡 *Actionable Insights:*\n" + "\n".join(action_items)
                }
            })

        if production_status_fields:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": "📈 *Production Status & Goals*"
                },
                "fields": production_status_fields
            })

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

        # Optional per-book business metrics
        profit_estimate = book_result.get("profit_estimate")
        qa_score        = book_result.get("qa_score")
        extra_fields: List[Dict[str, str]] = []
        if profit_estimate is not None:
            extra_fields.append(
                {"type": "mrkdwn", "text": f"*Profit Estimate:*\n${profit_estimate:.2f}"}
            )
        if qa_score is not None:
            extra_fields.append(
                {"type": "mrkdwn", "text": f"*QA Score:*\n{qa_score}/100"}
            )
        if extra_fields:
            blocks[1]["fields"].extend(extra_fields)
        
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
