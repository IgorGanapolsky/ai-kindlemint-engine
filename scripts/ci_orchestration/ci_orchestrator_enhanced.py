#!/usr/bin/env python3
"""
Enhanced CI Orchestrator - Properly extracts and analyzes CI failures
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from ci_analyzer import CIAnalyzer
from ci_fixer import CIFixer
from ci_monitor_enhanced import EnhancedCIMonitor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedCIOrchestrator:
    """Enhanced orchestrator with proper failure analysis"""

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
        self.monitor = EnhancedCIMonitor(repo_owner, repo_name, github_token)
        self.analyzer = CIAnalyzer(repo_path)
        self.fixer = CIFixer(repo_path, dry_run)

    def collect_and_analyze_failures(self, lookback_minutes: int = 60) -> Dict:
        """Collect failures and analyze them"""
        logger.info("Starting enhanced CI failure collection and analysis")

        # Step 1: Collect failures with proper log extraction
        failures = self.monitor.monitor_failures(lookback_minutes)
        logger.info(f"Collected {len(failures)} failures")

        # Save raw failures for debugging
        self.monitor.save_failures(failures, "ci_failures_enhanced.json")

        # Step 2: Analyze each failure
        analysis_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "total_failures": len(failures),
            "analyzed_failures": [],
            "summary": {
                "auto_fixable": 0,
                "manual_review": 0,
                "by_strategy_type": {},
                "by_failure_type": {},
            },
        }

        for failure in failures:
            # Pass the failure with logs to the analyzer
            strategies = self.analyzer.analyze_failure(failure)
            prioritized = self.analyzer.prioritize_strategies(strategies)

            analyzed_failure = {
                "failure_info": failure,
                "strategies": [self._strategy_to_dict(s) for s in prioritized],
                "recommended_strategy": (
                    self._strategy_to_dict(prioritized[0]) if prioritized else None
                ),
            }

            analysis_results["analyzed_failures"].append(analyzed_failure)

            # Update summary statistics
            failure_type = failure.get("failure_type", "unknown")
            analysis_results["summary"]["by_failure_type"][failure_type] = (
                analysis_results["summary"]["by_failure_type"].get(failure_type, 0) + 1
            )

            if prioritized:
                best_strategy = prioritized[0]
                if best_strategy.auto_fixable and best_strategy.confidence > 0.7:
                    analysis_results["summary"]["auto_fixable"] += 1
                else:
                    analysis_results["summary"]["manual_review"] += 1

                stype = best_strategy.strategy_type
                analysis_results["summary"]["by_strategy_type"][stype] = (
                    analysis_results["summary"]["by_strategy_type"].get(stype, 0) + 1
                )

        # Save enhanced analysis
        with open("ci_analysis_enhanced.json", "w") as f:
            json.dump(analysis_results, f, indent=2)

        logger.info("Enhanced analysis complete")
        return analysis_results

    def _strategy_to_dict(self, strategy) -> Dict:
        """Convert strategy object to dictionary"""
        return {
            "strategy_type": strategy.strategy_type,
            "description": strategy.description,
            "confidence": strategy.confidence,
            "files_to_modify": strategy.files_to_modify,
            "commands": strategy.commands,
            "estimated_complexity": strategy.estimated_complexity,
            "auto_fixable": strategy.auto_fixable,
        }

    def execute_fixes(self, analysis_results: Dict, max_fixes: int = 5) -> Dict:
        """Execute recommended fixes for failures"""
        fix_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "attempted_fixes": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "fixes": [],
        }

        fixes_attempted = 0

        for analyzed_failure in analysis_results["analyzed_failures"]:
            if fixes_attempted >= max_fixes:
                break

            failure_info = analyzed_failure["failure_info"]
            recommended = analyzed_failure.get("recommended_strategy")

            if not recommended:
                continue

            # Only attempt high-confidence auto-fixable strategies
            if recommended["auto_fixable"] and recommended["confidence"] > 0.8:
                logger.info(
                    f"Attempting fix for {failure_info['job_name']}: {recommended['description']}"
                )

                fix_result = {
                    "failure": failure_info["job_name"],
                    "strategy": recommended["strategy_type"],
                    "description": recommended["description"],
                    "status": "pending",
                    "error": None,
                }

                try:
                    # Execute the fix
                    if self.dry_run:
                        logger.info(
                            f"DRY RUN: Would execute {recommended['strategy_type']}"
                        )
                        fix_result["status"] = "dry_run"
                    else:
                        # Convert dict back to strategy object for fixer
                        from ci_analyzer import FixStrategy

                        strategy = FixStrategy(**recommended)

                        success = self.fixer.apply_fix(strategy, failure_info)
                        fix_result["status"] = "success" if success else "failed"

                        if success:
                            fix_results["successful_fixes"] += 1
                        else:
                            fix_results["failed_fixes"] += 1

                except Exception as e:
                    logger.error(f"Fix failed with error: {e}")
                    fix_result["status"] = "error"
                    fix_result["error"] = str(e)
                    fix_results["failed_fixes"] += 1

                fix_results["fixes"].append(fix_result)
                fixes_attempted += 1
                fix_results["attempted_fixes"] += 1

        # Save fix results
        with open("ci_fix_results.json", "w") as f:
            json.dump(fix_results, f, indent=2)

        return fix_results

    def run_complete_cycle(self) -> Dict:
        """Run a complete orchestration cycle"""
        logger.info("Starting enhanced CI orchestration cycle")

        # Collect and analyze
        analysis = self.collect_and_analyze_failures()

        # Print summary
        self._print_analysis_summary(analysis)

        # Execute fixes if not in dry run
        if not self.dry_run and analysis["summary"]["auto_fixable"] > 0:
            fix_results = self.execute_fixes(analysis)
            self._print_fix_summary(fix_results)

        return analysis

    def _print_analysis_summary(self, analysis: Dict):
        """Print analysis summary"""
        print(f"\n{'='*60}")
        print(f"CI Failure Analysis Summary")
        print(f"{'='*60}")
        print(f"Repository: {analysis['repository']}")
        print(f"Total failures: {analysis['total_failures']}")
        print(f"Auto-fixable: {analysis['summary']['auto_fixable']}")
        print(f"Manual review: {analysis['summary']['manual_review']}")

        print("\nFailures by type:")
        for ftype, count in analysis["summary"]["by_failure_type"].items():
            print(f"  - {ftype}: {count}")

        print("\nStrategies by type:")
        for stype, count in analysis["summary"]["by_strategy_type"].items():
            print(f"  - {stype}: {count}")

        # Show puzzle-specific failures
        puzzle_failures = [
            f
            for f in analysis["analyzed_failures"]
            if f["failure_info"].get("failure_type") == "puzzle_qa_failure"
        ]

        if puzzle_failures:
            print(f"\n⚠️  Found {len(puzzle_failures)} puzzle QA failures:")
            for pf in puzzle_failures[:3]:  # Show first 3
                print(
                    f"  - {pf['failure_info']['job_name']}: {pf['failure_info']['error_message']}"
                )

    def _print_fix_summary(self, fix_results: Dict):
        """Print fix execution summary"""
        print(f"\n{'='*60}")
        print(f"Fix Execution Summary")
        print(f"{'='*60}")
        print(f"Attempted: {fix_results['attempted_fixes']}")
        print(f"Successful: {fix_results['successful_fixes']}")
        print(f"Failed: {fix_results['failed_fixes']}")

        if fix_results["fixes"]:
            print("\nFix details:")
            for fix in fix_results["fixes"]:
                status_emoji = {
                    "success": "✅",
                    "failed": "❌",
                    "error": "⚠️",
                    "dry_run": "🔍",
                }.get(fix["status"], "❓")
                print(
                    f"  {status_emoji} {fix['failure']}: {fix['description']} ({fix['status']})"
                )


def main():
    """Main entry point for enhanced orchestrator"""
    parser = argparse.ArgumentParser(
        description="Enhanced CI orchestrator with proper failure analysis"
    )
    parser.add_argument("--owner", default="IgorGanapolsky", help="Repository owner")
    parser.add_argument(
        "--repo", default="ai-kindlemint-engine", help="Repository name"
    )
    parser.add_argument(
        "--lookback", type=int, default=120, help="Minutes to look back for failures"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze but don't apply fixes"
    )
    parser.add_argument(
        "--max-fixes", type=int, default=5, help="Maximum fixes to attempt"
    )

    args = parser.parse_args()

    orchestrator = EnhancedCIOrchestrator(args.owner, args.repo, dry_run=args.dry_run)

    analysis = orchestrator.run_complete_cycle()

    print(f"\n✅ Enhanced CI orchestration complete")
    print(f"📄 Analysis saved to: ci_analysis_enhanced.json")


if __name__ == "__main__":
    main()
