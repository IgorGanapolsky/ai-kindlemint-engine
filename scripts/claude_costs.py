#!/usr/bin/env python3
"""
Claude Costs - User-friendly interface for Claude cost tracking
Integrates with claude-flow command structure
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from kindlemint.utils.cost_tracker import ClaudeCostTracker
from security import safe_command


def format_currency(amount: float) -> str:
    """Format currency with proper precision"""
    if amount < 0.01:
        return f"${amount:.6f}"
    elif amount < 1.0:
        return f"${amount:.4f}"
    else:
        return f"${amount:.2f}"

    """Main"""


def main():
    parser = argparse.ArgumentParser(
        description="Claude API Cost Tracking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude_costs init                    # Initialize cost tracking
  claude_costs status                  # Show current cost status
  claude_costs track                   # Track current changes
  claude_costs summary --days 7        # Show 7-day summary
  claude_costs details --last 5        # Show last 5 commits
  claude_costs export costs.csv        # Export costs to CSV
  claude_costs badge                   # Update cost badge in README
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize cost tracking")

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Show current cost status")

    # Track command
    track_parser = subparsers.add_parser(
        "track", help="Track current commit costs")
    track_parser.add_argument(
        "--model",
        default="claude-3-sonnet",
        choices=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        help="Claude model to use for estimation",
    )
    track_parser.add_argument("--message", help="Commit message")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show cost summary")
    summary_parser.add_argument(
        "--days", type=int, default=30, help="Number of days to summarize"
    )

    # Details command
    details_parser = subparsers.add_parser(
        "details", help="Show detailed commit costs")
    details_parser.add_argument(
        "--last", type=int, default=10, help="Number of commits to show"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export cost data")
    export_parser.add_argument("output", help="Output file (csv or json)")

    # Badge command
    badge_parser = subparsers.add_parser(
        "badge", help="Update cost badge in README")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    tracker = ClaudeCostTracker()

    if args.command == "init":
        # Initialize tracking files
        result = tracker.track_commit("Initial Claude cost tracking setup")
        print("✅ Claude cost tracking initialized!")
        print(f"   Created: commit_costs.json")
        print(f"   Created: last_commit_cost.json")

    elif args.command == "status":
        # Show current status
        commit_costs = tracker.load_commit_costs()
        last_cost = tracker.load_last_commit_cost()

        print("\n📊 Claude Cost Tracking Status")
        print("=" * 50)

        if commit_costs.get("commits"):
            print(
                f"Total tracked cost: {format_currency(commit_costs['total_cost'])}")
            print(f"Commits tracked: {len(commit_costs['commits'])}")
            print(f"First tracked: {commit_costs['first_tracked'][:10]}")
            print(f"Last updated: {commit_costs['last_updated'][:19]}")

            # Show last commit
            last_commit = commit_costs["commits"][-1]
            print(f"\nLast commit:")
            print(f"  Hash: {last_commit['hash']}")
            print(f"  Cost: {format_currency(last_commit['cost'])}")
            print(f"  Files: {last_commit['files_changed']}")
            print(f"  Message: {last_commit['message'][:50]}...")
        else:
            print("No commits tracked yet. Run 'claude_costs init' to start.")

        # Repository analysis
        print(f"\nRepository Analysis:")
        print(
            f"  Full repo cost estimate: {format_currency(last_cost['full_repo_cost'])}"
        )
        print(
            f"  Last worktree cost: {format_currency(last_cost['worktree_cost'])}")
        print(
            f"  Savings potential: {format_currency(last_cost['savings_potential'])}")

    elif args.command == "track":
        # Track current changes
        message = args.message or ""
        result = tracker.track_commit(message, args.model)

        if result["status"] == "tracked":
            print(f"✅ Tracked commit cost: {format_currency(result['cost'])}")
            print(f"   Model: {args.model}")
            print(f"   Tokens: {result['tokens']:,}")
            print(f"   Files: {result['files']}")
        else:
            print("ℹ️  No changes to track")

    elif args.command == "summary":
        # Show summary
        summary = tracker.get_cost_summary(args.days)

        if "error" in summary:
            print(f"❌ {summary['error']}")
        else:
            print(f"\n📊 Claude Cost Summary ({args.days} days)")
            print("=" * 50)
            print(f"Commits tracked: {summary['commit_count']}")
            print(f"Total cost: {format_currency(summary['total_cost'])}")
            print(f"Total tokens: {summary['total_tokens']:,}")
            print(
                f"Average per commit: {format_currency(
                    summary['average_cost_per_commit'])}"
            )

            if summary["most_expensive_commit"]:
                c = summary["most_expensive_commit"]
                print(f"\nMost expensive commit:")
                print(f"  {c['hash']} - {format_currency(c['cost'])}")
                print(
                    f"  Files: {c['files_changed']}, Tokens: {c['tokens']:,}")
                print(f"  {c['message'][:60]}...")

    elif args.command == "details":
        # Show detailed commit history
        commit_costs = tracker.load_commit_costs()

        if not commit_costs.get("commits"):
            print("No commits tracked yet.")
            return

        commits = commit_costs["commits"][-args.last:]

        print(f"\n📋 Last {len(commits)} Commits with Claude Costs")
        print("=" * 80)
        print(
            f"{'Hash': < 10} {'Date': < 20} {'Cost': < 12} {
                'Files': < 8} {'Tokens': < 10} Message"
        )
        print("-" * 80)

        for commit in commits:
            date = datetime.fromisoformat(commit["timestamp"]).strftime(
                "%Y-%m-%d %H:%M"
            )
            cost = format_currency(commit["cost"])
            msg = (
                commit["message"][:30] + "..."
                if len(commit["message"]) > 30
                else commit["message"]
            )

            print(
                f"{commit['hash']: < 10} {date: < 20} {
                    cost: < 12} {commit['files_changed']: < 8} "
                f"{commit['tokens']:<10,} {msg}"
            )

        print("-" * 80)
        total = sum(c["cost"] for c in commits)
        print(f"{'Total':<10} {'':<20} {format_currency(total):<12}")

    elif args.command == "export":
        # Export data
        output_path = Path(args.output)
        commit_costs = tracker.load_commit_costs()

        if output_path.suffix == ".csv":
            # Export as CSV
            import csv

            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Hash", "Timestamp", "Cost", "Tokens",
                        "Files", "Model", "Message"]
                )

                for commit in commit_costs.get("commits", []):
                    writer.writerow(
                        [
                            commit["hash"],
                            commit["timestamp"],
                            commit["cost"],
                            commit["tokens"],
                            commit["files_changed"],
                            commit.get("model", "claude-3-sonnet"),
                            commit["message"],
                        ]
                    )

            print(
                f"✅ Exported {len(commit_costs.get('commits', []))
                              } commits to {output_path}"
            )

        elif output_path.suffix == ".json":
            # Export as JSON
            with open(output_path, "w") as f:
                json.dump(commit_costs, f, indent=2)

            print(f"✅ Exported cost data to {output_path}")

        else:
            print(f"❌ Unsupported export format. Use .csv or .json")

    elif args.command == "badge":
        # Update cost badges in README with comprehensive analytics
        import subprocess
        import sys
        from pathlib import Path

        script_dir = Path(__file__).parent
        badge_script = script_dir / "generate_cost_badges.py"

        try:
            result = safe_command.run(subprocess.run, [sys.executable, str(badge_script)],
                                    capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Badge generation failed: {e.stderr}")


if __name__ == "__main__":
    main()
