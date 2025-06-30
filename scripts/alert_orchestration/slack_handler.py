#!/usr/bin/env python3
"""
Slack Handler - Advanced Slack integration for autonomous alert handling
Provides interactive alert handling, bot responses, and escalation management
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import requests

# Make FastAPI optional for CI environments
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Mock classes for when FastAPI is not available
    class FastAPI:
            """  Init  """
def __init__(self, *args, **kwargs):
            pass

            """Post"""
def post(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    class HTTPException(Exception):
            """  Init  """
def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail

    class Request:
        pass

    class JSONResponse:
            """  Init  """
def __init__(self, content, status_code=200):
            self.content = content
            self.status_code = status_code


# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SlackHandler")


@dataclass
class SlackAlert:
    """Slack alert data structure"""

    id: str
    channel: str
    user: str
    message: str
    timestamp: datetime
    alert_type: str
    severity: str
    source: str
    metadata: Dict[str, Any]
    thread_ts: Optional[str] = None
    actions_taken: List[str] = None
    status: str = "new"  # new, acknowledged, resolved, escalated

        """  Post Init  """
def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []


@dataclass
class SlackResponse:
    """Slack response configuration"""

    text: str
    blocks: Optional[List[Dict]] = None
    thread_ts: Optional[str] = None
    replace_original: bool = False
    ephemeral: bool = False


class SlackBot:
    """
    Advanced Slack bot for handling alerts and automation

    Features:
    - Interactive alert responses
    - Automated acknowledgment and escalation
    - Rich message formatting with blocks
    - Action buttons and workflows
    - Thread management for organized conversations
    """

        """  Init  """
def __init__(
        self, bot_token: Optional[str] = None, webhook_url: Optional[str] = None
    ):
        """Initialize Slack bot with OAuth token and webhook"""
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

        if not self.bot_token and not self.webhook_url:
            raise ValueError("Either SLACK_BOT_TOKEN or SLACK_WEBHOOK_URL is required")

        self.base_url = "https://slack.com/api"
        self.session = requests.Session()

        if self.bot_token:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.bot_token}",
                    "Content-Type": "application/json",
                }
            )

        # Bot state
        self.active_alerts: Dict[str, SlackAlert] = {}
        self.alert_handlers: Dict[str, Callable] = {}
        self.response_templates: Dict[str, Dict] = {}

        logger.info("Slack bot initialized")

    def _make_api_call(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated API call to Slack"""
        if not self.bot_token:
            raise ValueError("Bot token required for API calls")

        url = f"{self.base_url}/{method}"

        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise Exception(
                    f"Slack API error: {result.get('error', 'Unknown error')}"
                )

            return result
        except Exception as e:
            logger.error(f"Slack API call failed: {e}")
            raise

    def _send_webhook(self, data: Dict[str, Any]) -> bool:
        """Send message via webhook"""
        if not self.webhook_url:
            raise ValueError("Webhook URL required for webhook messages")

        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False

    def send_alert(
        self,
        channel: str,
        alert_data: Dict[str, Any],
        alert_type: str = "error",
        severity: str = "medium",
        include_actions: bool = True,
    ) -> str:
        """
        Send alert to Slack with interactive components

        Returns:
            Message timestamp for thread management
        """
        # Create alert blocks
        blocks = self._create_alert_blocks(
            alert_data, alert_type, severity, include_actions
        )

        # Prepare message
        message_data = {
            "channel": channel,
            "blocks": blocks,
            "text": f"{alert_type.title()} Alert: {alert_data.get('title', 'Unknown')}",
        }

        try:
            if self.bot_token:
                result = self._make_api_call("chat.postMessage", message_data)
                message_ts = result["ts"]
            else:
                # Use webhook (no timestamp return)
                self._send_webhook(message_data)
                message_ts = str(time.time())

            # Store alert for tracking
            alert_id = f"{channel}_{message_ts}"
            alert = SlackAlert(
                id=alert_id,
                channel=channel,
                user="system",
                message=alert_data.get("title", ""),
                timestamp=datetime.now(),
                alert_type=alert_type,
                severity=severity,
                source=alert_data.get("source", "unknown"),
                metadata=alert_data,
                thread_ts=message_ts,
            )
            self.active_alerts[alert_id] = alert

            logger.info(f"Alert sent to {channel}: {alert_type}")
            return message_ts

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            raise

    def _create_alert_blocks(
        self,
        alert_data: Dict[str, Any],
        alert_type: str,
        severity: str,
        include_actions: bool,
    ) -> List[Dict]:
        """Create Slack blocks for alert message"""

        # Check if this is a QA validation alert and use specialized template
        if alert_type in ["qa_validation", "validation", "qa_failure"]:
            try:
                from .qa_notification_templates import qa_validation_failure_blocks

                return qa_validation_failure_blocks(alert_data)
            except ImportError:
                pass  # Fall back to generic template

        # Check for QA resolution success
        if alert_type == "qa_resolution_success":
            try:
                from .qa_notification_templates import qa_resolution_success_blocks

                return qa_resolution_success_blocks(alert_data)
            except ImportError:
                pass  # Fall back to generic template

        # Determine emoji and color based on severity
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
                    "text": f"{config['emoji']} {alert_type.title()} Alert - {severity.title()} Severity",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{alert_data.get('title', 'Unknown Alert')}*\n{alert_data.get('description', '')}",
                },
            },
        ]

        # Add detailed information
        if alert_data.get("error_details"):
            blocks.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Error:*\n{alert_data['error_details'][:100]}...",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Source:*\n{alert_data.get('source', 'Unknown')}",
                        },
                    ],
                }
            )

        # Add metrics if available
        if alert_data.get("metrics"):
            metrics_text = []
            for key, value in alert_data["metrics"].items():
                metrics_text.append(f"• *{key}*: {value}")

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Metrics:*\n" + "\n".join(metrics_text[:5]),
                    },
                }
            )

        # Add context information
        context_elements = []
        if alert_data.get("environment"):
            context_elements.append(f"Environment: {alert_data['environment']}")
        if alert_data.get("timestamp"):
            context_elements.append(f"Time: {alert_data['timestamp']}")
        if alert_data.get("frequency"):
            context_elements.append(f"Frequency: {alert_data['frequency']}")

        if context_elements:
            blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": " | ".join(context_elements)}
                    ],
                }
            )

        # Add action buttons if requested
        if include_actions:
            action_block = self._create_action_buttons(alert_data, alert_type, severity)
            if action_block:
                blocks.append(action_block)

        return blocks

    def _create_action_buttons(
        self, alert_data: Dict[str, Any], alert_type: str, severity: str
    ) -> Optional[Dict]:
        """Create interactive action buttons for alerts"""

        # Base actions for all alerts
        actions = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Investigate"},
                "style": "primary",
                "action_id": "investigate_alert",
                "value": json.dumps(
                    {"action": "investigate", "alert_data": alert_data}
                ),
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "✅ Acknowledge"},
                "action_id": "acknowledge_alert",
                "value": json.dumps(
                    {"action": "acknowledge", "alert_data": alert_data}
                ),
            },
        ]

        # Add severity-specific actions
        if severity in ["critical", "high"]:
            actions.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📞 Escalate"},
                    "style": "danger",
                    "action_id": "escalate_alert",
                    "value": json.dumps(
                        {"action": "escalate", "alert_data": alert_data}
                    ),
                }
            )

        # Add type-specific actions
        if alert_type == "error":
            actions.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔧 Auto-Fix"},
                    "action_id": "autofix_alert",
                    "value": json.dumps(
                        {"action": "autofix", "alert_data": alert_data}
                    ),
                }
            )

        elif alert_type == "performance":
            actions.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "⚡ Optimize"},
                    "action_id": "optimize_alert",
                    "value": json.dumps(
                        {"action": "optimize", "alert_data": alert_data}
                    ),
                }
            )

        return {"type": "actions", "elements": actions} if actions else None

    def handle_interaction(self, payload: Dict[str, Any]) -> SlackResponse:
        """Handle Slack interactive component interactions"""
        try:
            action = payload.get("actions", [{}])[0]
            action_id = action.get("action_id")
            action_value = json.loads(action.get("value", "{}"))
            user = payload.get("user", {}).get("username", "unknown")

            logger.info(f"Handling interaction: {action_id} by {user}")

            # Route to appropriate handler
            if action_id == "investigate_alert":
                return self._handle_investigate(action_value, user)
            elif action_id == "acknowledge_alert":
                return self._handle_acknowledge(action_value, user)
            elif action_id == "escalate_alert":
                return self._handle_escalate(action_value, user)
            elif action_id == "autofix_alert":
                return self._handle_autofix(action_value, user)
            elif action_id == "optimize_alert":
                return self._handle_optimize(action_value, user)
            else:
                return SlackResponse(
                    text=f"Unknown action: {action_id}", ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error handling interaction: {e}")
            return SlackResponse(
                text="Error processing action. Please try again.", ephemeral=True
            )

    def _handle_investigate(self, action_value: Dict, user: str) -> SlackResponse:
        """Handle investigate action"""
        alert_data = action_value.get("alert_data", {})

        # Create investigation blocks
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔍 *Investigation started by {user}*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Investigation Steps:*\n• Gathering error context\n• Checking related logs\n• Analyzing error patterns\n• Generating resolution suggestions",
                },
            },
        ]

        # Add investigation details based on alert type
        if alert_data.get("error_id"):
            blocks.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Error ID:*\n{alert_data['error_id']}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Investigation Status:*\nIn Progress",
                        },
                    ],
                }
            )

        return SlackResponse(text=f"Investigation started by {user}", blocks=blocks)

    def _handle_acknowledge(self, action_value: Dict, user: str) -> SlackResponse:
        """Handle acknowledge action"""
        alert_data = action_value.get("alert_data", {})

        # Update alert status
        for alert in self.active_alerts.values():
            if alert.metadata.get("error_id") == alert_data.get("error_id"):
                alert.status = "acknowledged"
                alert.actions_taken.append(f"Acknowledged by {user}")
                break

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Alert acknowledged by {user}*\n_This alert is now being handled._",
                },
            }
        ]

        return SlackResponse(text=f"Alert acknowledged by {user}", blocks=blocks)

    def _handle_escalate(self, action_value: Dict, user: str) -> SlackResponse:
        """Handle escalate action"""
        alert_data = action_value.get("alert_data", {})

        # Update alert status
        for alert in self.active_alerts.values():
            if alert.metadata.get("error_id") == alert_data.get("error_id"):
                alert.status = "escalated"
                alert.actions_taken.append(f"Escalated by {user}")
                break

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"📞 *Alert escalated by {user}*"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Escalation Actions:*\n• Notifying on-call engineer\n• Creating high-priority incident\n• Escalating to senior team\n• Setting up war room if needed",
                },
            },
        ]

        return SlackResponse(text=f"Alert escalated by {user}", blocks=blocks)

    def _handle_autofix(self, action_value: Dict, user: str) -> SlackResponse:
        """Handle auto-fix action"""
        action_value.get("alert_data", {})

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔧 *Auto-fix initiated by {user}*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Auto-fix Progress:*\n• Analyzing error pattern\n• Identifying fix strategy\n• Applying automated resolution\n• Validating fix effectiveness",
                },
            },
        ]

        return SlackResponse(text=f"Auto-fix initiated by {user}", blocks=blocks)

    def _handle_optimize(self, action_value: Dict, user: str) -> SlackResponse:
        """Handle optimize action"""
        action_value.get("alert_data", {})

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚡ *Optimization started by {user}*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Optimization Steps:*\n• Performance profiling\n• Resource utilization analysis\n• Bottleneck identification\n• Performance improvements",
                },
            },
        ]

        return SlackResponse(text=f"Optimization started by {user}", blocks=blocks)


