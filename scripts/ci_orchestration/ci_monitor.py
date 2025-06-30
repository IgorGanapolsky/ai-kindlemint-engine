#!/usr/bin/env python3
"""
CI Monitor - Monitors GitHub Actions for failures and triggers automated fixes
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CIMonitor:
    """Monitors GitHub Actions workflows for failures"""

    def __init__(
        self, repo_owner: str, repo_name: str, github_token: Optional[str] = None
    ):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.github_token}" if self.github_token else "",
        }

    def get_workflow_runs(self, limit: int = 10, status: str = "failure") -> List[Dict]:
        """Get recent workflow runs with specified status"""
        url = f"{self.api_base}/actions/runs"
        params = {"status": status, "per_page": limit}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("workflow_runs", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch workflow runs: {e}")
            return []

    def get_workflow_logs(self, run_id: int) -> Optional[str]:
        """Download logs for a specific workflow run using GitHub CLI"""
        try:
            # Use GitHub CLI to get detailed logs
            cmd = (
                f"gh run view {run_id} --repo {self.repo_owner}/{self.repo_name} --log"
            )
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(
                    f"Failed to fetch logs for run {run_id}: {result.stderr}")
                # Fallback to API if CLI fails
                return self._get_workflow_logs_api_fallback(run_id)
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout fetching logs for run {run_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch logs for run {run_id}: {e}")
            return None

    def _get_workflow_logs_api_fallback(self, run_id: int) -> Optional[str]:
        """Fallback method to get basic log info from API"""
        # Get job details to at least have some information
        jobs = self.get_job_details(run_id)
        log_summary = []

        for job in jobs:
            if job.get("conclusion") == "failure":
                log_summary.append(f"Job: {job.get('name', 'Unknown')}")
                log_summary.append(
                    f"Status: {job.get('conclusion', 'Unknown')}")

                # Get steps to find which step failed
                steps = job.get("steps", [])
                for step in steps:
                    if step.get("conclusion") == "failure":
                        log_summary.append(
                            f"Failed step: {step.get('name', 'Unknown')}"
                        )

        return "\n".join(log_summary) if log_summary else None

    def get_job_details(self, run_id: int) -> List[Dict]:
        """Get job details for a workflow run"""
        url = f"{self.api_base}/actions/runs/{run_id}/jobs"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch jobs for run {run_id}: {e}")
            return []

    def categorize_failure(self, job: Dict, logs: str) -> Dict:
        """Categorize the type of failure based on job info and logs"""
        failure_info = {
            "job_name": job.get("name", ""),
            "job_id": job.get("id"),
            "status": job.get("status"),
            "conclusion": job.get("conclusion"),
            "failed_step": None,
            "failure_type": "unknown",
            "error_message": "",
            "suggested_fix": None,
        }

        # Find the failed step
        for step in job.get("steps", []):
            if step.get("conclusion") == "failure":
                failure_info["failed_step"] = step.get("name")
                break

        # Analyze logs to categorize failure
        if logs:
            logs_lower = logs.lower()

            # Import errors
            if "modulenotfounderror" in logs_lower or "importerror" in logs_lower:
                failure_info["failure_type"] = "import_error"
                # Extract module name
                import_match = self._extract_error_pattern(
                    logs, r"No module named '([^']+)'"
                )
                if import_match:
                    failure_info["error_message"] = f"Missing module: {import_match}"
                    failure_info["suggested_fix"] = (
                        f"Add missing import for {import_match}"
                    )

            # Test failures
            elif "failed" in logs_lower and (
                "test" in logs_lower or "pytest" in logs_lower
            ):
                failure_info["failure_type"] = "test_failure"
                failure_info["error_message"] = "Unit or integration tests failed"
                failure_info["suggested_fix"] = (
                    "Fix failing test assertions or update test data"
                )

            # Syntax errors
            elif "syntaxerror" in logs_lower:
                failure_info["failure_type"] = "syntax_error"
                syntax_match = self._extract_error_pattern(
                    logs, r"SyntaxError: (.+)")
                if syntax_match:
                    failure_info["error_message"] = f"Syntax error: {syntax_match}"
                    failure_info["suggested_fix"] = "Fix syntax error in code"

            # Linting errors
            elif (
                "flake8" in logs_lower or "black" in logs_lower or "isort" in logs_lower
            ):
                failure_info["failure_type"] = "linting_error"
                failure_info["error_message"] = "Code style or linting violations"
                failure_info["suggested_fix"] = (
                    "Run formatters and fix style violations"
                )

            # Type errors
            elif "typeerror" in logs_lower or "mypy" in logs_lower:
                failure_info["failure_type"] = "type_error"
                type_match = self._extract_error_pattern(
                    logs, r"TypeError: (.+)")
                if type_match:
                    failure_info["error_message"] = f"Type error: {type_match}"
                    failure_info["suggested_fix"] = (
                        "Fix type annotations or type mismatches"
                    )

            # Dependency errors
            elif "requirements" in logs_lower or "pip install" in logs_lower:
                failure_info["failure_type"] = "dependency_error"
                failure_info["error_message"] = "Dependency installation failed"
                failure_info["suggested_fix"] = (
                    "Update requirements.txt or resolve conflicts"
                )

            # Path/File errors
            elif "filenotfounderror" in logs_lower or "no such file" in logs_lower:
                failure_info["failure_type"] = "path_error"
                path_match = self._extract_error_pattern(
                    logs, r"No such file or directory: '([^']+)'"
                )
                if path_match:
                    failure_info["error_message"] = f"Missing file: {path_match}"
                    failure_info["suggested_fix"] = (
                        f"Create missing file or fix path to {path_match}"
                    )

        return failure_info

    def _extract_error_pattern(self, logs: str, pattern: str) -> Optional[str]:
        """Extract error details using regex pattern"""
        import re

        match = re.search(pattern, logs, re.IGNORECASE | re.MULTILINE)
        return match.group(1) if match else None

    def monitor_failures(self, lookback_minutes: int = 60) -> List[Dict]:
        """Monitor recent CI failures"""
        logger.info(
            f"Monitoring CI failures for {self.repo_owner}/{self.repo_name}")

        # Get failed workflow runs
        failed_runs = self.get_workflow_runs(limit=20, status="failure")

        # Filter by time window
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        recent_failures = []

        for run in failed_runs:
            run_time = datetime.strptime(
                run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if run_time >= cutoff_time:
                # Get detailed job information
                jobs = self.get_job_details(run["id"])
                logs = self.get_workflow_logs(run["id"])

                for job in jobs:
                    if job.get("conclusion") == "failure":
                        failure_info = self.categorize_failure(job, logs)
                        failure_info["workflow_name"] = run.get("name")
                        failure_info["workflow_id"] = run.get("id")
                        failure_info["branch"] = run.get("head_branch")
                        failure_info["commit_sha"] = run.get("head_sha")
                        failure_info["run_url"] = run.get("html_url")
                        failure_info["created_at"] = run.get("created_at")

                        recent_failures.append(failure_info)

        logger.info(f"Found {len(recent_failures)} recent failures")
        return recent_failures

    def save_failure_report(
        self, failures: List[Dict], output_path: str = "ci_failures.json"
    ):
        """Save failure report to file"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "total_failures": len(failures),
            "failures": failures,
            "failure_summary": self._generate_summary(failures),
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved failure report to {output_path}")
        return report

    def _generate_summary(self, failures: List[Dict]) -> Dict:
        """Generate summary statistics of failures"""
        summary = {"by_type": {}, "by_workflow": {}, "by_branch": {}}

        for failure in failures:
            # Count by type
            ftype = failure["failure_type"]
            summary["by_type"][ftype] = summary["by_type"].get(ftype, 0) + 1

            # Count by workflow
            workflow = failure["workflow_name"]
            summary["by_workflow"][workflow] = (
                summary["by_workflow"].get(workflow, 0) + 1
            )

            # Count by branch
            branch = failure["branch"]
            summary["by_branch"][branch] = summary["by_branch"].get(
                branch, 0) + 1

        return summary


