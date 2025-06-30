#!/usr/bin/env python3
"""
Enhanced CI Monitor - Properly extracts step logs for failure analysis
"""

import json
import logging
import os
import re
import subprocess
import sys
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


class EnhancedCIMonitor:
    """Enhanced CI Monitor with proper step log extraction"""

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

    def get_job_logs(self, job_id: int) -> Optional[str]:
        """Get logs for a specific job"""
        url = f"{self.api_base}/actions/jobs/{job_id}/logs"

        try:
            # The logs endpoint returns a redirect to the log file
            response = requests.get(
                url, headers=self.headers, allow_redirects=False)

            if response.status_code == 302:
                # Follow the redirect to get the actual logs
                log_url = response.headers.get("Location")
                if log_url:
                    log_response = requests.get(log_url)
                    if log_response.status_code == 200:
                        return log_response.text

            # Fallback to GitHub CLI if API fails
            return self._get_job_logs_cli_fallback(job_id)

        except Exception as e:
            logger.error(f"Failed to fetch logs for job {job_id}: {e}")
            return None

    def _get_job_logs_cli_fallback(self, job_id: int) -> Optional[str]:
        """Fallback to GitHub CLI for job logs"""
        try:
            cmd = f"gh api repos/{self.repo_owner}/{
                self.repo_name}/actions/jobs/{job_id}/logs"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None

    def extract_step_logs(self, logs: str, failed_step: str) -> str:
        """Extract logs for a specific failed step"""
        if not logs or not failed_step:
            return ""

        # GitHub Actions logs have a specific format
        # Each step starts with a timestamp and the step name
        step_pattern = rf"\d{{4}} -\d{{2}} -\d{{2}}T\d{{2}}: \d{{2}}: \d{{2}}\.\d+Z {
            re.escape(failed_step)}"

        lines = logs.split("\n")
        step_logs = []
        in_step = False

        for i, line in enumerate(lines):
            if re.search(step_pattern, line):
                in_step = True
                continue

            if in_step:
                # Check if we've reached the next step
                if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z", line):
                    break
                step_logs.append(line)

        return "\n".join(step_logs)

    def categorize_failure(self, job: Dict, logs: str) -> Dict:
        """Enhanced failure categorization with puzzle-specific detection"""
        failure_info = {
            "job_name": job.get("name", ""),
            "job_id": job.get("id"),
            "status": job.get("status"),
            "conclusion": job.get("conclusion"),
            "failed_step": None,
            "failure_type": "unknown",
            "error_message": "",
            "suggested_fix": None,
            "logs": "",  # Include actual logs for analyzer
        }

        # Find the failed step
        failed_step = None
        for step in job.get("steps", []):
            if step.get("conclusion") == "failure":
                failed_step = step.get("name")
                failure_info["failed_step"] = failed_step
                break

        # Get logs for this specific job
        if job.get("id"):
            job_logs = self.get_job_logs(job["id"])
            if job_logs:
                # Extract logs for the failed step
                step_logs = (
                    self.extract_step_logs(job_logs, failed_step)
                    if failed_step
                    else job_logs
                )
                failure_info["logs"] = step_logs
                logs = step_logs  # Use step-specific logs for categorization

        # Analyze logs to categorize failure
        if logs:
            logs_lower = logs.lower()

            # Puzzle-specific QA failures
            if any(
                pattern in logs
                for pattern in [
                    "blank_puzzles",
                    "missing_clues",
                    "repeated_solutions",
                    "puzzle integrity",
                    "unsellable",
                    "missing instructions",
                ]
            ):
                failure_info["failure_type"] = "puzzle_qa_failure"

                # Extract specific puzzle issues
                if (
                    "blank_puzzles" in logs
                    or "Detected blank or missing puzzle grids" in logs
                ):
                    failure_info["error_message"] = (
                        "Blank puzzles detected - no visible content"
                    )
                elif "missing_clues" in logs:
                    match = re.search(
                        r"Only (\d+)% of puzzles have visible clues", logs
                    )
                    if match:
                        failure_info["error_message"] = (
                            f"Missing clues - only {match.group(1)}% have clues"
                        )
                elif "missing instructions" in logs:
                    failure_info["error_message"] = "Puzzles lack customer instructions"
                else:
                    failure_info["error_message"] = "Puzzle content validation failed"

                failure_info["suggested_fix"] = "Fix puzzle generation and validation"

            # PDF generation errors
            elif any(
                pattern in logs
                for pattern in [
                    "create_puzzle_grid",
                    "create_solution_grid",
                    "AttributeError",
                    "could not generate puzzle grid",
                ]
            ):
                failure_info["failure_type"] = "pdf_generation_error"
                failure_info["error_message"] = (
                    "PDF generation failed - missing fallback methods"
                )
                failure_info["suggested_fix"] = (
                    "Implement create_puzzle_grid and create_solution_grid methods"
                )

            # Import errors
            elif "modulenotfounderror" in logs_lower or "importerror" in logs_lower:
                failure_info["failure_type"] = "import_error"
                import_match = re.search(r"No module named '([^']+)'", logs)
                if import_match:
                    failure_info["error_message"] = (
                        f"Missing module: {import_match.group(1)}"
                    )
                    failure_info["suggested_fix"] = f"Install {import_match.group(1)}"

            # Test failures
            elif "failed" in logs_lower and (
                "test" in logs_lower or "pytest" in logs_lower
            ):
                failure_info["failure_type"] = "test_failure"
                # Extract test details
                test_match = re.search(r"FAILED (.*)::(.*) -", logs)
                if test_match:
                    failure_info["error_message"] = (
                        f"Test failed: {test_match.group(2)}"
                    )
                else:
                    failure_info["error_message"] = "Unit or integration tests failed"
                failure_info["suggested_fix"] = "Fix failing test assertions"

            # Other error types...
            elif "syntaxerror" in logs_lower:
                failure_info["failure_type"] = "syntax_error"
                syntax_match = re.search(r"SyntaxError: (.+)", logs)
                if syntax_match:
                    failure_info["error_message"] = (
                        f"Syntax error: {syntax_match.group(1)}"
                    )

        return failure_info

    def monitor_failures(self, lookback_minutes: int = 60) -> List[Dict]:
        """Monitor recent CI failures with enhanced log extraction"""
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

                for job in jobs:
                    if job.get("conclusion") == "failure":
                        # Get job-specific logs
                        failure_info = self.categorize_failure(job, "")

                        # Add workflow metadata
                        failure_info["workflow_name"] = run.get("name")
                        failure_info["workflow_id"] = run.get("id")
                        failure_info["branch"] = run.get("head_branch")
                        failure_info["commit_sha"] = run.get("head_sha")
                        failure_info["run_url"] = run.get("html_url")
                        failure_info["created_at"] = run.get("created_at")

                        recent_failures.append(failure_info)

        logger.info(f"Found {len(recent_failures)} recent failures")
        return recent_failures

    def save_failures(
        self, failures: List[Dict], output_file: str = "ci_failures.json"
    ):
        """Save failure data to JSON file"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "total_failures": len(failures),
            "failures": failures,
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved {len(failures)} failures to {output_file}")


def main():
    """Test the enhanced CI monitor"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor GitHub Actions for failures")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument(
        "--lookback", type=int, default=60, help="Minutes to look back (default: 60)"
    )
    parser.add_argument(
        "--output", default="ci_failures.json", help="Output file for failures"
    )

    args = parser.parse_args()

    monitor = EnhancedCIMonitor(args.owner, args.repo)
    failures = monitor.monitor_failures(args.lookback)
    monitor.save_failures(failures, args.output)

    # Print summary
    print(
        f"\nFound {len(failures)} failures in the last {args.lookback} minutes")
    for failure in failures:
        print(f"\n- {failure['job_name']} ({failure['failure_type']})")
        print(f"  Step: {failure['failed_step']}")
        print(f"  Error: {failure['error_message']}")


if __name__ == "__main__":
    main()