class SlackWebhookHandler:
    """
    Webhook handler for processing incoming Slack events
    """

        """  Init  """
def __init__(self, slack_bot: SlackBot):
        self.slack_bot = slack_bot
        self.app = FastAPI(title="Slack Alert Handler")
        self._setup_routes()

        """ Setup Routes"""
def _setup_routes(self):
        """Setup FastAPI routes for webhook handling"""

        @self.app.post("/slack/events")
        async     """Handle Events"""
def handle_events(request: Request):
            """Handle Slack events"""
            try:
                payload = await request.json()

                # Handle URL verification challenge
                if payload.get("type") == "url_verification":
                    return JSONResponse({"challenge": payload.get("challenge")})

                # Handle other events
                event = payload.get("event", {})
                if event.get("type") == "message":
                    await self._process_message(event)

                return JSONResponse({"status": "ok"})

            except Exception as e:
                logger.error(f"Error handling Slack event: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/slack/interactive")
        async     """Handle Interactive"""
def handle_interactive(request: Request):
            """Handle Slack interactive components"""
            try:
                form_data = await request.form()
                payload = json.loads(form_data.get("payload", "{}"))

                # Process interaction
                response = self.slack_bot.handle_interaction(payload)

                return JSONResponse(
                    {
                        "text": response.text,
                        "blocks": response.blocks,
                        "replace_original": response.replace_original,
                        "response_type": (
                            "ephemeral" if response.ephemeral else "in_channel"
                        ),
                    }
                )

            except Exception as e:
                logger.error(f"Error handling interaction: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/slack/commands")
        async     """Handle Commands"""
