#!/usr/bin/env python3
"""
Project Cleanup Tool - Uses Code Hygiene Orchestrator to analyze and clean project structure
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from agents.code_hygiene_orchestrator import CodeHygieneOrchestrator
except ImportError:
    print("Error: Could not import CodeHygieneOrchestrator")
    sys.exit(1)


def analyze_project(project_path: Path, deep_scan: bool = True):
    """Analyze project structure"""
    print(f"🔍 Analyzing project structure at: {project_path}")
    print("=" * 60)

    orchestrator = CodeHygieneOrchestrator(project_path)
    result = orchestrator.analyze()

    if result["issues"]:
        # Print summary
        print(f"\n📊 Analysis Summary:")
        print(result["summary"])

        print(f"\n📁 Issues Found:")
        for category, issues in result["issues"].items():
            print(f"   - {category}: {len(issues)} issues")
            for issue in issues[:3]:  # Show first 3 issues per category
                print(f"     * {issue}")

        print(f"\n📊 Statistics:")
        for category, count in result["stats"].items():
            print(f"   - {category}: {count}")

        return result
    else:
        print("✅ No issues found!")
        return result


def clean_project(project_path: Path, dry_run: bool = True):
    """Clean project using hygiene orchestrator"""
    print(f"\n🧹 Cleaning project...")
    print("=" * 60)

    orchestrator = CodeHygieneOrchestrator(project_path)
    result = orchestrator.clean(dry_run=dry_run, interactive=False)

    if result["actions"]:
        print(f"\n✅ Applied {len(result['actions'])} fixes:")
        for action in result["actions"][:10]:  # Show first 10 actions
            print(f"   - {action}")
        if len(result["actions"]) > 10:
            print(f"   ... and {len(result['actions']) - 10} more")
    else:
        print("✅ No cleanup actions needed!")

    return result


def save_report(analysis: dict, output_file: str):
    """Save detailed report"""
    from datetime import datetime
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_path": str(Path.cwd()),
        "analysis": analysis,
        "version": "1.0.0",
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and clean up project structure using Code Hygiene Orchestrator"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Project path to analyze (default: current directory)",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Run cleanup after analysis"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be cleaned without making changes"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="hygiene_report.json",
        help="Output file for detailed report",
    )

    args = parser.parse_args()

    project_path = Path(args.path).resolve()
    if not project_path.exists():
        print(f"❌ Path does not exist: {project_path}")
        return

    print(f"🧹 Code Hygiene Orchestrator")
    print(f"   Project: {project_path}")
    print("=" * 60)

    # Run analysis
    analysis = analyze_project(project_path)
    if not analysis:
        return

    # Run cleanup if requested
    if args.clean:
        clean_project(project_path, dry_run=args.dry_run)

    # Save report
    save_report(analysis, args.output)

    print(f"\n✅ Analysis complete!")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the hygiene report: {args.output}")
    print(f"   2. Run with --clean to apply fixes")
    print(f"   3. Use --dry-run to preview changes first")


if __name__ == "__main__":
    main()
