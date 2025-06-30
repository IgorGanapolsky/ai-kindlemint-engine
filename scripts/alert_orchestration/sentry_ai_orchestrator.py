#!/usr/bin/env python3
"""
Sentry AI Orchestrator - Integrates Sentry AI capabilities into the orchestration system
Automatically triggers test generation and code reviews for quality assurance
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from github import Github
from sentry_sdk import capture_exception, capture_message

logger = logging.getLogger("SentryAIOrchestrator")


class SentryAIOrchestrator:
    """Orchestrates Sentry AI operations for automated code quality"""

        """  Init  """
def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.github_token) if self.github_token else None
        self.repo_name = self._get_repo_name()

    def _get_repo_name(self) -> Optional[str]:
        """Get the current repository name from git"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"], capture_output=True, text=True
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract owner/repo from URL
                if "github.com" in url:
                    parts = url.split("github.com")[-1].strip("/:").split("/")
                    if len(parts) >= 2:
                        return f"{parts[0]}/{parts[1].replace('.git', '')}"
        except Exception as e:
            logger.error(f"Failed to get repo name: {e}")
        return None

    async def check_pr_status(self, pr_number: int) -> Dict[str, Any]:
        """Check if a PR has been reviewed by Sentry AI"""
        if not self.github or not self.repo_name:
            return {"error": "GitHub not configured"}

        try:
            repo = self.github.get_repo(self.repo_name)
            pr = repo.get_pull(pr_number)

            # Check labels
            labels = [label.name for label in pr.labels]
            has_review = "sentry-ai-reviewed" in labels
            is_processing = "sentry-ai-processing" in labels

            # Check comments for Sentry responses
            comments = pr.get_issue_comments()
            sentry_comments = []

            for comment in comments:
                if (
                    comment.user.type == "Bot"
                    and "sentry" in comment.user.login.lower()
                ):
                    sentry_comments.append(
                        {
                            "created_at": comment.created_at.isoformat(),
                            "body_preview": (
                                comment.body[:200] + "..."
                                if len(comment.body) > 200
                                else comment.body
                            ),
                        }
                    )

            return {
                "pr_number": pr_number,
                "title": pr.title,
                "has_sentry_review": has_review,
                "is_processing": is_processing,
                "sentry_comments_count": len(sentry_comments),
                "latest_sentry_comment": (
                    sentry_comments[0] if sentry_comments else None
                ),
                "labels": labels,
            }

        except Exception as e:
            logger.error(f"Failed to check PR status: {e}")
            return {"error": str(e)}

    async def trigger_sentry_ai(
        self, pr_number: int, command: str = "both"
    ) -> Dict[str, Any]:
        """Manually trigger Sentry AI commands on a PR"""
        if not self.github or not self.repo_name:
            return {"error": "GitHub not configured"}

        try:
            repo = self.github.get_repo(self.repo_name)
            pr = repo.get_pull(pr_number)

            results = {"pr_number": pr_number, "commands_triggered": []}

            # Trigger review
            if command in ["review", "both"]:
                pr.create_issue_comment("@sentry review")
                results["commands_triggered"].append("review")
                await asyncio.sleep(2)  # Small delay between commands

            # Trigger test generation
            if command in ["test", "both"]:
                pr.create_issue_comment("@sentry generate-test")
                results["commands_triggered"].append("generate-test")

            # Add processing label
            pr.add_to_labels("sentry-ai-processing")

            # Log to Sentry
            capture_message(
                f"Triggered Sentry AI on PR #{pr_number}",
                level="info",
                tags={"pr_number": pr_number, "commands": command},
            )

            return results

        except Exception as e:
            logger.error(f"Failed to trigger Sentry AI: {e}")
            capture_exception(e)
            return {"error": str(e)}

    async def analyze_sentry_feedback(self, pr_number: int) -> Dict[str, Any]:
        """Analyze Sentry AI feedback on a PR"""
        if not self.github or not self.repo_name:
            return {"error": "GitHub not configured"}

        try:
            repo = self.github.get_repo(self.repo_name)
            pr = repo.get_pull(pr_number)

            analysis = {
                "pr_number": pr_number,
                "issues_found": 0,
                "tests_generated": 0,
                "suggestions": [],
                "critical_issues": [],
            }

            # Get all comments
            comments = pr.get_issue_comments()

            for comment in comments:
                if (
                    comment.user.type == "Bot"
                    and "sentry" in comment.user.login.lower()
                ):
                    body_lower = comment.body.lower()

                    # Analyze review comments
                    if (
                        "issue" in body_lower
                        or "error" in body_lower
                        or "bug" in body_lower
                    ):
                        analysis["issues_found"] += (
                            body_lower.count("issue")
                            + body_lower.count("error")
                            + body_lower.count("bug")
                        )

                    # Check for generated tests
                    if "test" in body_lower and "generated" in body_lower:
                        analysis["tests_generated"] += 1

                    # Extract critical issues
                    if (
                        "critical" in body_lower
                        or "security" in body_lower
                        or "vulnerability" in body_lower
                    ):
                        analysis["critical_issues"].append(
                            {
                                "timestamp": comment.created_at.isoformat(),
                                "preview": comment.body[:200],
                            }
                        )

                    # Extract suggestions
                    if "suggest" in body_lower or "recommend" in body_lower:
                        analysis["suggestions"].append(
                            {
                                "timestamp": comment.created_at.isoformat(),
                                "preview": comment.body[:200],
                            }
                        )

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze Sentry feedback: {e}")
            return {"error": str(e)}

    async def orchestrate_pr_quality_check(self, pr_number: int) -> Dict[str, Any]:
        """Full orchestration of PR quality check with Sentry AI"""
        logger.info(f"Starting quality check orchestration for PR #{pr_number}")

        orchestration_result = {
            "pr_number": pr_number,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
        }

        # Step 1: Check current status
        status = await self.check_pr_status(pr_number)
        orchestration_result["steps"].append({"step": "check_status", "result": status})

        # Step 2: Trigger Sentry AI if not already processed
        if not status.get("has_sentry_review"):
            trigger_result = await self.trigger_sentry_ai(pr_number)
            orchestration_result["steps"].append(
                {"step": "trigger_sentry", "result": trigger_result}
            )

            # Wait for processing
            await asyncio.sleep(30)

        # Step 3: Analyze feedback
        analysis = await self.analyze_sentry_feedback(pr_number)
        orchestration_result["steps"].append(
            {"step": "analyze_feedback", "result": analysis}
        )

        # Step 4: Generate summary
        summary = {
            "quality_score": self._calculate_quality_score(analysis),
            "recommendation": self._get_recommendation(analysis),
            "action_required": len(analysis.get("critical_issues", [])) > 0,
        }
        orchestration_result["summary"] = summary

        # Log to Sentry
        capture_message(
            f"Completed PR quality check for #{pr_number}",
            level="info",
            extra=orchestration_result,
        )

        return orchestration_result

    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate a quality score based on Sentry AI analysis"""
        score = 100.0

        # Deduct for issues
        score -= analysis.get("issues_found", 0) * 5

        # Deduct for critical issues
        score -= len(analysis.get("critical_issues", [])) * 20

        # Add points for generated tests
        score += min(analysis.get("tests_generated", 0) * 10, 20)

        return max(0, min(100, score))

    def _get_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Get recommendation based on analysis"""
        if len(analysis.get("critical_issues", [])) > 0:
            return "BLOCK: Critical issues found - must be resolved"
        elif analysis.get("issues_found", 0) > 5:
            return "REVIEW: Multiple issues found - careful review needed"
        elif analysis.get("tests_generated", 0) == 0:
            return "CAUTION: No tests generated - consider adding tests"
        else:
            return "APPROVE: Code quality checks passed"

    async def monitor_active_prs(self) -> List[Dict[str, Any]]:
        """Monitor all active PRs for Sentry AI status"""
        if not self.github or not self.repo_name:
            return []

        try:
            repo = self.github.get_repo(self.repo_name)
            open_prs = repo.get_pulls(state="open")

            results = []
            for pr in open_prs:
                status = await self.check_pr_status(pr.number)
                results.append(status)

            return results

        except Exception as e:
            logger.error(f"Failed to monitor PRs: {e}")
            return []