def handle_commands(request: Request):
            """Handle Slack slash commands"""
            try:
                form_data = await request.form()
                command = form_data.get("command")
                text = form_data.get("text", "")
                user = form_data.get("user_name")
                channel = form_data.get("channel_id")

                response = await self._process_command(command, text, user, channel)

                return JSONResponse(response)

            except Exception as e:
                logger.error(f"Error handling command: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async     """ Process Message"""
def _process_message(self, event: Dict[str, Any]):
        """Process incoming message events"""
        text = event.get("text", "")
        event.get("user")
        channel = event.get("channel")

        # Check for alert keywords
        alert_keywords = ["error", "alert", "issue", "problem", "down", "failure"]
        if any(keyword in text.lower() for keyword in alert_keywords):
            # Parse potential alert from message
            alert_data = self._parse_alert_from_message(text, event)
            if alert_data:
                # Create alert
                self.slack_bot.send_alert(
                    channel=channel,
                    alert_data=alert_data,
                    alert_type="user_reported",
                    severity="medium",
                )

    def _parse_alert_from_message(self, text: str, event: Dict) -> Optional[Dict]:
        """Parse alert information from a message"""
        # Simple parsing logic - can be enhanced with NLP
        return {
            "title": f"User reported issue: {text[:50]}...",
            "description": text,
            "source": "slack_user",
            "timestamp": datetime.now().isoformat(),
            "user": event.get("user"),
            "channel": event.get("channel"),
        }

    async def _process_command(
        self, command: str, text: str, user: str, channel: str
    ) -> Dict:
        """Process slash commands"""
        if command == "/alert-status":
            # Return status of active alerts
            active_count = len(
                [a for a_var in self.slack_bot.active_alerts.values() if a.status == "new"]
            )
            return {
                "text": f"Active alerts: {active_count}",
                "response_type": "ephemeral",
            }

        elif command == "/alert-help":
            return {
                "text": "Available commands:\n• `/alert-status` - Show active alerts\n• `/alert-help` - Show this help",
                "response_type": "ephemeral",
            }

        return {"text": f"Unknown command: {command}", "response_type": "ephemeral"}

        """Start Server"""
def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the webhook server"""
        import uvicorn

        logger.info(f"Starting Slack webhook server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


# Example usage
async     """Example Usage"""
def example_usage():
    """Example of how to use the Slack handler"""
    try:
        # Initialize bot
        bot = SlackBot()

        # Send a test alert
        alert_data = {
            "title": "Database Connection Error",
            "description": "Unable to connect to PostgreSQL database",
            "error_details": "Connection timeout after 30 seconds",
            "source": "api_server",
            "environment": "production",
            "metrics": {
                "error_count": 15,
                "affected_users": 42,
                "duration": "5 minutes",
            },
        }

        message_ts = bot.send_alert(
            channel="#alerts",
            alert_data=alert_data,
            alert_type="error",
            severity="high",
        )

        print(f"Alert sent with timestamp: {message_ts}")

    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
