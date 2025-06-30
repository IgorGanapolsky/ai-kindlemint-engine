#!/usr/bin/env python3
"""
QA Notification Templates - Enhanced templates for QA validation notifications
Provides clear, actionable Slack messages for QA failures
"""

from typing import Any, Dict, List


def qa_validation_failure_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate detailed blocks for QA validation failures"""

    # Extract data
    book_title = data.get("book_title", "Unknown Book")
    volume = data.get("volume", "?")
    failure_count = data.get("failure_count", 0)
    failures = data.get("failures", [])
    passed_checks = data.get("passed_checks", [])
    warnings = data.get("warnings", [])

    # Determine severity
    if failure_count > 5:
        severity_emoji = "🚨"
        severity_color = "#FF0000"
    elif failure_count > 2:
        severity_emoji = "⚠️"
        severity_color = "#FF6600"
    else:
        severity_emoji = "⚡"
        severity_color = "#FFB347"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{severity_emoji} QA Validation Failed - {book_title}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Book:* {book_title} - Volume {volume}\n*Status:* {failure_count} validation failures detected",
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "View Details"},
                "url": data.get("github_url", "#"),
                "action_id": "view_details",
            },
        },
        {"type": "divider"},
    ]

    # Add failure details
    if failures:
        failure_text = "*❌ Failed Checks:*\n"
        for i, failure in enumerate(failures[:5]):  # Show first 5
            failure_text += f"{i + 1}. {failure}\n"
        if len(failures) > 5:
            failure_text += f"_...and {len(failures) - 5} more_"

        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": failure_text}}
        )

    # Add warnings if any
    if warnings:
        warning_text = "*⚠️ Warnings:*\n"
        for i, warning in enumerate(warnings[:3]):  # Show first 3
            warning_text += f"• {warning}\n"

        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": warning_text}}
        )

    # Add passed checks summary
    if passed_checks:
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"✅ *{len(passed_checks)} checks passed*",
                    }
                ],
            }
        )

    # Add resolution status
    blocks.append({"type": "divider"})

    if data.get("auto_resolution_attempted", False):
        resolution_status = data.get("resolution_status", {})
        if resolution_status.get("success"):
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🤖 *Auto-Resolution:* ✅ Successfully fixed {resolution_status.get('fixes_applied', 0)} issues",
                    },
                }
            )
        else:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🤖 *Auto-Resolution:* ❌ Unable to fix automatically\n*Reason:* {resolution_status.get('reason', 'Unknown')}",
                    },
                }
            )
    else:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🤖 *Auto-Resolution:* Attempting to fix automatically...",
                },
            }
        )

    # Add action buttons
    blocks.append(
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Re-run Validation"},
                    "style": "primary",
                    "action_id": "rerun_validation",
                    "value": f"{book_title}|{volume}",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Logs"},
                    "action_id": "view_logs",
                    "url": data.get("logs_url", "#"),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Manual Fix Guide"},
                    "action_id": "manual_fix",
                    "url": "https://github.com/IgorGanapolsky/ai-kindlemint-engine/wiki/QA-Validation-Fixes",
                },
            ],
        }
    )

    # Add helpful context
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Environment: *{data.get('environment', 'production')}* | "
                    f"Workflow: *{data.get('workflow', 'QA Validation')}* | "
                    f"Run ID: `{data.get('run_id', 'unknown')}`",
                }
            ],
        }
    )

    return blocks


def qa_resolution_success_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for successful QA resolution"""

    book_title = data.get("book_title", "Unknown Book")
    fixes_applied = data.get("fixes_applied", 0)
    time_taken = data.get("time_taken", 0)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"✅ QA Issues Resolved - {book_title}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Status:* All validation issues have been automatically resolved\n"
                f"*Fixes Applied:* {fixes_applied}\n"
                f"*Time Taken:* {time_taken:.1f} seconds",
            },
        },
        {"type": "section", "fields": [{"type": "mrkdwn", "text": "*Actions Taken:*"}]},
    ]

    # List actions taken
    actions = data.get("actions_taken", [])
    for action in actions:
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": f"• {action}"}}
        )

    # Add next steps
    blocks.append({"type": "divider"})

    blocks.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Next Steps:*\n"
                "• Book is ready for production\n"
                "• No manual intervention required\n"
                "• QA validation passed successfully",
            },
        }
    )

    return blocks


def qa_summary_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate daily/weekly QA summary blocks"""

    total_validations = data.get("total_validations", 0)
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    auto_fixed = data.get("auto_fixed", 0)
    manual_fixes = data.get("manual_fixes_needed", 0)

    pass_rate = (passed / total_validations * 100) if total_validations > 0 else 0
    auto_fix_rate = (auto_fixed / failed * 100) if failed > 0 else 0

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 QA Validation Summary - {data.get('period', 'Daily')}",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Validations:*\n{total_validations}",
                },
                {"type": "mrkdwn", "text": f"*Pass Rate:*\n{pass_rate:.1f}%"},
                {"type": "mrkdwn", "text": f"*Passed:*\n✅ {passed}"},
                {"type": "mrkdwn", "text": f"*Failed:*\n❌ {failed}"},
                {"type": "mrkdwn", "text": f"*Auto-Fixed:*\n🤖 {auto_fixed}"},
                {"type": "mrkdwn", "text": f"*Manual Fixes:*\n👤 {manual_fixes}"},
            ],
        },
    ]

    # Add common failure reasons
    if data.get("common_failures"):
        failure_text = "*Most Common Failures:*\n"
        for reason, count in data.get("common_failures", {}).items()[:5]:
            failure_text += f"• {reason}: {count} occurrences\n"

        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": failure_text}}
        )

    # Add improvement suggestions
    if auto_fix_rate < 70:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💡 *Improvement Opportunity:*\n"
                    f"Auto-fix rate is {auto_fix_rate:.1f}%. Consider:\n"
                    f"• Adding more resolution strategies\n"
                    f"• Updating validation rules\n"
                    f"• Reviewing common failure patterns",
                },
            }
        )

    return blocks
