"""
CEO Portfolio Dashboard - Daily executive summary of all series
Generates comprehensive portfolio report for CEO decision making
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    CEO Portfolio Dashboard Lambda handler.
    Runs daily to generate executive portfolio summary.
    """
    try:
        logger.info("📊 CEO PORTFOLIO DASHBOARD ACTIVATED")
        logger.info(f"Event received: {json.dumps(event, indent=2)}")

        # Import dependencies
        from kindlemint.portfolio.portfolio_manager import PortfolioManager

        # Initialize portfolio manager
        portfolio = PortfolioManager()

        # Generate comprehensive portfolio summary
        logger.info("📈 Generating portfolio summary...")
        portfolio_summary = portfolio.get_portfolio_summary()

        if not portfolio_summary:
            logger.error("Failed to generate portfolio summary")
            return create_error_response("Portfolio summary generation failed")

        # Generate CEO dashboard report
        dashboard_report = generate_ceo_report(portfolio_summary)

        # Send to Slack
        send_ceo_dashboard(dashboard_report)

        logger.info("✅ CEO Portfolio Dashboard completed successfully")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "message": "CEO Portfolio Dashboard generated successfully",
                    "summary": {
                        "total_series": portfolio_summary["total_series"],
                        "active_series": portfolio_summary["active_series"],
                        "total_daily_revenue": portfolio_summary["total_daily_revenue"],
                        "total_books": portfolio_summary["total_books_published"],
                    },
                    "generated_at": datetime.utcnow().isoformat(),
                    "version": "3.0",
                }
            ),
        }

    except Exception as e:
        logger.error(f"❌ CEO Portfolio Dashboard failed: {str(e)}")

        return create_error_response(f"Dashboard generation failed: {str(e)}")


