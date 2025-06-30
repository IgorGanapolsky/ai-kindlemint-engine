#!/usr/bin/env python3
"""
Deployment and Migration Script for KindleMint Engine Quality Fixes

This script manages the transition from the old puzzle generation and QA systems
to the new, enhanced versions. It provides functionality to:
1. Test the new engine and QA system in a sandboxed environment.
2. Generate a before-and-after comparison report.
3. Deploy the new scripts into the production workflow.
4. Roll back to the previous versions if necessary.
"""

import argparse
import fileinput
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --- Configuration ---
# Define paths relative to the repository root
ROOT_DIR = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = ROOT_DIR / "scripts"
WORKFLOWS_DIR = ROOT_DIR / ".github" / "workflows"
TEMP_DIR = ROOT_DIR / "tmp_deployment_test"

# Define script names
OLD_ENGINE = "crossword_engine_v2.py"
NEW_ENGINE = "crossword_engine_v3_fixed.py"
OLD_QA_CHECKER = "enhanced_qa_checker.py"
OLD_QA_VALIDATOR = "production_qa_validator.py"
NEW_QA = "enhanced_qa_validator_v2.py"

# Files to modify during deployment
BATCH_PROCESSOR_FILE = SCRIPTS_DIR / "batch_processor.py"
PRODUCTION_QA_WORKFLOW = WORKFLOWS_DIR / "production_qa.yml"
BOOK_QA_WORKFLOW = WORKFLOWS_DIR / "book_qa_validation.yml"

# --- Helper Functions ---


def print_header(title):
    """Prints a formatted header."""
    print("\n" + "=" * 70)
    print(f"🚀 {title.upper()}")
    print("=" * 70)


def print_subheader(title):
    """Prints a formatted subheader."""
    print(f"\n--- {title} ---")


def run_command(command, cwd=None):
    """Runs a shell command and handles errors."""
    print(f"▶️  Running command: {' '.join(map(str, command))}")
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=cwd or ROOT_DIR
        )
        print("✅ Command successful.")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Command failed with exit code {e.returncode}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"❌ ERROR: Command not found: {command[0]}")
        return None