# Integration with main orchestration system
class SentryAIAgent:
    """Agent for Sentry AI orchestration"""

        """  Init  """
def __init__(self):
        self.orchestrator = SentryAIOrchestrator()
        self.name = "sentry-ai-agent"
        self.status = "ready"

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a Sentry AI task"""
        task_type = task.get("type")

        if task_type == "check_pr":
            pr_number = task.get("pr_number")
            return await self.orchestrator.orchestrate_pr_quality_check(pr_number)

        elif task_type == "monitor_prs":
            return await self.orchestrator.monitor_active_prs()

        elif task_type == "analyze_pr":
            pr_number = task.get("pr_number")
            return await self.orchestrator.analyze_sentry_feedback(pr_number)

        else:
            return {"error": f"Unknown task type: {task_type}"}


# CLI for testing
async     """Main"""
def main():
    """Test the Sentry AI orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="Sentry AI Orchestrator")
    parser.add_argument("command", choices=["check", "trigger", "analyze", "monitor"])
    parser.add_argument("--pr", type=int, help="PR number")

    args = parser.parse_args()

    orchestrator = SentryAIOrchestrator()

    if args.command == "check" and args.pr:
        result = await orchestrator.check_pr_status(args.pr)
        print(json.dumps(result, indent=2))

    elif args.command == "trigger" and args.pr:
        result = await orchestrator.trigger_sentry_ai(args.pr)
        print(json.dumps(result, indent=2))

    elif args.command == "analyze" and args.pr:
        result = await orchestrator.analyze_sentry_feedback(args.pr)
        print(json.dumps(result, indent=2))

    elif args.command == "monitor":
        results = await orchestrator.monitor_active_prs()
        print(json.dumps(results, indent=2))

    else:
        print("Invalid command or missing PR number")


if __name__ == "__main__":
    asyncio.run(main())