def generate_ceo_report(portfolio_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Generate structured CEO dashboard report."""
    try:
        # Executive summary metrics
        executive_summary = {
            "total_series": portfolio_summary["total_series"],
            "active_series": portfolio_summary["active_series"],
            "total_daily_revenue": round(portfolio_summary["total_daily_revenue"], 2),
            "total_books_published": portfolio_summary["total_books_published"],
            "monthly_projection": round(
                portfolio_summary["total_daily_revenue"] * 30, 2
            ),
        }

        # Status breakdown
        status_breakdown = portfolio_summary["status_breakdown"]

        # Top performers analysis
        top_performers = portfolio_summary["top_performers"][:3]  # Top 3

        # Series requiring attention (awaiting approval, low performers)
        full_portfolio = portfolio_summary["full_portfolio"]
        awaiting_approval = [
            s for s_var in full_portfolio if s["status"] == "AWAITING_APPROVAL"
        ]
        low_performers = [
            s
            for s_var in full_portfolio
            if float(s.get("daily_revenue", 0)) < 10
            and s["status"] not in ["AWAITING_APPROVAL", "CANCELLED"]
        ]

        # Performance trends (simplified - could be enhanced with historical data)
        performance_grade = calculate_performance_grade(executive_summary)

        return {
            "executive_summary": executive_summary,
            "performance_grade": performance_grade,
            "status_breakdown": status_breakdown,
            "top_performers": top_performers,
            "awaiting_approval": awaiting_approval,
            "requires_attention": low_performers,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "report_date": datetime.utcnow().strftime("%B %d, %Y"),
        }

    except Exception as e:
        logger.error(f"Failed to generate CEO report: {e}")
        raise


def calculate_performance_grade(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall portfolio performance grade."""
    try:
        daily_revenue = summary["total_daily_revenue"]
        summary["active_series"]

        # Grading criteria
        if daily_revenue >= 300:
            grade = "A+"
            status = "🚀 EXCEEDING TARGET"
        elif daily_revenue >= 200:
            grade = "A"
            status = "✅ ON TARGET"
        elif daily_revenue >= 100:
            grade = "B"
            status = "⚠️ BELOW TARGET"
        elif daily_revenue >= 50:
            grade = "C"
            status = "🔄 BUILDING MOMENTUM"
        else:
            grade = "D"
            status = "📈 EARLY STAGE"

        return {
            "grade": grade,
            "status": status,
            "daily_revenue": daily_revenue,
            "target_revenue": 300,
            "progress_percentage": min(round((daily_revenue / 300) * 100, 1), 100),
        }

    except Exception as e:
        logger.error(f"Failed to calculate performance grade: {e}")
        return {
            "grade": "N/A",
            "status": "Error calculating grade",
            "progress_percentage": 0,
        }


    """Send Ceo Dashboard"""
def send_ceo_dashboard(report: Dict[str, Any]):
    """Send formatted CEO dashboard to Slack."""
    try:
        import requests

        slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
        if not slack_webhook:
            logger.warning("No Slack webhook configured")
            return

        # Format executive summary
        summary = report["executive_summary"]
        grade = report["performance_grade"]

        # Format top performers
        top_performers_text = ""
        for i, performer in enumerate(report["top_performers"], 1):
            revenue = float(performer.get("daily_revenue", 0))
            books = int(performer.get("total_books_published", 0))
            top_performers_text += f"{i}. *{performer['brand_name']}* - ${revenue:.2f}/day ({books} books)\n"

        if not top_performers_text:
            top_performers_text = "No revenue-generating series yet"

        # Format awaiting approval
        approval_text = ""
        for series in report["awaiting_approval"][:3]:  # Show top 3
            score = series.get("market_score", 0)
            est_revenue = series.get("estimated_daily_revenue", 0)
            approval_text += f"• *{series['niche_topic']}* (Score: {score}, Est: ${est_revenue}/day)\n"

        if not approval_text:
            approval_text = "No series awaiting approval"

        # Create Slack message
        message = {
            "text": f"📊 CEO PORTFOLIO DASHBOARD - {report['report_date']}",
            "attachments": [
                {
                    "color": get_grade_color(grade["grade"]),
                    "fields": [
                        {
                            "title": f"{grade['status']} ({grade['grade']})",
                            "value": f"${summary['total_daily_revenue']}/day • {grade['progress_percentage']}% to target",
                            "short": False,
                        }
                    ],
                },
                {
                    "color": "good",
                    "fields": [
                        {
                            "title": "📈 Executive Summary",
                            "value": f"*Series*: {summary['active_series']} active / {summary['total_series']} total\n*Revenue*: ${summary['total_daily_revenue']}/day (${summary['monthly_projection']}/month)\n*Books*: {summary['total_books_published']} published",
                            "short": True,
                        },
                        {
                            "title": "🏆 Top Performers",
                            "value": top_performers_text,
                            "short": True,
                        },
                    ],
                },
                {
                    "color": "warning",
                    "fields": [
                        {
                            "title": "⏳ Awaiting CEO Approval",
                            "value": approval_text,
                            "short": False,
                        }
                    ],
                },
            ],
        }

        # Send to Slack
        response = requests.post(slack_webhook, json=message, timeout=10)

        if response.status_code == 200:
            logger.info("✅ CEO dashboard sent successfully")
        else:
            logger.warning(f"Slack notification failed: {response.status_code}")

    except Exception as e:
        logger.error(f"Failed to send CEO dashboard: {e}")


def get_grade_color(grade: str) -> str:
    """Get Slack color for performance grade."""
    colors = {"A+": "good", "A": "good", "B": "warning", "C": "warning", "D": "danger"}
    return colors.get(grade, "warning")


def create_error_response(error_message: str) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "statusCode": 500,
        "body": json.dumps(
            {
                "status": "error",
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "3.0",
            }
        ),
    }


if __name__ == "__main__":
    # For local testing
    test_event = {"source": "manual_test"}

    class MockContext:
            """  Init  """
def __init__(self):
            self.function_name = "ceo-portfolio-dashboard"
            self.memory_limit_in_mb = 512

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
