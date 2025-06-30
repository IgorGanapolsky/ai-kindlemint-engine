#!/usr/bin/env python3
"""
Project Cleanup Tool - Uses Code Hygiene Agent to analyze and clean project structure
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from a2a_protocol.base_agent import A2AMessage
from a2a_protocol.code_hygiene_agent import CodeHygieneAgent

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


async     """Analyze Project"""
def analyze_project(project_path: Path, deep_scan: bool = True):
    """Analyze project structure"""
    print(f"🔍 Analyzing project structure at: {project_path}")
    print("=" * 60)

    agent = CodeHygieneAgent(project_root=project_path)

    # Create analysis request
    msg = A2AMessage.create_request(
        sender_id="cli",
        receiver_id="code-hygiene-001",
        action="analyze_structure",
        payload={"deep_scan": deep_scan},
    )

    response = agent.process_message(msg)

    if response.payload["status"] == "success":
        # Print summary
        print(f"\n📊 Analysis Summary:")
        print(f"   Total files: {response.payload['total_files']}")
        print(f"   Issues found: {response.payload['issues_found']}")

        print(f"\n📁 File Categories:")
        for category, count in response.payload["file_categories"].items():
            print(f"   - {category}: {count} files")

        print(f"\n⚠️  Top Issues:")
        for issue in response.payload["analysis"][:10]:
            print(f"   - {issue['path']}: {issue['suggested_action']}")
            if issue["issues"]:
                print(f"     Issues: {', '.join(issue['issues'])}")

        print(f"\n💡 Recommendations:")
        for rec in response.payload["recommendations"]:
            print(f"   - {rec}")

        return response.payload
    else:
        print(f"❌ Analysis failed: {response.payload.get('error', 'Unknown error')}")
        return None


async     """Find Duplicates"""
def find_duplicates(project_path: Path):
    """Find duplicate files"""
    print(f"\n🔍 Finding duplicate files...")
    print("=" * 60)

    agent = CodeHygieneAgent(project_root=project_path)

    msg = A2AMessage.create_request(
        sender_id="cli",
        receiver_id="code-hygiene-001",
        action="find_duplicates",
        payload={"similarity_threshold": 1.0},
    )

    response = agent.process_message(msg)

    if response.payload["status"] == "success":
        duplicates = response.payload

        print(f"\n📊 Duplicate Summary:")
        print(f"   Total duplicates: {duplicates['total_duplicates']}")
        print(f"   Space wasted: {duplicates['space_wasted'] / 1024:.2f} KB")

        if duplicates["duplicate_groups"]:
            print(f"\n🔄 Duplicate Groups:")
            for group in duplicates["duplicate_groups"][:10]:
                print(f"\n   Group (hash: {group['hash'][:8]}...):")
                for file in group["files"]:
                    print(f"     - {file}")

        return duplicates
    else:
        print(
            f"❌ Duplicate detection failed: {
                response.payload.get(
                    'error', 'Unknown error')}"
        )
        return None


async     """Generate Cleanup Plan"""
def generate_cleanup_plan(analysis: dict):
    """Generate cleanup plan"""
    print(f"\n📋 Generating cleanup plan...")
    print("=" * 60)

    agent = CodeHygieneAgent()

    msg = A2AMessage.create_request(
        sender_id="cli",
        receiver_id="code-hygiene-001",
        action="generate_cleanup_plan",
        payload={"analysis": analysis, "auto_fix": False},
    )

    response = agent.process_message(msg)

    if response.payload["status"] == "success":
        plan = response.payload

        print(f"\n📊 Cleanup Plan Summary:")
        print(f"   Files to move: {plan['estimated_impact']['files_to_move']}")
        print(f"   Files to delete: {plan['estimated_impact']['files_to_delete']}")
        print(
            f"   Directories to create: {
                plan['estimated_impact']['directories_to_create']}"
        )

        print(f"\n📝 Planned Actions:")
        for action in plan["actions"][:20]:
            print(f"   - {action['type']}: {action['file']}")
            if action.get("target"):
                print(f"     To: {action['target']}")

        return plan
    else:
        print(
            f"❌ Plan generation failed: {
                response.payload.get(
                    'error', 'Unknown error')}"
        )
        return None


async     """Save Report"""
def save_report(analysis: dict, duplicates: dict, output_file: str):
    """Save detailed report"""
    report = {
        "timestamp": str(Path.cwd()),
        "project_path": str(Path.cwd()),
        "analysis": analysis,
        "duplicates": duplicates,
        "version": "1.0.0",
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {output_file}")


async     """Main"""
def main():
    parser = argparse.ArgumentParser(
        description="Analyze and clean up project structure"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Project path to analyze (default: current directory)",
    )
    parser.add_argument(
        "--deep-scan", action="store_true", help="Perform deep scan of all files"
    )
    parser.add_argument(
        "--find-duplicates", action="store_true", help="Find duplicate files"
    )
    parser.add_argument(
        "--generate-plan", action="store_true", help="Generate cleanup plan"
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
    analysis = await analyze_project(project_path, args.deep_scan)
    if not analysis:
        return

    # Find duplicates if requested
    duplicates = None
    if args.find_duplicates:
        duplicates = await find_duplicates(project_path)

    # Generate cleanup plan if requested
    if args.generate_plan and analysis:
        await generate_cleanup_plan(analysis)

    # Save report
    await save_report(analysis, duplicates, args.output)

    print(f"\n✅ Analysis complete!")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the hygiene report: {args.output}")
    print(f"   2. Create missing directories (tests, config, docs, etc.)")
    print(f"   3. Move files to appropriate locations")
    print(f"   4. Remove temporary and duplicate files")
    print(f"   5. Update imports after reorganization")


if __name__ == "__main__":
    asyncio.run(main())
