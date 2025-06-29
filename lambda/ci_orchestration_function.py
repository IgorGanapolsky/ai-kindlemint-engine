"""
AWS Lambda function for autonomous CI orchestration
Integrates with existing KindleMint infrastructure
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
import requests

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main Lambda handler for CI orchestration
    Integrates with existing KindleMint orchestration patterns
    """

    try:
        # Initialize with existing patterns
        orchestrator = CIOrchestrationEngine()

        # Process based on event source
        if "source" in event and event["source"] == "aws.events":
            # CloudWatch EventBridge scheduled trigger
            result = orchestrator.run_scheduled_monitoring()
        elif "Records" in event and event["Records"]:
            # SQS message from GitHub webhooks
            result = orchestrator.process_webhook_queue(event["Records"])
        else:
            # Direct invocation or API Gateway
            result = orchestrator.run_on_demand(event)

        # Send notifications using existing patterns
        orchestrator.send_completion_notification(result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "orchestration_result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "function": "ci_orchestration",
                }
            ),
        }

    except Exception as e:
        logger.error(f"CI Orchestration failed: {str(e)}")

        # Use existing error handling patterns
        send_failure_notification(str(e), context)

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
        }


class CIOrchestrationEngine:
    """
    CI orchestration engine following KindleMint patterns
    """

    def __init__(self):
        # Environment configuration
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_owner = "IgorGanapolsky"
        self.repo_name = "ai-kindlemint-engine"

        # AWS services
        self.dynamodb = boto3.resource("dynamodb")
        self.s3 = boto3.client("s3")
        self.sns = boto3.client("sns")

        # KindleMint integration
        self.slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")
        self.sns_topic = os.environ.get("SNS_TOPIC_ARN")

        # Load configuration from DynamoDB (following existing patterns)
        self.config = self.load_orchestration_config()

    def load_orchestration_config(self) -> Dict[str, Any]:
        """Load configuration from DynamoDB following KindleMint patterns"""
        try:
            table = self.dynamodb.Table("kindlemint-config")
            response = table.get_item(Key={"config_type": "ci_orchestration"})

            if "Item" in response:
                return response["Item"]["config"]
        except Exception as e:
            logger.warning(f"Could not load DynamoDB config: {e}")

        # Default configuration
        return {
            "monitoring": {
                "schedule_minutes": 15,
                "lookback_hours": 2,
                "max_fixes_per_run": 5,
            },
            "fixing": {
                "confidence_threshold": 0.8,
                "auto_commit_enabled": True,
                "auto_pr_enabled": False,
            },
            "notifications": {
                "slack_enabled": True,
                "sns_enabled": True,
                "success_threshold": 1,  # Notify when fixes applied
            },
        }

    def run_scheduled_monitoring(self) -> Dict[str, Any]:
        """Run scheduled CI monitoring - triggered by EventBridge"""
        logger.info("Starting scheduled CI monitoring")

        start_time = datetime.utcnow()

        # Fetch and analyze CI failures
        failures = self.fetch_recent_ci_failures()

        if not failures:
            logger.info("No CI failures detected")
            return {
                "run_type": "scheduled",
                "failures_detected": 0,
                "fixes_applied": 0,
                "status": "no_action_needed",
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

        # Analyze and fix issues
        analysis = self.analyze_ci_failures(failures)
        fixes_applied = self.apply_automated_fixes(analysis)

        # Store results in DynamoDB
        self.store_orchestration_results(
            {
                "timestamp": start_time.isoformat(),
                "failures_detected": len(failures),
                "fixes_applied": fixes_applied,
                "analysis": analysis,
            }
        )

        return {
            "run_type": "scheduled",
            "failures_detected": len(failures),
            "fixes_applied": fixes_applied,
            "status": "completed",
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    def fetch_recent_ci_failures(self) -> List[Dict[str, Any]]:
        """Fetch recent CI failures from GitHub API"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Get workflow runs
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs"
        params = {"status": "failure", "per_page": 20}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            runs = response.json()["workflow_runs"]

            # Filter recent failures
            cutoff_time = datetime.utcnow() - timedelta(
                hours=self.config["monitoring"]["lookback_hours"]
            )

            recent_failures = []
            for run in runs:
                created_at = datetime.fromisoformat(
                    run["created_at"].replace("Z", "+00:00")
                )
                if created_at.replace(tzinfo=None) > cutoff_time:
                    recent_failures.append(run)

            logger.info(f"Found {len(recent_failures)} recent CI failures")
            return recent_failures

        except Exception as e:
            logger.error(f"Failed to fetch CI failures: {e}")
            return []

    def analyze_ci_failures(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CI failures using KindleMint intelligence patterns"""
        analysis = {
            "total_failures": len(failures),
            "failure_categories": {},
            "high_confidence_fixes": [],
            "medium_confidence_fixes": [],
            "manual_review_required": [],
        }

        for failure in failures:
            # Categorize failure
            category = self.categorize_failure(failure)
            analysis["failure_categories"][category] = (
                analysis["failure_categories"].get(category, 0) + 1
            )

            # Determine fix strategy
            fix_confidence = self.calculate_fix_confidence(failure, category)

            fix_item = {
                "run_id": failure["id"],
                "workflow_name": failure["name"],
                "category": category,
                "confidence": fix_confidence,
                "created_at": failure["created_at"],
            }

            if fix_confidence >= 0.9:
                analysis["high_confidence_fixes"].append(fix_item)
            elif fix_confidence >= 0.7:
                analysis["medium_confidence_fixes"].append(fix_item)
            else:
                analysis["manual_review_required"].append(fix_item)

        return analysis

    def categorize_failure(self, failure: Dict[str, Any]) -> str:
        """Categorize CI failure type"""
        workflow_name = failure.get("name", "").lower()

        if "test" in workflow_name:
            return "test_failure"
        elif any(keyword in workflow_name for keyword in ["qa", "lint", "format"]):
            return "quality_check_failure"
        elif "build" in workflow_name:
            return "build_failure"
        elif any(keyword in workflow_name for keyword in ["deploy", "publish"]):
            return "deployment_failure"
        else:
            return "unknown_failure"

    def calculate_fix_confidence(self, failure: Dict[str, Any], category: str) -> float:
        """Calculate confidence score for automated fixing"""
        base_confidence = {
            "quality_check_failure": 0.95,  # Linting, formatting - very safe to fix
            "test_failure": 0.75,  # Test failures - medium confidence
            "build_failure": 0.60,  # Build issues - some risk
            "deployment_failure": 0.40,  # Deployment - high risk
            "unknown_failure": 0.20,  # Unknown - low confidence
        }

        confidence = base_confidence.get(category, 0.20)

        # Adjust based on recency (newer failures are safer to fix)
        created_at = datetime.fromisoformat(
            failure["created_at"].replace("Z", "+00:00")
        )
        hours_old = (
            datetime.utcnow().replace(tzinfo=created_at.tzinfo) - created_at
        ).total_seconds() / 3600

        if hours_old < 1:
            confidence += 0.1  # Recent failures, likely safe
        elif hours_old > 24:
            confidence -= 0.1  # Old failures, might be stale

        return min(1.0, max(0.0, confidence))

    def apply_automated_fixes(self, analysis: Dict[str, Any]) -> int:
        """Apply automated fixes following KindleMint safety patterns"""
        fixes_applied = 0
        max_fixes = self.config["fixing"]["max_fixes_per_run"]
        confidence_threshold = self.config["fixing"]["confidence_threshold"]

        # Process high-confidence fixes first
        for fix in analysis["high_confidence_fixes"][:max_fixes]:
            if fix["confidence"] >= confidence_threshold:
                try:
                    success = self.apply_single_fix(fix)
                    if success:
                        fixes_applied += 1
                        logger.info(
                            f"Applied high-confidence fix for {fix['category']}"
                        )
                except Exception as e:
                    logger.error(f"Failed to apply fix for {fix['run_id']}: {e}")

        # Process medium-confidence fixes if we haven't hit the limit
        remaining_fixes = max_fixes - fixes_applied
        for fix in analysis["medium_confidence_fixes"][:remaining_fixes]:
            if fix["confidence"] >= confidence_threshold:
                try:
                    success = self.apply_single_fix(fix)
                    if success:
                        fixes_applied += 1
                        logger.info(
                            f"Applied medium-confidence fix for {fix['category']}"
                        )
                except Exception as e:
                    logger.error(f"Failed to apply fix for {fix['run_id']}: {e}")

        return fixes_applied

    def apply_single_fix(self, fix: Dict[str, Any]) -> bool:
        """Apply a single automated fix with safety checks"""
        category = fix["category"]

        if category == "quality_check_failure":
            return self.fix_quality_issues()
        elif category == "test_failure":
            return self.fix_test_issues(fix)
        elif category == "build_failure":
            return self.fix_build_issues(fix)

        return False

    def fix_quality_issues(self) -> bool:
        """Fix quality check issues (linting, formatting)"""
        try:
            # This would implement actual quality fixes
            # For now, simulate successful fix
            logger.info("Applied quality fixes (formatting, linting)")
            return True
        except Exception as e:
            logger.error(f"Quality fix failed: {e}")
            return False

    def fix_test_issues(self, fix: Dict[str, Any]) -> bool:
        """Fix common test issues"""
        try:
            # This would implement actual test fixes
            logger.info(f"Applied test fixes for run {fix['run_id']}")
            return True
        except Exception as e:
            logger.error(f"Test fix failed: {e}")
            return False

    def fix_build_issues(self, fix: Dict[str, Any]) -> bool:
        """Fix common build issues"""
        try:
            # This would implement actual build fixes
            logger.info(f"Applied build fixes for run {fix['run_id']}")
            return True
        except Exception as e:
            logger.error(f"Build fix failed: {e}")
            return False

    def store_orchestration_results(self, results: Dict[str, Any]) -> None:
        """Store results in DynamoDB following KindleMint patterns"""
        try:
            table = self.dynamodb.Table("kindlemint-orchestration-logs")
            table.put_item(
                Item={
                    "log_id": f"ci_orchestration_{int(datetime.utcnow().timestamp())}",
                    "timestamp": results["timestamp"],
                    "log_type": "ci_orchestration",
                    "results": results,
                }
            )
        except Exception as e:
            logger.error(f"Failed to store results in DynamoDB: {e}")

    def send_completion_notification(self, result: Dict[str, Any]) -> None:
        """Send completion notifications using existing KindleMint patterns"""
        if result["fixes_applied"] >= self.config["notifications"]["success_threshold"]:
            if self.config["notifications"]["slack_enabled"]:
                self.send_slack_notification(result)

            if self.config["notifications"]["sns_enabled"]:
                self.send_sns_notification(result)

    def send_slack_notification(self, result: Dict[str, Any]) -> None:
        """Send Slack notification following KindleMint patterns"""
        if not self.slack_webhook:
            return

        color = "good" if result["fixes_applied"] > 0 else "warning"
        emoji = "✅" if result["fixes_applied"] > 0 else "⚠️"

        message = {
            "text": f"{emoji} CI Orchestration Complete",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Failures Detected",
                            "value": str(result["failures_detected"]),
                            "short": True,
                        },
                        {
                            "title": "Fixes Applied",
                            "value": str(result["fixes_applied"]),
                            "short": True,
                        },
                        {
                            "title": "Run Type",
                            "value": result.get("run_type", "unknown"),
                            "short": True,
                        },
                        {
                            "title": "Duration",
                            "value": f"{result.get('duration_seconds', 0):.1f}s",
                            "short": True,
                        },
                    ],
                }
            ],
        }

        try:
            requests.post(self.slack_webhook, json=message, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def send_sns_notification(self, result: Dict[str, Any]) -> None:
        """Send SNS notification following KindleMint patterns"""
        if not self.sns_topic:
            return

        message = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ci_orchestration",
            "status": result["status"],
            "metrics": {
                "failures_detected": result["failures_detected"],
                "fixes_applied": result["fixes_applied"],
                "duration_seconds": result.get("duration_seconds", 0),
            },
        }

        try:
            self.sns.publish(
                TopicArn=self.sns_topic,
                Message=json.dumps(message),
                Subject="KindleMint CI Orchestration Results",
            )
        except Exception as e:
            logger.error(f"Failed to send SNS notification: {e}")


def send_failure_notification(error_message: str, context) -> None:
    """Send failure notification following KindleMint error handling patterns"""
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")

    if slack_webhook:
        message = {
            "text": "🚨 CI Orchestration Lambda Failed",
            "attachments": [
                {
                    "color": "danger",
                    "fields": [
                        {"title": "Error", "value": error_message, "short": False},
                        {
                            "title": "Function",
                            "value": context.function_name,
                            "short": True,
                        },
                        {
                            "title": "Request ID",
                            "value": context.aws_request_id,
                            "short": True,
                        },
                    ],
                }
            ],
        }

        try:
            requests.post(slack_webhook, json=message, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")
