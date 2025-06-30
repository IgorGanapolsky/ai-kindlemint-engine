#!/usr/bin/env python3
"""
Notification Templates - Comprehensive templates for Slack alerts and notifications
Provides rich, consistent formatting for different types of alerts and escalations
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class NotificationTemplate:
    """Base class for notification templates"""

        """  Init  """
def __init__(self, template_type: str, name: str):
        self.template_type = template_type
        self.name = name

    def render(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render the template with provided data"""
        raise NotImplementedError


class SlackBlockTemplate(NotificationTemplate):
    """Template for Slack Block Kit messages"""

        """  Init  """
def __init__(self, name: str, blocks_func: callable):
        super().__init__("slack_blocks", name)
        self.blocks_func = blocks_func

    def render(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render Slack blocks with data"""
        blocks = self.blocks_func(data)
        return {
            "blocks": blocks,
            "text": data.get("fallback_text", "Alert notification"),
        }


class SlackTextTemplate(NotificationTemplate):
    """Template for simple Slack text messages"""

        """  Init  """
def __init__(self, name: str, template: str):
        super().__init__("slack_text", name)
        self.template = template

    def render(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render text template with data"""
        text = self.template.format(**data)
        return {"text": text, "mrkdwn": True}


# Alert notification templates
def error_alert_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for error alerts"""
    severity = data.get("severity", "medium")
    environment = data.get("environment", "unknown")
    error_count = data.get("error_count", 1)

    # Severity mapping
    severity_config = {
        "critical": {"emoji": "🚨", "color": "#FF0000"},
        "high": {"emoji": "⚠️", "color": "#FF6600"},
        "medium": {"emoji": "⚡", "color": "#FFB347"},
        "low": {"emoji": "ℹ️", "color": "#36C5F0"},
    }

    config = severity_config.get(severity, severity_config["medium"])

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{config['emoji']} {severity.title()} Error Alert",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{data.get('title', 'Unknown Error')}*\n{data.get('description', '')}",
            },
        },
    ]

    # Add details section
    details_fields = []

    if environment:
        details_fields.append(
            {"type": "mrkdwn", "text": f"*Environment:*\n{environment}"}
        )

    if error_count > 1:
        details_fields.append(
            {"type": "mrkdwn", "text": f"*Occurrences:*\n{error_count}"}
        )

    if data.get("category"):
        details_fields.append(
            {"type": "mrkdwn", "text": f"*Category:*\n{data['category']}"}
        )

    if data.get("confidence_score"):
        details_fields.append(
            {"type": "mrkdwn", "text": f"*Confidence:*\n{data['confidence_score']:.1%}"}
        )

    if details_fields:
        blocks.append({"type": "section", "fields": details_fields})

    # Add error details if available
    if data.get("error_details"):
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Details:*\n```{data['error_details'][:500]}```",
                },
            }
        )

    # Add suggested actions
    if data.get("suggested_actions"):
        actions_text = "\n".join(
            [f"• {action}" for action in data["suggested_actions"][:3]]
        )
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Suggested Actions:*\n{actions_text}",
                },
            }
        )

    # Add action buttons if requested
    if data.get("include_actions", True):
        action_elements = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Investigate"},
                "style": "primary",
                "action_id": "investigate_alert",
                "value": json.dumps({"error_id": data.get("error_id")}),
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "✅ Acknowledge"},
                "action_id": "acknowledge_alert",
                "value": json.dumps({"error_id": data.get("error_id")}),
            },
        ]

        if severity in ["critical", "high"]:
            action_elements.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📞 Escalate"},
                    "style": "danger",
                    "action_id": "escalate_alert",
                    "value": json.dumps({"error_id": data.get("error_id")}),
                }
            )

        blocks.append({"type": "actions", "elements": action_elements})

    # Add timestamp
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Alert ID: {data.get('alert_id', 'N/A')}",
                }
            ],
        }
    )

    return blocks


def resolution_success_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for successful auto-resolution"""
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "✅ Auto-Resolution Successful"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Successfully resolved:* {data.get('error_title', 'Unknown error')}\n*Resolution:* {data.get('resolution_action', 'Unknown action')}",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Execution Time:*\n{data.get('execution_time', '0')}s",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Strategy:*\n{data.get('strategy_name', 'Unknown')}",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Actions Taken:*\n{chr(10).join([f'• {action}' for action in data.get('actions_taken', [])])}",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Resolution ID: {data.get('resolution_id', 'N/A')}",
                }
            ],
        },
    ]


