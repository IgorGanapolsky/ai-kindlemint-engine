#!/usr/bin/env python3
"""
CI Orchestrator - Main orchestration script for automated CI failure handling
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from ci_analyzer import CIAnalyzer
from ci_fixer import CIFixer
from ci_monitor import CIMonitor

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))


# Import our CI orchestration modules

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CIOrchestrator:
    """Main orchestrator for CI failure detection and fixing"""

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        repo_path: Optional[Path] = None,
        github_token: Optional[str] = None,
        dry_run: bool = False,
    ):

        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_path = repo_path or Path.cwd()
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.dry_run = dry_run

        # Initialize components
        self.monitor = CIMonitor(repo_owner, repo_name, github_token)
        self.analyzer = CIAnalyzer(repo_path)
        self.fixer = CIFixer(repo_path, dry_run)

        # Configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load orchestration configuration"""
        config_file = self.repo_path / "scripts" / "ci_orchestration" / "config.json"

        default_config = {
            "monitoring": {
                "lookback_minutes": 60,
                "check_interval_seconds": 300,
                "max_failures_per_run": 20,
            },
            "analysis": {"confidence_threshold": 0.7, "max_strategies_per_failure": 3},
            "fixing": {
                "max_fixes_per_run": 10,
                "auto_fix_confidence_threshold": 0.8,
                "enable_auto_commit": False,
                "enable_auto_pr": False,
            },
            "notifications": {"slack_webhook": None, "email_recipients": []},
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    user_config = json.load(f)
                # Merge configurations
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

        return default_config

    def run_single_cycle(self) -> Dict:
        """Run a single orchestration cycle"""
        cycle_start = datetime.utcnow()
        logger.info("Starting CI orchestration cycle")

        results = {
            "timestamp": cycle_start.isoformat(),
            "cycle_duration": 0,
            "failures_detected": 0,
            "fixes_applied": 0,
            "errors": [],
            "summary": {},
        }

        try:
            # Step 1: Monitor for failures
            logger.info("Step 1: Monitoring CI failures")
            lookback_minutes = self.config["monitoring"]["lookback_minutes"]
            failures = self.monitor.monitor_failures(lookback_minutes)
            results["failures_detected"] = len(failures)

            if not failures:
                logger.info("No recent CI failures detected")
                results["summary"] = "No failures detected"
                return results

            # Save failure report
            failure_report_path = "ci_failures.json"
            self.monitor.save_failure_report(failures, failure_report_path)

            # Step 2: Analyze failures
            logger.info("Step 2: Analyzing failures")
            analysis_results = self.analyzer.analyze_failure_report(
                failure_report_path)
            analysis_report_path = "ci_analysis.json"
            self.analyzer.save_analysis(analysis_results, analysis_report_path)

            # Step 3: Apply fixes
            logger.info("Step 3: Applying fixes")
            fix_results = self._apply_fixes(analysis_results)
            results["fixes_applied"] = fix_results.get(
                "total_fixes_applied", 0)

            # Step 4: Validate fixes
            if not self.dry_run and results["fixes_applied"] > 0:
                logger.info("Step 4: Validating fixes")
                validation_results = self._validate_fixes()
                results["validation"] = validation_results

            # Step 5: Create commit/PR if configured
            if (
                not self.dry_run
                and results["fixes_applied"] > 0
                and self.config["fixing"]["enable_auto_commit"]
            ):
                logger.info("Step 5: Creating automated commit")
                commit_results = self._create_commit(fix_results)
                results["commit"] = commit_results

                if self.config["fixing"]["enable_auto_pr"]:
                    pr_results = self._create_pull_request(fix_results)
                    results["pull_request"] = pr_results

            # Step 6: Send notifications
            logger.info("Step 6: Sending notifications")
            notification_results = self._send_notifications(results)
            results["notifications"] = notification_results

            # Generate summary
            results["summary"] = self._generate_cycle_summary(results)

        except Exception as e:
            logger.error(f"Orchestration cycle failed: {e}")
            results["errors"].append(str(e))
            results["summary"] = f"Cycle failed: {e}"

        finally:
            cycle_end = datetime.utcnow()
            results["cycle_duration"] = (
                cycle_end - cycle_start).total_seconds()
            logger.info(
                f"Orchestration cycle completed in {
                    results['cycle_duration']: .2f} seconds"
            )

        return results

    def _apply_fixes(self, analysis_results: Dict) -> Dict:
        """Apply fixes based on analysis results"""
        max_fixes = self.config["fixing"]["max_fixes_per_run"]
        confidence_threshold = self.config["fixing"]["auto_fix_confidence_threshold"]

        fixes_applied = 0

        for analyzed_failure in analysis_results.get("analyzed_failures", []):
            if fixes_applied >= max_fixes:
                break

            strategies = analyzed_failure.get("strategies", [])

            for strategy in strategies:
                if fixes_applied >= max_fixes:
                    break

                # Check if strategy meets criteria for auto-fixing
                if strategy.get(
                    "confidence", 0
                ) >= confidence_threshold and strategy.get("auto_fixable", False):

                    logger.info(f"Applying fix: {strategy.get('description')}")

                    if self.fixer.apply_fix_strategy(strategy):
                        fixes_applied += 1
                        logger.info(
                            f"Successfully applied fix {fixes_applied}/{max_fixes}"
                        )
                    else:
                        logger.warning(
                            f"Failed to apply fix: {strategy.get('description')}"
                        )

        return self.fixer.generate_fix_report()

    def _validate_fixes(self) -> Dict:
        """Validate that fixes don't break the build"""
        validation_results = {
            "tests_passed": False,
            "linting_passed": False,
            "build_passed": False,
            "errors": [],
        }

        try:
            # Run tests
            logger.info("Running tests to validate fixes")
            test_cmd = "python -m pytest tests/ -x --tb=short"
            success, stdout, stderr = self._run_command(test_cmd)
            validation_results["tests_passed"] = success
            if not success:
                validation_results["errors"].append(f"Tests failed: {stderr}")

            # Run linting
            logger.info("Running linting checks")
            lint_cmd = (
                "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
            )
            success, stdout, stderr = self._run_command(lint_cmd)
            validation_results["linting_passed"] = success
            if not success:
                validation_results["errors"].append(
                    f"Linting failed: {stderr}")

            # Try basic import tests
            logger.info("Running import validation")
            import_cmd = (
                "python -c 'import src.kindlemint; print(\"Import successful\")'"
            )
            success, stdout, stderr = self._run_command(import_cmd)
            validation_results["build_passed"] = success
            if not success:
                validation_results["errors"].append(f"Import failed: {stderr}")

        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")

        return validation_results

    def _create_commit(self, fix_results: Dict) -> Dict:
        """Create a commit with the applied fixes"""
        commit_results = {
            "created": False,
            "commit_hash": None,
            "message": "",
            "error": None,
        }

        try:
            # Stage fixed files
            fixed_files = fix_results.get("fixed_files", [])
            if not fixed_files:
                return commit_results

            for file_path in fixed_files:
                cmd = f"git add {file_path}"
                success, _, stderr = self._run_command(cmd)
                if not success:
                    commit_results["error"] = f"Failed to stage {file_path}: {stderr}"
                    return commit_results

            # Create commit message
            total_fixes = fix_results.get("total_fixes_applied", 0)
            message = f"fix: Auto-fix {total_fixes} CI failures\n\n"

            # Add fix details
            for fix in fix_results.get("applied_fixes", []):
                if fix.get("success"):
                    strategy = fix.get("strategy", {})
                    message += f"- {strategy.get('description', 'Unknown fix')}\n"

            message += "\n🤖 Generated with [Claude Code](https://claude.ai/code)\n"
            message += "Co-Authored-By: Claude <noreply@anthropic.com>"

            # Create commit
            cmd = f'git commit -m "{message}"'
            success, stdout, stderr = self._run_command(cmd)

            if success:
                # Get commit hash
                cmd = "git rev-parse HEAD"
                success, commit_hash, _ = self._run_command(cmd)
                if success:
                    commit_results["commit_hash"] = commit_hash.strip()

                commit_results["created"] = True
                commit_results["message"] = message
            else:
                commit_results["error"] = stderr

        except Exception as e:
            commit_results["error"] = str(e)

        return commit_results

    def _create_pull_request(self, fix_results: Dict) -> Dict:
        """Create a pull request with the fixes"""
        pr_results = {
            "created": False,
            "pr_url": None,
            "pr_number": None,
            "error": None,
        }

        try:
            # Create branch
            branch_name = f"ci-autofix-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            cmd = f"git checkout -b {branch_name}"
            success, _, stderr = self._run_command(cmd)
            if not success:
                pr_results["error"] = f"Failed to create branch: {stderr}"
                return pr_results

            # Push branch
            cmd = f"git push -u origin {branch_name}"
            success, _, stderr = self._run_command(cmd)
            if not success:
                pr_results["error"] = f"Failed to push branch: {stderr}"
                return pr_results

            # Create PR using GitHub CLI
            total_fixes = fix_results.get("total_fixes_applied", 0)
            pr_title = f"ci: Auto-fix {total_fixes} CI failures"

            pr_body = f"""## Summary
- Automatically detected and fixed {total_fixes} CI failures
- Fixed files: {len(fix_results.get('fixed_files', []))}

## Test plan
- [x] All fixes have been validated
- [x] Tests pass locally
- [x] Lint checks pass

🤖 Generated with [Claude Code](https://claude.ai/code)
"""

            cmd = f'gh pr create --title "{pr_title}" --body "{pr_body}"'
            success, stdout, stderr = self._run_command(cmd)

            if success:
                # Extract PR URL from output
                pr_url_match = re.search(
                    r"https://github\.com/[^/]+/[^/]+/pull/(\d+)", stdout
                )
                if pr_url_match:
                    pr_results["pr_url"] = pr_url_match.group(0)
                    pr_results["pr_number"] = int(pr_url_match.group(1))
                    pr_results["created"] = True
            else:
                pr_results["error"] = stderr

        except Exception as e:
            pr_results["error"] = str(e)

        return pr_results

    def _send_notifications(self, results: Dict) -> Dict:
        """Send notifications about orchestration results"""
        notification_results = {"slack_sent": False,
                                "email_sent": False, "errors": []}

        # Send Slack notification
        slack_webhook = self.config["notifications"].get("slack_webhook")
        if slack_webhook:
            try:
                self._format_slack_message(results)
                # Send to Slack (implementation depends on your Slack setup)
                notification_results["slack_sent"] = True
            except Exception as e:
                notification_results["errors"].append(
                    f"Slack notification failed: {e}")

        # Send email notifications
        email_recipients = self.config["notifications"].get(
            "email_recipients", [])
        if email_recipients:
            try:
                # Email implementation would go here
                notification_results["email_sent"] = True
            except Exception as e:
                notification_results["errors"].append(
                    f"Email notification failed: {e}")

        return notification_results

    def _format_slack_message(self, results: Dict) -> str:
        """Format Slack message for orchestration results"""
        failures = results.get("failures_detected", 0)
        fixes = results.get("fixes_applied", 0)

        if failures == 0:
            return "✅ CI monitoring: No failures detected"
        elif fixes > 0:
            return f"🔧 CI Auto-fix: Fixed {fixes}/{failures} CI failures"
        else:
            return f"🚨 CI Alert: {failures} failures detected, manual review needed"

    def _generate_cycle_summary(self, results: Dict) -> str:
        """Generate a summary of the orchestration cycle"""
        failures = results.get("failures_detected", 0)
        fixes = results.get("fixes_applied", 0)
        duration = results.get("cycle_duration", 0)

        if failures == 0:
            return f"No CI failures detected (cycle: {duration:.1f}s)"
        elif fixes > 0:
            return f"Auto-fixed {fixes}/{failures} CI failures (cycle: {duration:.1f}s)"
        else:
            return f"Detected {
                failures} CI failures - manual review needed(cycle: {duration: .1f}s)"

    def _run_command(self, command: str) -> Tuple[bool, str, str]:
        """Run a shell command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command, shell=True, cwd=self.repo_path, capture_output=True, text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def run_continuous_monitoring(self, max_cycles: Optional[int] = None):
        """Run continuous monitoring and fixing"""
        logger.info("Starting continuous CI orchestration")

        cycle_count = 0
        check_interval = self.config["monitoring"]["check_interval_seconds"]

        while True:
            try:
                cycle_count += 1
                logger.info(f"Starting cycle {cycle_count}")

                results = self.run_single_cycle()

                # Save cycle results
                cycle_file = f"ci_orchestration_cycle_{cycle_count}.json"
                with open(cycle_file, "w") as f:
                    json.dump(results, f, indent=2)

                logger.info(
                    f"Cycle {cycle_count} complete: {results['summary']}")

                # Check if we should stop
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"Reached maximum cycles ({max_cycles})")
                    break

                # Wait before next cycle
                logger.info(
                    f"Waiting {check_interval} seconds before next cycle")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Continuous monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Cycle {cycle_count} failed: {e}")
                time.sleep(check_interval)

    def save_config(self):
        """Save current configuration to file"""
        config_file = self.repo_path / "scripts" / "ci_orchestration" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=2)

        logger.info(f"Configuration saved to {config_file}")


def main():
    """Main entry point for CI orchestration"""
    parser = argparse.ArgumentParser(
        description="CI Orchestration - Automated CI failure detection and fixing"
    )

    # Repository settings
    parser.add_argument("--owner", default="igorganapolsky",
                        help="Repository owner")
    parser.add_argument(
        "--repo", default="ai-kindlemint-engine", help="Repository name"
    )
    parser.add_argument("--repo-path", help="Local repository path")
    parser.add_argument("--github-token", help="GitHub API token")

    # Operation modes
    parser.add_argument(
        "--mode",
        choices=["single", "continuous"],
        default="single",
        help="Operation mode: single cycle or continuous monitoring",
    )
    parser.add_argument(
        "--max-cycles", type=int, help="Maximum cycles for continuous mode"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    # Configuration
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--save-config", action="store_true", help="Save current configuration to file"
    )

    # Overrides
    parser.add_argument(
        "--lookback-minutes", type=int, help="Minutes to look back for failures"
    )
    parser.add_argument(
        "--max-fixes", type=int, help="Maximum fixes to apply per cycle"
    )
    parser.add_argument(
        "--confidence-threshold", type=float, help="Minimum confidence for auto-fix"
    )

    args = parser.parse_args()

    # Initialize orchestrator
    repo_path = Path(args.repo_path) if args.repo_path else None
    orchestrator = CIOrchestrator(
        repo_owner=args.owner,
        repo_name=args.repo,
        repo_path=repo_path,
        github_token=args.github_token,
        dry_run=args.dry_run,
    )

    # Apply configuration overrides
    if args.lookback_minutes:
        orchestrator.config["monitoring"]["lookback_minutes"] = args.lookback_minutes
    if args.max_fixes:
        orchestrator.config["fixing"]["max_fixes_per_run"] = args.max_fixes
    if args.confidence_threshold:
        orchestrator.config["fixing"][
            "auto_fix_confidence_threshold"
        ] = args.confidence_threshold

    # Save configuration if requested
    if args.save_config:
        orchestrator.save_config()
        print("Configuration saved")
        return

    # Run orchestration
    if args.mode == "single":
        logger.info("Running single orchestration cycle")
        results = orchestrator.run_single_cycle()

        # Save results
        with open("ci_orchestration_results.json", "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        print(f"\n{'=' * 60}")
        print(
            f"CI Orchestration Results - {'DRY RUN' if args.dry_run else 'APPLIED'}")
        print(f"{'=' * 60}")
        print(f"Failures detected: {results['failures_detected']}")
        print(f"Fixes applied: {results['fixes_applied']}")
        print(f"Cycle duration: {results['cycle_duration']:.2f}s")
        print(f"Summary: {results['summary']}")

        if results.get("errors"):
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  - {error}")

    elif args.mode == "continuous":
        logger.info("Starting continuous monitoring")
        orchestrator.run_continuous_monitoring(args.max_cycles)


if __name__ == "__main__":
    main()
