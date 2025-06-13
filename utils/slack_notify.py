"""Lightweight helper to send Slack notifications via incoming webhook.
Avoids external dependencies by using the stdlib only.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error

logger = logging.getLogger("SlackNotify")


def notify_slack(message: str) -> None:
    """Post a simple text message to Slack.

    The webhook URL is expected in the SLACK_WEBHOOK_URL environment variable.
    If it is missing or the request fails, we log a warning but do not raise.
    """
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        logger.debug("SLACK_WEBHOOK_URL not set; skipping Slack notification")
        return

    payload = json.dumps({"text": message}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                logger.warning("Slack notification returned status %s", resp.status)
    except urllib.error.URLError as exc:
        logger.warning("Failed to send Slack notification: %s", exc)