def resolution_failure_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for failed auto-resolution"""
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "❌ Auto-Resolution Failed"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Failed to resolve:* {data.get('error_title', 'Unknown error')}\n*Attempted strategy:* {data.get('strategy_name', 'Unknown')}",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Failure Reason:*\n{data.get('failure_reason', 'Unknown')}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Next Steps:*\nManual intervention required",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Actions Attempted:*\n{chr(10).join([f'• {action}' for action in data.get('actions_attempted', [])])}",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔧 Manual Fix"},
                    "style": "primary",
                    "action_id": "manual_fix",
                    "value": json.dumps({"error_id": data.get("error_id")}),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📞 Escalate"},
                    "style": "danger",
                    "action_id": "escalate_failed_resolution",
                    "value": json.dumps({"error_id": data.get("error_id")}),
                },
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Resolution ID: {data.get('resolution_id', 'N/A')}",
                }
            ],
        },
    ]


def escalation_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for escalation notifications"""
    escalation_level = data.get("escalation_level", 1)

    level_config = {
        1: {"emoji": "⚠️", "title": "Alert Escalation - Team Attention Required"},
        2: {"emoji": "🚨", "title": "Critical Escalation - On-Call Required"},
        3: {"emoji": "🔥", "title": "MANAGEMENT ESCALATION - Critical System Issue"},
    }

    config = level_config.get(escalation_level, level_config[1])

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{config['emoji']} {config['title']}",
            },
        }
    ]

    # Add mentions based on escalation level
    mention_text = ""
    if escalation_level == 2:
        mention_text = "@oncall-engineer "
    elif escalation_level == 3:
        mention_text = "@management @cto "

    blocks.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{mention_text}immediate attention required\n\n*Issue:* {data.get('error_title', 'Unknown error')}\n*Environment:* {data.get('environment', 'Unknown')}\n*Escalation Reason:* {data.get('escalation_reason', 'Threshold exceeded')}",
            },
        }
    )

    # Add severity and impact information
    severity_fields = []

    if data.get("severity"):
        severity_fields.append(
            {"type": "mrkdwn", "text": f"*Severity:*\n{data['severity'].title()}"}
        )

    if data.get("business_impact"):
        severity_fields.append(
            {
                "type": "mrkdwn",
                "text": f"*Business Impact:*\n{data['business_impact'].title()}",
            }
        )

    if data.get("affected_users"):
        severity_fields.append(
            {"type": "mrkdwn", "text": f"*Affected Users:*\n{data['affected_users']}"}
        )

    if data.get("revenue_impact"):
        severity_fields.append(
            {
                "type": "mrkdwn",
                "text": f"*Revenue Impact:*\n${data['revenue_impact']}/hour",
            }
        )

    if severity_fields:
        blocks.append({"type": "section", "fields": severity_fields})

    # Add previous actions taken
    if data.get("previous_actions"):
        actions_text = "\n".join([f"• {action}" for action in data["previous_actions"]])
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Previous Actions Taken:*\n{actions_text}",
                },
            }
        )

    # Add suggested next steps
    if data.get("suggested_actions"):
        suggestions_text = "\n".join(
            [f"• {action}" for action in data["suggested_actions"]]
        )
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Suggested Next Steps:*\n{suggestions_text}",
                },
            }
        )

    # Add escalation actions
    blocks.append(
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🎯 Take Ownership"},
                    "style": "primary",
                    "action_id": "take_ownership",
                    "value": json.dumps(
                        {
                            "error_id": data.get("error_id"),
                            "escalation_level": escalation_level,
                        }
                    ),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📋 Create Incident"},
                    "action_id": "create_incident",
                    "value": json.dumps({"error_id": data.get("error_id")}),
                },
            ],
        }
    )

    # Add context
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Escalation Level: {escalation_level} | Error ID: {data.get('error_id', 'N/A')}",
                }
            ],
        }
    )

    return blocks


def metrics_report_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for metrics reports"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Alert Orchestration Metrics Report",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{data.get('report_period', 'Hourly')} metrics for automated alert handling*",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Errors Processed:*\n{data.get('errors_processed', 0)}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Alerts Sent:*\n{data.get('alerts_sent', 0)}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Auto-Resolutions:*\n{data.get('auto_resolutions_attempted', 0)}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Success Rate:*\n{data.get('resolution_success_rate', '0%')}",
                },
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Escalations:*\n{data.get('escalations_triggered', 0)}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Active Alerts:*\n{data.get('active_alerts', 0)}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Avg Resolution Time:*\n{data.get('avg_resolution_time', '0')}s",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*System Health:*\n{data.get('system_health', 'Unknown')}",
                },
            ],
        },
    ]


def system_health_blocks(data: Dict[str, Any]) -> List[Dict]:
    """Generate blocks for system health notifications"""
    health_status = data.get("health_status", "unknown")

    status_config = {
        "healthy": {"emoji": "✅", "color": "#2ecc71"},
        "warning": {"emoji": "⚠️", "color": "#f39c12"},
        "critical": {"emoji": "🚨", "color": "#e74c3c"},
        "unknown": {"emoji": "❓", "color": "#95a5a6"},
    }

    config = status_config.get(health_status, status_config["unknown"])

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{config['emoji']} System Health Report",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Overall Status:* {health_status.title()}\n*Last Check:* {data.get('last_check_time', 'Unknown')}",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Sentry Monitor:*\n{data.get('sentry_status', 'Unknown')}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Slack Integration:*\n{data.get('slack_status', 'Unknown')}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Auto-Resolver:*\n{data.get('resolver_status', 'Unknown')}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Error Analyzer:*\n{data.get('analyzer_status', 'Unknown')}",
                },
            ],
        },
    ]