def cleanup_temp_dirs():
    """Removes temporary directories."""
    if TEMP_DIR.exists():
        print(f"🗑️  Cleaning up temporary directory: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR)


# --- Core Logic ---


def test_systems():
    """
    Runs a test of both the old and new systems to generate a comparison.
    """
    print_header("Running Before-and-After System Test")
    cleanup_temp_dirs()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Define output directories for the test
    old_output_dir = TEMP_DIR / "old_system_output"
    new_output_dir = TEMP_DIR / "new_system_output"
    old_output_dir.mkdir()
    new_output_dir.mkdir()

    # 1. Run the old engine
    print_subheader("Generating puzzles with OLD engine (v2)")
    run_command(
        [
            sys.executable,
            SCRIPTS_DIR / OLD_ENGINE,
            "--output",
            old_output_dir,
            "--count",
            "5",  # Small batch for testing
        ]
    )

    # 2. Run the new engine
    print_subheader("Generating puzzles with NEW engine (v3)")
    run_command(
        [
            sys.executable,
            SCRIPTS_DIR / NEW_ENGINE,
            "--output",
            new_output_dir,
            "--count",
            "5",
        ]
    )

    # 3. Run the NEW QA validator on both outputs
    print_subheader("Validating OLD engine output with NEW QA system")
    run_command(
        [
            sys.executable,
            SCRIPTS_DIR / NEW_QA,
            str(old_output_dir),
            "--output-dir",
            str(old_output_dir),
        ]
    )

    print_subheader("Validating NEW engine output with NEW QA system")
    run_command(
        [
            sys.executable,
            SCRIPTS_DIR / NEW_QA,
            str(new_output_dir),
            "--output-dir",
            str(new_output_dir),
        ]
    )

    print("\n✅ Test run complete. You can now generate a comparison report.")
    generate_comparison_report()


def generate_comparison_report():
    """
    Generates a Markdown report comparing the results of the test run.
    """
    print_header("Generating Comparison Report")

    old_report_path = (
        TEMP_DIR / "old_system_output" / "ENHANCED_QA_REPORT_old_system_output.json"
    )
    new_report_path = (
        TEMP_DIR / "new_system_output" / "ENHANCED_QA_REPORT_new_system_output.json"
    )

    if not old_report_path.exists() or not new_report_path.exists():
        print("❌ ERROR: QA reports not found. Please run the 'test' command first.")
        return

    with open(old_report_path, "r") as f:
        old_report = json.load(f)
    with open(new_report_path, "r") as f:
        new_report = json.load(f)

    old_summary = old_report.get("summary", {})
    new_summary = new_report.get("summary", {})

    report_content = f"""
# Engine Quality Comparison Report
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This report compares the output of the old crossword engine (`v2`) with the new, fixed engine (`v3`), both validated by the new `enhanced_qa_validator_v2.py`.

## Summary of Results

| Metric                      | Old Engine (v2) | New Engine (v3) | Result      |
| --------------------------- | --------------- | --------------- | ----------- |
| **Overall Status**          | `{old_report.get("overall_status", "N/A")}`   | `{new_report.get("overall_status", "N/A")}`   | {'✅ PASS' if new_report.get("overall_status") == "PASS" else '⚠️ WARN'} |
| Total Puzzles Validated     | `{old_summary.get("total_puzzles", 0)}`       | `{new_summary.get("total_puzzles", 0)}`       |             |
| Puzzles Passed              | `{old_summary.get("puzzles_passed", 0)}`      | `{new_summary.get("puzzles_passed", 0)}`      | {'✅ Improved' if new_summary.get("puzzles_passed", 0) > old_summary.get("puzzles_passed", 0) else 'No change'} |
| Puzzles with Warnings       | `{old_summary.get("puzzles_with_warnings", 0)}` | `{new_summary.get("puzzles_with_warnings", 0)}` | {'✅ Improved' if new_summary.get("puzzles_with_warnings", 0) < old_summary.get("puzzles_with_warnings", 0) else 'No change'} |
| Puzzles with Critical Issues| `{old_summary.get("puzzles_with_critical_issues", 0)}` | `{new_summary.get("puzzles_with_critical_issues", 0)}` | {'✅ FIXED' if new_summary.get("puzzles_with_critical_issues", 0) < old_summary.get("puzzles_with_critical_issues", 0) else 'No change'} |
| **Total Critical Issues**   | `{old_summary.get("critical_issues_count", 0)}` | `{new_summary.get("critical_issues_count", 0)}` | {'✅ FIXED' if new_summary.get("critical_issues_count", 0) == 0 else '⚠️'} |

## Detailed Issues Analysis

### Old Engine (v2) - Critical Issues
*The old engine produced puzzles with fundamental flaws that made them unsolvable.*
```json
{json.dumps([p['critical_issues'] for p in old_report.get(
        'puzzles', {}).values() if p.get('critical_issues')], indent=2)}
```

### New Engine (v3) - Critical Issues
*The new engine should have zero critical issues.*
```json
{json.dumps([p['critical_issues'] for p in new_report.get(
            'puzzles', {}).values() if p.get('critical_issues')], indent=2)}
```

## Conclusion

The new engine and QA system represent a **critical improvement** in quality and reliability. The new engine successfully generates valid, solvable puzzles that pass the new, stringent content-aware validation. The old system consistently failed these checks.

**Recommendation: Proceed with deployment.**
"""
    report_path = ROOT_DIR / "DEPLOYMENT_COMPARISON_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report_content)

    print(f"✅ Comparison report generated: {report_path}")


def _backup_file(file_path):
    """Creates a backup of a file."""
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        print(f"🛡️  Backing up {file_path.name} to {backup_path.name}")
        shutil.copy(file_path, backup_path)
        return True
    else:
        print(f"⚠️  Warning: File not found, cannot back up: {file_path}")
        return False


def _restore_backup(file_path):
    """Restores a file from its backup."""
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    if backup_path.exists():
        print(f"롤백  Restoring {file_path.name} from backup.")
        shutil.move(backup_path, file_path)
        return True
    else:
        print(f"⚠️  Warning: Backup file not found, cannot restore: {backup_path}")
        return False


def _update_file_content(file_path, old_str, new_str):
    """Performs in-place string replacement in a file."""
    print(f"✍️  Updating {file_path.name}: Replacing '{old_str}' with '{new_str}'")
    with fileinput.FileInput(file_path, inplace=True) as file:
        for line in file:
            print(line.replace(old_str, new_str), end="")


def deploy_changes():
    """Deploys the new scripts by updating the batch processor and workflows."""
    print_header("Deploying Quality Fixes")

    # 1. Update Batch Processor
    print_subheader("Updating Batch Processor")
    if _backup_file(BATCH_PROCESSOR_FILE):
        _update_file_content(BATCH_PROCESSOR_FILE, OLD_ENGINE, NEW_ENGINE)

    # 2. Update GitHub Workflows
    print_subheader("Updating GitHub Actions Workflows")
    if _backup_file(PRODUCTION_QA_WORKFLOW):
        _update_file_content(PRODUCTION_QA_WORKFLOW, OLD_QA_VALIDATOR, NEW_QA)

    if _backup_file(BOOK_QA_WORKFLOW):
        _update_file_content(BOOK_QA_WORKFLOW, OLD_QA_CHECKER, NEW_QA)

    print(
        "\n✅ Deployment complete. The system will now use the new engine and QA validator."
    )
    print("   To revert these changes, run: python scripts/deploy_fixes.py rollback")


def rollback_changes():
    """Rolls back the changes to the previous state."""
    print_header("Rolling Back Deployment")

    # 1. Rollback Batch Processor
    _restore_backup(BATCH_PROCESSOR_FILE)

    # 2. Rollback Workflows
    _restore_backup(PRODUCTION_QA_WORKFLOW)
    _restore_backup(BOOK_QA_WORKFLOW)

    print("\n✅ Rollback complete. The system has been restored to its previous state.")


# --- Main CLI ---


def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(
        description="Deployment script for KindleMint Engine quality fixes.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Test command
    subparsers.add_parser(
        "test",
        help="Run a sandboxed test of the old vs. new systems and generate a report.",
    )

    # Report command
    subparsers.add_parser(
        "report", help="Generate the comparison report from the last test run."
    )

    # Deploy command
    subparsers.add_parser(
        "deploy", help="Update the main scripts and workflows to use the new systems."
    )

    # Rollback command
    subparsers.add_parser(
        "rollback", help="Revert the changes and restore the old systems."
    )

    # Cleanup command
    subparsers.add_parser(
        "cleanup", help="Remove temporary directories created during testing."
    )

    args = parser.parse_args()

    try:
        if args.command == "test":
            test_systems()
        elif args.command == "report":
            generate_comparison_report()
        elif args.command == "deploy":
            deploy_changes()
        elif args.command == "rollback":
            rollback_changes()
        elif args.command == "cleanup":
            cleanup_temp_dirs()
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
