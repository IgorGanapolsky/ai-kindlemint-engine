"""
Slack Notification System for Operational Monitoring
Real-time alerts for the Memory-Driven Publishing Engine.

PURPOSE: Provide operational visibility into autonomous revenue generation
BUSINESS IMPACT: Monitor system health and revenue generation in real-time
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """Notification severity levels."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SlackNotifier:
    """
    Slack notification system for operational monitoring.
    
    Provides real-time alerts for the autonomous publishing pipeline.
    """
    
    def __init__(self, webhook_url: Optional[str] = None, channel: Optional[str] = None):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url: Slack webhook URL (or set SLACK_WEBHOOK_URL env var)
            channel: Slack channel override (optional)
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.channel = channel
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured. Notifications will be logged only.")
        
        self.enabled = bool(self.webhook_url)
    
    def notify_pipeline_start(self, book_id: str, niche: str, topic: str) -> bool:
        """Notify when publishing pipeline starts."""
        return self.send_notification(
            level=NotificationLevel.INFO,
            title="🚀 Publishing Pipeline Started",
            message=f"Memory-driven pipeline initiated for profitable niche: **{niche}**",
            fields={
                "Book ID": book_id,
                "Topic": topic[:100] + "..." if len(topic) > 100 else topic,
                "Niche": niche,
                "Status": "Pipeline initiated"
            }
        )
    
    def notify_market_validation(self, book_id: str, validation_score: float, should_proceed: bool) -> bool:
        """Notify market validation results."""
        level = NotificationLevel.SUCCESS if should_proceed else NotificationLevel.WARNING
        emoji = "✅" if should_proceed else "⚠️"
        status = "PASSED" if should_proceed else "FAILED"
        
        return self.send_notification(
            level=level,
            title=f"{emoji} Market Validation {status}",
            message=f"AI persona validation score: **{validation_score:.1f}%**",
            fields={
                "Book ID": book_id,
                "Validation Score": f"{validation_score:.1f}%",
                "Decision": "Proceed with publishing" if should_proceed else "Abort publishing",
                "Cost Savings": "N/A" if should_proceed else "API costs saved by aborting low-viability topic"
            }
        )
    
    def notify_content_generated(self, book_id: str, word_count: int, chapter_count: int) -> bool:
        """Notify when content generation completes."""
        return self.send_notification(
            level=NotificationLevel.SUCCESS,
            title="📝 Content Generation Complete",
            message=f"Intelligent content creation finished successfully",
            fields={
                "Book ID": book_id,
                "Word Count": f"{word_count:,} words",
                "Chapters": f"{chapter_count} chapters",
                "Status": "Ready for publishing"
            }
        )
    
    def notify_kdp_publishing_start(self, book_id: str, title: str) -> bool:
        """Notify when KDP publishing starts."""
        return self.send_notification(
            level=NotificationLevel.INFO,
            title="🚛 KDP Publishing Started",
            message="Automated shipping department uploading book to Amazon",
            fields={
                "Book ID": book_id,
                "Title": title[:100] + "..." if len(title) > 100 else title,
                "Status": "Uploading to KDP"
            }
        )
    
    def notify_kdp_publishing_success(self, book_id: str, title: str, asin: Optional[str] = None, kdp_url: Optional[str] = None) -> bool:
        """Notify successful KDP publishing."""
        return self.send_notification(
            level=NotificationLevel.SUCCESS,
            title="🎉 BOOK PUBLISHED SUCCESSFULLY!",
            message="Revenue generation pipeline complete - book is live on Amazon!",
            fields={
                "Book ID": book_id,
                "Title": title,
                "ASIN": asin or "Pending",
                "KDP URL": kdp_url or "N/A",
                "Status": "LIVE ON AMAZON - Revenue generation active",
                "Next Step": "Monitor sales and update memory system"
            }
        )
    
    def notify_kdp_publishing_failure(self, book_id: str, title: str, errors: List[str]) -> bool:
        """Notify KDP publishing failure."""
        error_summary = "; ".join(errors[:3])  # First 3 errors
        
        return self.send_notification(
            level=NotificationLevel.ERROR,
            title="❌ KDP Publishing Failed",
            message="Automated publishing encountered errors - manual review required",
            fields={
                "Book ID": book_id,
                "Title": title[:100] + "..." if len(title) > 100 else title,
                "Errors": error_summary,
                "Total Errors": len(errors),
                "Action Required": "Review KDP publishing logs and retry"
            }
        )
    
    def notify_memory_update(self, books_processed: int, total_sales: int, total_revenue: float) -> bool:
        """Notify when memory system updates with new sales data."""
        return self.send_notification(
            level=NotificationLevel.INFO,
            title="🧠 Memory System Updated",
            message="Learning loop activated - new sales data ingested",
            fields={
                "Books Processed": books_processed,
                "Total Sales": total_sales,
                "Total Revenue": f"${total_revenue:.2f}",
                "Status": "System learning from real market data"
            }
        )
    
    def notify_profitable_niche_identified(self, niche: str, avg_roi: float, book_count: int) -> bool:
        """Notify when a highly profitable niche is identified."""
        return self.send_notification(
            level=NotificationLevel.SUCCESS,
            title="💎 Profitable Niche Identified",
            message="Memory system found high-performing niche for next book generation",
            fields={
                "Niche": niche,
                "Average ROI": f"{avg_roi:.1%}",
                "Sample Size": f"{book_count} books",
                "Recommendation": "Focus next publishing efforts on this niche"
            }
        )
    
    def notify_system_health(self, status: str, uptime_hours: float, books_generated: int, revenue_generated: float) -> bool:
        """Notify system health status."""
        level = NotificationLevel.SUCCESS if status == "healthy" else NotificationLevel.WARNING
        emoji = "💚" if status == "healthy" else "⚠️"
        
        return self.send_notification(
            level=level,
            title=f"{emoji} System Health Report",
            message=f"Memory-Driven Publishing Engine status: **{status.upper()}**",
            fields={
                "System Status": status.upper(),
                "Uptime": f"{uptime_hours:.1f} hours",
                "Books Generated": books_generated,
                "Revenue Generated": f"${revenue_generated:.2f}",
                "Performance": "Autonomous revenue generation operational"
            }
        )
    
    def notify_revenue_milestone(self, milestone: str, total_revenue: float, books_published: int, days_to_milestone: int) -> bool:
        """Notify when revenue milestones are reached."""
        return self.send_notification(
            level=NotificationLevel.SUCCESS,
            title="🎯 REVENUE MILESTONE ACHIEVED!",
            message=f"Memory-Driven Publishing Engine reached {milestone} milestone!",
            fields={
                "Milestone": milestone,
                "Total Revenue": f"${total_revenue:.2f}",
                "Books Published": books_published,
                "Time to Milestone": f"{days_to_milestone} days",
                "Achievement": "Intelligent automation delivering real revenue",
                "Next Target": "Scale to $300/day through niche domination"
            }
        )
    
    def send_notification(
        self, 
        level: NotificationLevel, 
        title: str, 
        message: str, 
        fields: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send a notification to Slack.
        
        Args:
            level: Notification severity level
            title: Notification title
            message: Main message
            fields: Additional structured data
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            # Log notification instead of sending
            logger.info(f"[{level.value.upper()}] {title}: {message}")
            if fields:
                for key, value in fields.items():
                    logger.info(f"  {key}: {value}")
            return True
        
        try:
            # Build Slack message
            slack_message = self._build_slack_message(level, title, message, fields)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=slack_message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent: {title}")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _build_slack_message(
        self, 
        level: NotificationLevel, 
        title: str, 
        message: str, 
        fields: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Build Slack message payload."""
        
        # Color mapping for different levels
        colors = {
            NotificationLevel.INFO: "#36a64f",      # Green
            NotificationLevel.SUCCESS: "#36a64f",   # Green  
            NotificationLevel.WARNING: "#ff9500",   # Orange
            NotificationLevel.ERROR: "#ff0000",     # Red
            NotificationLevel.CRITICAL: "#ff0000"   # Red
        }
        
        # Build attachment fields
        attachment_fields = []
        if fields:
            for key, value in fields.items():
                attachment_fields.append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        # Add timestamp
        attachment_fields.append({
            "title": "Timestamp",
            "value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "short": True
        })
        
        slack_message = {
            "text": f"KindleMint Alert: {title}",
            "attachments": [
                {
                    "color": colors.get(level, "#36a64f"),
                    "title": title,
                    "text": message,
                    "fields": attachment_fields,
                    "footer": "KindleMint Memory-Driven Publishing Engine",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        # Add channel override if specified
        if self.channel:
            slack_message["channel"] = self.channel
        
        return slack_message


def create_test_notifications():
    """Create test notifications to validate the system."""
    notifier = SlackNotifier()
    
    print("🔔 Testing Slack notification system...")
    
    # Test different notification types
    test_cases = [
        ("Pipeline Start", lambda: notifier.notify_pipeline_start(
            "test_book_123", "productivity", "The Ultimate Productivity Guide"
        )),
        ("Market Validation Success", lambda: notifier.notify_market_validation(
            "test_book_123", 85.5, True
        )),
        ("Content Generated", lambda: notifier.notify_content_generated(
            "test_book_123", 12500, 8
        )),
        ("KDP Publishing Success", lambda: notifier.notify_kdp_publishing_success(
            "test_book_123", "The Ultimate Productivity Guide", "B123456789"
        )),
        ("Revenue Milestone", lambda: notifier.notify_revenue_milestone(
            "$1 first revenue", 1.23, 1, 1
        ))
    ]
    
    for test_name, test_func in test_cases:
        try:
            success = test_func()
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
        except Exception as e:
            print(f"  ❌ {test_name}: {e}")
    
    print("🔔 Notification testing complete")


if __name__ == "__main__":
    create_test_notifications()