def main():
    """Main entry point for CI monitoring"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor GitHub Actions CI failures")
    parser.add_argument("--owner", default="igorganapolsky",
                        help="Repository owner")
    parser.add_argument(
        "--repo", default="ai-kindlemint-engine", help="Repository name"
    )
    parser.add_argument("--lookback", type=int, default=60,
                        help="Minutes to look back")
    parser.add_argument(
        "--output", default="ci_failures.json", help="Output file path")
    parser.add_argument(
        "--watch", action="store_true", help="Continuous monitoring mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (watch mode)",
    )

    args = parser.parse_args()

    # Initialize monitor
    monitor = CIMonitor(args.owner, args.repo)

    if args.watch:
        # Continuous monitoring mode
        logger.info(
            f"Starting continuous monitoring (checking every {args.interval} seconds)"
        )
        while True:
            try:
                failures = monitor.monitor_failures(args.lookback)
                if failures:
                    monitor.save_failure_report(failures, args.output)
                    logger.info(
                        f"Found {len(failures)} failures - report saved")
                else:
                    logger.info("No recent failures found")

                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(args.interval)
    else:
        # Single run mode
        failures = monitor.monitor_failures(args.lookback)
        report = monitor.save_failure_report(failures, args.output)

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"CI Failure Report - {report['timestamp']}")
        print(f"{'=' * 60}")
        print(f"Total failures: {report['total_failures']}")

        if failures:
            print("\nFailures by type:")
            for ftype, count in report["failure_summary"]["by_type"].items():
                print(f"  - {ftype}: {count}")

            print("\nFailures by workflow:")
            for workflow, count in report["failure_summary"]["by_workflow"].items():
                print(f"  - {workflow}: {count}")

            print(f"\nDetailed report saved to: {args.output}")
        else:
            print("\nNo recent CI failures found!")


if __name__ == "__main__":
    main()
