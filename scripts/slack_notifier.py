#!/usr/bin/env python3
"""
Slack Notifier - Reusable Slack notification helper for KindleMint Engine
Provides rich notifications for batch processing, errors, and market research
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

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
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)

        if not self.enabled:
            logger.warning("Slack notifications disabled - SLACK_WEBHOOK_URL not set")
        else:
            logger.info("Slack notifier initialized")

        if SENTRY_AVAILABLE:
            add_breadcrumb(
                "Slack notifier initialized",
                category="notification",
                data={"enabled": self.enabled},
            )

    def send_message(
        self, text: str, blocks: Optional[List[Dict]] = None, color: str = "#2c3e50"
    ) -> bool:
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
                payload["attachments"] = [{"color": color, "text": text}]

            if SENTRY_AVAILABLE:
                add_breadcrumb(
                    "Sending Slack notification",
                    category="notification",
                    data={"text": text[:50] + "..." if len(text) > 50 else text},
                )

            # Send the message
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code != 200:
                logger.error(
                    f"Slack API error: {response.status_code} - {response.text}"
                )
                if SENTRY_AVAILABLE:
                    capture_kdp_error(
                        Exception(f"Slack API error: {response.status_code}"),
                        {"response": response.text},
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
        success_rate = (
            (books_succeeded / books_processed * 100) if books_processed > 0 else 0
        )

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
        if books_processed:
            avg_seconds = total_time / books_processed
            f"{int(avg_seconds // 60)}m {int(avg_seconds % 60)}s"

        # Optional business metrics expected from BatchProcessor
        total_profit = batch_results.get("total_profit")
        avg_profit_per_book = batch_results.get("avg_profit_per_book")
        previous_success_rate = batch_results.get(
            "previous_success_rate"
        )  # e.g. read from history
        avg_qa_score = batch_results.get("avg_qa_score")
        production_efficiency = batch_results.get("production_efficiency")
        kdp_ready_count = batch_results.get("kdp_ready_count", 0)
        roi_percentage = batch_results.get("roi_percentage")
        cost_per_book = batch_results.get("cost_per_book")
        total_cost = batch_results.get("total_cost")

        # Determine color based on success rate and QA score
        if success_rate == 100 and (avg_qa_score is None or avg_qa_score >= 85):
            color = "#2ecc71"  # Green
            emoji = "✅"
            status_text = "EXCELLENT"
        elif success_rate >= 80 and (avg_qa_score is None or avg_qa_score >= 70):
            color = "#f39c12"  # Orange
            emoji = "⚠️"
            status_text = "NEEDS REVIEW"
        else:
            color = "#e74c3c"  # Red
            emoji = "❌"
            status_text = "CRITICAL ISSUES"

        # Create rich message with blocks - EXECUTIVE DASHBOARD HEADER
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 EXECUTIVE DASHBOARD: BATCH {batch_id}",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Status: {status_text}* {emoji}"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*📚 PRODUCTION SUMMARY*"},
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Books Processed:*\n{books_processed}",
                    },
                    {"type": "mrkdwn", "text": f"*Success Rate:*\n{success_rate:.1f}%"},
                    {"type": "mrkdwn", "text": f"*Succeeded:*\n{books_succeeded}"},
                    {"type": "mrkdwn", "text": f"*Failed:*\n{books_failed}"},
                    {"type": "mrkdwn", "text": f"*Total Time:*\n{time_str}"},
                    {"type": "mrkdwn", "text": f"*Batch ID:*\n{batch_id}"},
                ],
            },
        ]

        # FINANCIAL METRICS SECTION
        financial_fields: List[Dict[str, str]] = []

        if total_profit is not None:
            profit_emoji = "💰" if total_profit > 0 else "📉"
            financial_fields.append(
                {
                    "type": "mrkdwn",
                    "text": f"*Total Profit:*\n{profit_emoji} ${total_profit:.2f}",
                }
            )

        if avg_profit_per_book is not None:
            financial_fields.append(
                {
                    "type": "mrkdwn",
                    "text": f"*Avg Profit/Book:*\n${avg_profit_per_book:.2f}",
                }
            )

        if cost_per_book is not None:
            financial_fields.append(
                {"type": "mrkdwn", "text": f"*Cost/Book:*\n${cost_per_book:.2f}"}
            )

        if total_cost is not None:
            financial_fields.append(
                {"type": "mrkdwn", "text": f"*Total Cost:*\n${total_cost:.2f}"}
            )

        if roi_percentage is not None:
            roi_emoji = (
                "🚀" if roi_percentage > 100 else ("✅" if roi_percentage > 0 else "❌")
            )
            financial_fields.append(
                {"type": "mrkdwn", "text": f"*ROI:*\n{roi_emoji} {roi_percentage:.1f}%"}
            )

        if financial_fields:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*💰 FINANCIAL IMPACT*"},
                    "fields": financial_fields,
                }
            )

        # QUALITY ASSURANCE SECTION - Enhanced with multi-model validation results
        qa_fields: List[Dict[str, str]] = []

        if avg_qa_score is not None:
            qa_emoji = (
                "✅" if avg_qa_score >= 85 else ("⚠️" if avg_qa_score >= 70 else "❌")
            )
            qa_fields.append(
                {
                    "type": "mrkdwn",
                    "text": f"*Avg QA Score:*\n{qa_emoji} {avg_qa_score}/100",
                }
            )
            qa_fields.append(
                {
                    "type": "mrkdwn",
                    "text": f"*KDP Ready:*\n{kdp_ready_count}/{books_processed} books",
                }
            )

            # Calculate quality improvement if previous data available
            if previous_success_rate is not None:
                delta = success_rate - previous_success_rate
                delta_emoji = "🔼" if delta > 0 else ("🔽" if delta < 0 else "➡️")
                qa_fields.append(
                    {
                        "type": "mrkdwn",
                        "text": f"*Quality Trend:*\n{delta_emoji} {abs(delta):.1f}% vs last run",
                    }
                )

        if production_efficiency is not None:
            efficiency_emoji = (
                "⚡"
                if production_efficiency < 300
                else ("⏱️" if production_efficiency < 600 else "🐢")
            )
            qa_fields.append(
                {
                    "type": "mrkdwn",
                    "text": f"*Production Speed:*\n{efficiency_emoji} {production_efficiency:.1f}s/book",
                }
            )

        if qa_fields:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*🔍 QUALITY METRICS*"},
                    "fields": qa_fields,
                }
            )

        # MULTI-MODEL VALIDATION INSIGHTS
        # Extract model-specific validation results from book QA reports
        model_validation_results: Dict[str, List[str]] = {}
        model_consensus_scores: List[int] = []

        def _load_qa_data(raw: Any) -> Optional[Dict]:
            """Return QA dict if possible else None."""
            if isinstance(raw, dict):
                return raw
            if isinstance(raw, str):
                p = Path(raw)
                if p.exists():
                    try:
                        with p.open("r") as fp:
                            return json.load(fp)
                    except Exception:
                        logger.debug("Unable to load QA report JSON from %s", p)
            return None

        for book_id, book_result in batch_results.get("book_results", {}).items():
            title = book_result.get("title", book_id)

            # Prefer nested artifacts QA report
            qa_raw = book_result.get("artifacts", {}).get("qa_report")
            if qa_raw is None:  # fallback to legacy
                qa_raw = book_result.get("qa_report")

            qa_data = _load_qa_data(qa_raw)
            if not qa_data:
                continue

            # Extract multi-model validation results
            llm_validation = qa_data.get("checks", {}).get("llm_content_validation", {})

            # Get consensus score
            consensus_score = llm_validation.get("consensus_score")
            if consensus_score is not None:
                model_consensus_scores.append(consensus_score)

            # Get model-specific results
            for model, results in llm_validation.get("validation_results", {}).items():
                if model not in model_validation_results:
                    model_validation_results[model] = []

                # Get issues from this model
                for issue in results.get("issues", []):
                    model_validation_results[model].append(f"• {title}: {issue}")

                # Get warnings from this model (limited to 3 per model)
                for warning in results.get("warnings", [])[:3]:
                    model_validation_results[model].append(f"• {title}: {warning}")

        # Add multi-model validation section if we have data
        if model_validation_results:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🤖 MULTI-MODEL VALIDATION INSIGHTS*",
                    },
                }
            )

            # Add average consensus score if available
            if model_consensus_scores:
                avg_consensus = sum(model_consensus_scores) / len(
                    model_consensus_scores
                )
                consensus_emoji = (
                    "✅"
                    if avg_consensus >= 85
                    else ("⚠️" if avg_consensus >= 70 else "❌")
                )
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Multi-Model Consensus Score:* {consensus_emoji} {avg_consensus:.1f}/100",
                        },
                    }
                )

            # Add model-specific findings
            for model, issues in model_validation_results.items():
                if issues:
                    model_name = model.upper()
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{model_name} Findings:*\n"
                                + "\n".join(issues[:5]),
                            },
                        }
                    )

                    if len(issues) > 5:
                        blocks.append(
                            {
                                "type": "context",
                                "elements": [
                                    {
                                        "type": "mrkdwn",
                                        "text": f"_...and {len(issues) - 5} more issues from {model_name}_",
                                    }
                                ],
                            }
                        )

        # CRITICAL ISSUES SECTION - Enhanced with categorization
        content_issues: List[str] = []
        layout_issues: List[str] = []
        duplicate_issues: List[str] = []

        for book_id, book_result in batch_results.get("book_results", {}).items():
            title = book_result.get("title", book_id)

            # Get QA data
            qa_raw = book_result.get("artifacts", {}).get("qa_report")
            if qa_raw is None:
                qa_raw = book_result.get("qa_report")

            qa_data = _load_qa_data(qa_raw)
            if not qa_data:
                continue

            # Categorize issues
            for issue in qa_data.get("issues_found", []):
                desc = issue.get("description", "")
                issue_entry = f"• {title}: {desc}"

                if "duplicate" in desc.lower():
                    duplicate_issues.append(issue_entry)
                elif any(
                    keyword in desc.lower()
                    for keyword in ["cut off", "cutoff", "margin"]
                ):
                    layout_issues.append(issue_entry)
                elif any(
                    keyword in desc.lower()
                    for keyword in ["content", "text", "missing"]
                ):
                    content_issues.append(issue_entry)

        # Add critical issues sections if we have data
        if duplicate_issues or layout_issues or content_issues:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🚨 CRITICAL ISSUES REQUIRING ACTION*",
                    },
                }
            )

            if duplicate_issues:
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Duplicate Content Issues:*\n"
                            + "\n".join(duplicate_issues[:3]),
                        },
                    }
                )

            if layout_issues:
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Layout & Formatting Issues:*\n"
                            + "\n".join(layout_issues[:3]),
                        },
                    }
                )

            if content_issues:
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Content Quality Issues:*\n"
                            + "\n".join(content_issues[:3]),
                        },
                    }
                )

            # Total issue count
            total_issues = (
                len(duplicate_issues) + len(layout_issues) + len(content_issues)
            )
            displayed_issues = (
                min(len(duplicate_issues), 3)
                + min(len(layout_issues), 3)
                + min(len(content_issues), 3)
            )

            if total_issues > displayed_issues:
                blocks.append(
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"_...and {total_issues - displayed_issues} more issues not shown_",
                            }
                        ],
                    }
                )

        # ACTIONABLE RECOMMENDATIONS SECTION
        recommendations: List[str] = []

        # Generate recommendations based on issues found
        if duplicate_issues:
            recommendations.append(
                "🔄 *Fix duplicate content:* Update crossword_engine_v2.py to ensure unique clues for each puzzle"
            )

        if layout_issues:
            recommendations.append(
                "📏 *Address layout issues:* Adjust margins in book_layout_bot.py to prevent text cutoff"
            )

        if content_issues:
            recommendations.append(
                "📝 *Improve content quality:* Review and enhance content generation templates"
            )

        if avg_qa_score is not None and avg_qa_score < 70:
            recommendations.append(
                "🔍 *Enhance QA process:* Implement pre-publishing validation step with Claude Artifacts"
            )

        if books_failed > 0:
            recommendations.append(
                "🛠️ *Debug failed books:* Check error logs and fix root causes"
            )

        if production_efficiency is not None and production_efficiency > 300:
            recommendations.append(
                "⚡ *Optimize performance:* Parallelize book generation to reduce processing time"
            )

        # Add business recommendations
        if avg_profit_per_book is not None:
            if avg_profit_per_book < 3:
                recommendations.append(
                    "💰 *Increase profit margins:* Adjust pricing strategy or reduce production costs"
                )
            else:
                recommendations.append(
                    "📈 *Scale production:* Current profit margins support scaling to 5+ books/week"
                )

        # Add recommendations section if we have data
        if recommendations:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*💡 ACTIONABLE RECOMMENDATIONS*\n"
                        + "\n".join(recommendations),
                    },
                }
            )

        # BUSINESS IMPACT SUMMARY
        if total_profit is not None or avg_qa_score is not None:
            impact_text = "*📊 BUSINESS IMPACT SUMMARY*\n"

            # Financial impact
            if total_profit is not None:
                if total_profit > 0:
                    impact_text += f"• *Profitable batch* generating ${
                        total_profit:.2f} in estimated revenue\n"
                else:
                    impact_text += f"• *Unprofitable batch* with ${
                        abs(total_profit):.2f} estimated loss\n"

            # Quality impact
            if avg_qa_score is not None:
                if avg_qa_score >= 85:
                    impact_text += (
                        "• *Publication-ready quality* with minimal review needed\n"
                    )
                elif avg_qa_score >= 70:
                    impact_text += (
                        "• *Good quality* but requires review before publishing\n"
                    )
                else:
                    impact_text += "• *Quality issues detected* requiring significant improvements\n"

            # Production efficiency
            if production_efficiency is not None:
                weekly_capacity = int((7 * 24 * 60 * 60) / production_efficiency)
                impact_text += f"• Current capacity: *{
                    weekly_capacity} books/week* at this efficiency\n"

            # KDP readiness
            if kdp_ready_count is not None:
                if kdp_ready_count == books_processed:
                    impact_text += (
                        "• *All books ready for KDP* - proceed to publishing\n"
                    )
                elif kdp_ready_count > 0:
                    impact_text += f"• *{kdp_ready_count}/{
                        books_processed} books ready for KDP* - partial publishing possible\n"
                else:
                    impact_text += (
                        "• *No books ready for KDP* - fix critical issues first\n"
                    )

            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": impact_text}}
            )

        # Add report link
        report_dir = Path(f"batch_reports/{batch_id}")
        if report_dir.exists():
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📁 DETAILED REPORTS*\n• Batch Summary: `{report_dir}/batch_summary.md`\n• Full JSON Data: `{report_dir}/batch_report.json`",
                    },
                }
            )

        # Add timestamp and footer
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | KindleMint Engine v2.0",
                    }
                ],
            }
        )

        # Send the notification
        return self.send_message(
            text=f"📊 Executive Dashboard: Batch {
                batch_id} - {books_succeeded}/{books_processed} books successful ({success_rate:.1f}%)",
            blocks=blocks,
            color=color,
        )

    def send_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict] = None,
    ) -> bool:
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
                "text": {"type": "plain_text", "text": f"❌ KindleMint Engine Error"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Error:* {message}"},
            },
        ]

        # Add exception details if provided
        if error:
            error_type = type(error).__name__
            error_msg = str(error)
            blocks.append(
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Type:*\n{error_type}"},
                        {"type": "mrkdwn", "text": f"*Message:*\n{error_msg[:100]}..."},
                    ],
                }
            )

        # Add context if provided
        if context:
            context_items = []
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)[:50] + "..."
                context_items.append(f"• *{key}*: {value}")

            if context_items:
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Context:*\n" + "\n".join(context_items[:5]),
                        },
                    }
                )

        # Add timestamp
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    }
                ],
            }
        )

        # Send the notification
        return self.send_message(
            text=f"Error: {message}", blocks=blocks, color="#e74c3c"  # Red
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
        api_count = len(
            [api for api in research_results.get("apis_tested", []) if "SUCCESS" in api]
        )
        products_found = research_results.get("amazon_products", 0)

        # Create rich message with blocks
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔍 Market Research Complete"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*APIs Working:* {api_count}"},
                    {"type": "mrkdwn", "text": f"*Products Found:* {products_found}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Sentry Tracking:* {'✅ Active' if SENTRY_AVAILABLE else '❌ Inactive'}",
                    },
                ],
            },
        ]

        # Add timestamp
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    }
                ],
            }
        )

        # Send the notification
        return self.send_message(
            text=f"Market Research Complete: {products_found} products found",
            blocks=blocks,
            color="#3498db",  # Blue
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
        start_time = datetime.fromisoformat(
            book_result.get("start_time", datetime.now().isoformat())
        )
        end_time = datetime.fromisoformat(
            book_result.get("end_time", datetime.now().isoformat())
        )
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
                    "text": f"{emoji} Book Processing: {title}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Status:*\n{status.capitalize()}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{minutes}m {seconds}s"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Steps Completed:*\n{len(book_result.get('steps_completed', []))}",
                    },
                    {"type": "mrkdwn", "text": f"*Book ID:*\n{book_id}"},
                ],
            },
        ]

        # Optional per-book business metrics
        profit_estimate = book_result.get("profit_estimate")
        qa_score = book_result.get("qa_score")
        extra_fields: List[Dict[str, str]] = []
        if profit_estimate is not None:
            extra_fields.append(
                {
                    "type": "mrkdwn",
                    "text": f"*Profit Estimate:*\n${profit_estimate:.2f}",
                }
            )
        if qa_score is not None:
            extra_fields.append(
                {"type": "mrkdwn", "text": f"*QA Score:*\n{qa_score}/100"}
            )
        if extra_fields:
            blocks[1]["fields"].extend(extra_fields)

        # Add error if failed
        if status != "complete" and book_result.get("error"):
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:*\n{book_result.get('error')}",
                    },
                }
            )

        # Add timestamp
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    }
                ],
            }
        )

        # Send the notification
        return self.send_message(
            text=f"Book Processing {status.capitalize()}: {title}",
            blocks=blocks,
            color=color,
        )


# Simple test function
def test_slack_notifier():
    """Test the Slack notifier with a simple message"""
    notifier = SlackNotifier()

    if not notifier.enabled:
        print(
            "⚠️ Slack notifications disabled - set SLACK_WEBHOOK_URL environment variable to test"
        )
        return False

    test_message = f"🧪 Test notification from KindleMint Engine at {
        datetime.now().strftime('%H:%M:%S')}"
    success = notifier.send_message(test_message, color="#3498db")

    if success:
        print("✅ Test notification sent successfully!")
    else:
        print("❌ Failed to send test notification")

    return success


if __name__ == "__main__":
    # Run test if executed directly
    test_slack_notifier()