# Template registry
class TemplateRegistry:
    """Registry for managing notification templates"""

        """  Init  """
def __init__(self):
        self.templates = {}
        self._register_default_templates()

        """ Register Default Templates"""
def _register_default_templates(self):
        """Register default templates"""
        # Slack block templates
        self.register_template(SlackBlockTemplate("error_alert", error_alert_blocks))
        self.register_template(
            SlackBlockTemplate("resolution_success", resolution_success_blocks)
        )
        self.register_template(
            SlackBlockTemplate("resolution_failure", resolution_failure_blocks)
        )
        self.register_template(SlackBlockTemplate("escalation", escalation_blocks))
        self.register_template(
            SlackBlockTemplate("metrics_report", metrics_report_blocks)
        )
        self.register_template(
            SlackBlockTemplate("system_health", system_health_blocks)
        )

        # Simple text templates
        self.register_template(
            SlackTextTemplate(
                "simple_error",
                "🚨 *Error Alert:* {title}\n*Environment:* {environment}\n*Count:* {error_count}",
            )
        )

        self.register_template(
            SlackTextTemplate(
                "simple_resolution",
                "✅ *Resolved:* {error_title}\n*Action:* {resolution_action}\n*Time:* {execution_time}s",
            )
        )

        self.register_template(
            SlackTextTemplate(
                "simple_escalation",
                "📞 *ESCALATION:* {error_title}\n*Level:* {escalation_level}\n*Reason:* {escalation_reason}",
            )
        )

        """Register Template"""
def register_template(self, template: NotificationTemplate):
        """Register a notification template"""
        self.templates[template.name] = template

    def get_template(self, name: str) -> Optional[NotificationTemplate]:
        """Get a template by name"""
        return self.templates.get(name)

    def render_template(
        self, name: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Render a template with data"""
        template = self.get_template(name)
        if template:
            return template.render(data)
        return None

    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())


# Global template registry
template_registry = TemplateRegistry()


# Convenience functions
def render_notification(
    template_name: str, data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Render a notification using the specified template"""
    return template_registry.render_template(template_name, data)


    """Register Custom Template"""
def register_custom_template(template: NotificationTemplate):
    """Register a custom notification template"""
    template_registry.register_template(template)


def get_available_templates() -> List[str]:
    """Get list of available notification templates"""
    return template_registry.list_templates()


# Template data builders
def build_error_alert_data(error, classification, context=None) -> Dict[str, Any]:
    """Build data dictionary for error alert template"""
    return {
        "alert_id": error.id,
        "error_id": error.id,
        "title": error.title,
        "description": error.message,
        "error_details": error.message,
        "severity": "critical" if error.is_critical else "medium",
        "environment": error.environment,
        "error_count": error.count,
        "category": classification.primary_category if classification else "unknown",
        "confidence_score": classification.confidence_score if classification else 0.0,
        "suggested_actions": classification.suggested_actions if classification else [],
        "fallback_text": f"Error Alert: {error.title}",
        **(context or {}),
    }


def build_resolution_data(error, result, strategy_name) -> Dict[str, Any]:
    """Build data dictionary for resolution notification template"""
    return {
        "resolution_id": f"res_{error.id}_{int(datetime.now().timestamp())}",
        "error_id": error.id,
        "error_title": error.title,
        "resolution_action": strategy_name,
        "strategy_name": strategy_name,
        "execution_time": result.execution_time if result else 0,
        "actions_taken": result.actions_taken if result else [],
        "failure_reason": (
            result.error_message if result and not result.success else None
        ),
        "actions_attempted": (
            result.actions_taken if result and not result.success else []
        ),
        "fallback_text": f"Resolution {'successful' if result and result.success else 'failed'}: {error.title}",
    }


def build_escalation_data(
    error, classification, escalation_level, reason, context=None
) -> Dict[str, Any]:
    """Build data dictionary for escalation notification template"""
    return {
        "error_id": error.id,
        "error_title": error.title,
        "escalation_level": escalation_level,
        "escalation_reason": reason,
        "environment": error.environment,
        "severity": "critical" if error.is_critical else "high",
        "business_impact": (
            classification.business_impact if classification else "unknown"
        ),
        "suggested_actions": classification.suggested_actions if classification else [],
        "previous_actions": [],  # To be filled by caller
        "affected_users": context.get("affected_users") if context else None,
        "revenue_impact": context.get("revenue_impact") if context else None,
        "fallback_text": f"Escalation Level {escalation_level}: {error.title}",
        **(context or {}),
    }
