#!/usr/bin/env python3
"""
Test enhanced CI orchestration using GitHub CLI
"""

import json
import subprocess


# Test using GitHub CLI to get recent failures
def test_gh_cli():
    print("Testing GitHub CLI access...")

    # Get recent failed runs
    cmd = "gh run list --repo IgorGanapolsky/ai-kindlemint-engine --status failure --limit 10 --json databaseId,name,conclusion,createdAt,headBranch"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return

    runs = json.loads(result.stdout)
    print(f"Found {len(runs)} failed runs")

    # Get details for the first failed run
    if runs:
        run = runs[0]
        run_id = run["databaseId"]
        print(f"\nAnalyzing run: {run['name']} (ID: {run_id})")

        # Get job details
        cmd = f"gh run view {run_id} --repo IgorGanapolsky/ai-kindlemint-engine --json jobs"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            job_data = json.loads(result.stdout)
            jobs = job_data.get("jobs", [])

            for job in jobs:
                if job.get("conclusion") == "failure":
                    print(f"\nFailed job: {job['name']}")

                    # Find failed step
                    for step in job.get("steps", []):
                        if step.get("conclusion") == "failure":
                            print(f"Failed step: {step['name']}")

                            # Try to get logs for this job
                            job_id = job["databaseId"]
                            cmd = f"gh api repos/IgorGanapolsky/ai-kindlemint-engine/actions/jobs/{job_id}/logs"
                            log_result = subprocess.run(
                                cmd, shell=True, capture_output=True, text=True
                            )

                            if log_result.returncode == 0:
                                # Extract relevant error messages
                                logs = log_result.stdout
                                if "blank_puzzles" in logs:
                                    print("❌ FOUND: Blank puzzles issue in logs!")
                                elif "missing_clues" in logs:
                                    print("❌ FOUND: Missing clues issue in logs!")
                                elif "puzzle integrity" in logs:
                                    print("❌ FOUND: Puzzle integrity issue in logs!")
                                else:
                                    # Show first 500 chars of logs
                                    print(f"Log preview: {logs[:500]}...")


if __name__ == "__main__":
    test_gh_cli()
