#!/usr/bin/env python3
"""
Automated Code Hygiene Cleanup Script
Run this to clean up the project automatically
"""

import argparse
import sys
from pathlib import Path

from src.kindlemint.agents.code_hygiene_orchestrator import CodeHygieneOrchestrator

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="Clean up project hygiene issues")
    parser.add_argument(
        "--analyze", action="store_true", help="Only analyze, don't clean"
    )
    parser.add_argument(
        "--commit-plan", action="store_true", help="Generate commit plan"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Execute cleanup operations"
    )
    parser.add_argument(
        "--list-files", action="store_true", help="List all untracked files"
    )

    args = parser.parse_args()

    orchestrator = CodeHygieneOrchestrator()

    print("🧹 Code Hygiene Cleanup Tool")
    print("=" * 50)

    # Always analyze first
    report = orchestrator.analyze_project_hygiene()

    print(f"\n📊 Current Status:")
    print(f"   Hygiene Score: {report['metrics']['hygiene_score']:.1f}/100")
    print(f"   Untracked Files: {report['untracked_files']}")
    print(
        f"   Organization Score: {report['metrics']['organization_score']:.1f}%")

    # Show file categories
    print("\n📂 File Categories:")
    for category, count in report["categorized_files"].items():
        if count > 0:
            print(f"   {category}: {count} files")

    if args.list_files:
        print("\n📄 Untracked Files by Category:")
        categorized = orchestrator._categorize_files(
            orchestrator._get_untracked_files()
        )

        for category, files in categorized.items():
            if files:
                print(f"\n{category.value.upper()}:")
                for f in sorted(files)[:10]:  # Show first 10 of each category
                    print(f"   - {f}")
                if len(files) > 10:
                    print(f"   ... and {len(files) - 10} more")

    if args.commit_plan:
        print("\n📝 Suggested Commit Plan:")
        commit_groups = orchestrator.generate_commit_plan()

        for i, group in enumerate(commit_groups, 1):
            print(f"\n{i}. {group['message']}")
            print(f"   Files: {len(group['files'])}")
            for f in group["files"][:5]:  # Show first 5 files
                print(f"   - {f}")
            if len(group["files"]) > 5:
                print(f"   ... and {len(group['files']) - 5} more")

    if args.clean:
        print("\n🔧 Executing Cleanup...")
        results = orchestrator.execute_cleanup(auto_confirm=True)

        print(f"\n✅ Cleanup Results:")
        for op in results["operations"]:
            print(f"   - {op['action']}: {op['status']}")

    # Save updated report
    report_path = orchestrator.save_report()
    print(f"\n📄 Report saved to: {report_path}")


if __name__ == "__main__":
    main()
