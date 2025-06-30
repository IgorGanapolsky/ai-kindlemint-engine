#!/usr/bin/env python3
"""
Claude API Cost Tracker
Tracks Claude API usage costs and associates them with git commits
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ClaudeCostTracker:
    """Track Claude API costs per commit"""

    # Claude API pricing (as of 2025)
    CLAUDE_PRICING = {
        # per million tokens
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-2.1": {"input": 8.00, "output": 24.00},
        "claude-2.0": {"input": 8.00, "output": 24.00},
        "claude-instant": {"input": 0.80, "output": 2.40},
    }

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.commit_costs_file = self.repo_path / "commit_costs.json"
        self.last_commit_cost_file = self.repo_path / "last_commit_cost.json"
        self.usage_log_file = self.repo_path / ".claude_usage.log"

    def load_commit_costs(self) -> Dict:
        """Load existing commit costs data"""
        if self.commit_costs_file.exists():
            try:
                with open(self.commit_costs_file, "r") as f:
                    return json.load(f)
            except BaseException:
                pass

        return {
            "total_cost": 0.0,
            "commits": [],
            "first_tracked": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

    def load_last_commit_cost(self) -> Dict:
        """Load last commit cost data"""
        if self.last_commit_cost_file.exists():
            try:
                with open(self.last_commit_cost_file, "r") as f:
                    return json.load(f)
            except BaseException:
                pass

        return {
            "last_analysis": datetime.now().isoformat(),
            "full_repo_cost": 0.0,
            "worktree_cost": 0.0,
            "savings_potential": 0.0,
        }

    def get_current_commit_hash(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except BaseException:
            return None

    def get_changed_files(self) -> List[str]:
        """Get list of files changed in current commit"""
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            staged_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # Get modified files
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            modified_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            return list(set(staged_files + modified_files))
        except BaseException:
            return []

    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Claude uses a similar tokenization to GPT models
        # Rough estimate: 1 token ≈ 4 characters or 0.75 words
        words = len(text.split())
        chars = len(text)
        return max(int(chars / 4), int(words / 0.75))

    def analyze_file_complexity(self, file_path: str) -> Dict:
        """Analyze file to estimate Claude processing complexity"""
        full_path = self.repo_path / file_path

        if not full_path.exists():
            return {"tokens": 0, "complexity": "low"}

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tokens = self.estimate_token_count(content)

            # Determine complexity based on file type and content
            complexity = "low"
            if file_path.endswith((".py", ".js", ".ts", ".java", ".cpp")):
                # Count complex patterns
                complex_patterns = [
                    r"class\s+\w+",  # Classes
                    r"def\s+\w+\s*\(",  # Functions
                    r"async\s+",  # Async code
                    r"import\s+",  # Dependencies
                    r"try\s*:",  # Exception handling
                ]

                complexity_score = sum(
                    len(re.findall(pattern, content)) for pattern in complex_patterns
                )

                if complexity_score > 50:
                    complexity = "high"
                elif complexity_score > 20:
                    complexity = "medium"

            return {
                "tokens": tokens,
                "complexity": complexity,
                "lines": len(content.split("\n")),
            }
        except BaseException:
            return {"tokens": 0, "complexity": "low", "lines": 0}

    def calculate_file_cost(
        self, file_analysis: Dict, model: str = "claude-3-sonnet"
    ) -> float:
        """Calculate estimated cost for processing a file"""
        if model not in self.CLAUDE_PRICING:
            model = "claude-3-sonnet"  # Default model

        pricing = self.CLAUDE_PRICING[model]
        tokens = file_analysis["tokens"]

        # Estimate input/output ratio based on complexity
        complexity_multipliers = {
            "low": 1.5,  # Simple files generate less output
            "medium": 2.5,  # Medium complexity
            "high": 4.0,  # Complex files generate more analysis/code
        }

        output_multiplier = complexity_multipliers.get(
            file_analysis["complexity"], 2.0)

        # Calculate costs (convert from per million to actual tokens)
        input_cost = (tokens * pricing["input"]) / 1_000_000
        output_cost = (tokens * output_multiplier *
                       pricing["output"]) / 1_000_000

        return input_cost + output_cost

    def analyze_commit_cost(
        self, changed_files: List[str], model: str = "claude-3-sonnet"
    ) -> Dict:
        """Analyze the cost of processing changed files in a commit"""
        total_tokens = 0
        total_cost = 0.0
        file_analyses = []

        for file_path in changed_files:
            # Skip hidden files
            if file_path and not file_path.startswith("."):
                analysis = self.analyze_file_complexity(file_path)
                cost = self.calculate_file_cost(analysis, model)

                total_tokens += analysis["tokens"]
                total_cost += cost

                file_analyses.append(
                    {
                        "file": file_path,
                        "tokens": analysis["tokens"],
                        "complexity": analysis["complexity"],
                        "lines": analysis.get("lines", 0),
                        "cost": cost,
                    }
                )

        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "file_count": len(file_analyses),
            "files": file_analyses,
            "model": model,
        }

    def update_commit_costs(
        self, commit_analysis: Dict, commit_message: str = ""
    ) -> None:
        """Update commit costs file with new commit data"""
        commit_hash = self.get_current_commit_hash()
        if not commit_hash:
            return

        # Load existing data
        commit_costs = self.load_commit_costs()

        # Add new commit data
        commit_data = {
            "hash": commit_hash[:8],
            "timestamp": datetime.now().isoformat(),
            "message": commit_message or "No message",
            "cost": commit_analysis["total_cost"],
            "tokens": commit_analysis["total_tokens"],
            "files_changed": commit_analysis["file_count"],
            "model": commit_analysis["model"],
        }

        commit_costs["commits"].append(commit_data)
        commit_costs["total_cost"] += commit_analysis["total_cost"]
        commit_costs["last_updated"] = datetime.now().isoformat()

        # Keep only last 100 commits
        if len(commit_costs["commits"]) > 100:
            commit_costs["commits"] = commit_costs["commits"][-100:]

        # Save updated data
        with open(self.commit_costs_file, "w") as f:
            json.dump(commit_costs, f, indent=2)

    def update_last_commit_cost(self, commit_analysis: Dict) -> None:
        """Update last commit cost file"""
        # Calculate repository-wide cost estimation
        all_files = []
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            all_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
        except BaseException:
            pass

        # Quick estimation for full repo
        full_repo_tokens = 0
        # Limit to first 1000 files for performance
        for file_path in all_files[:1000]:
            if file_path and file_path.endswith(
                (".py", ".js", ".ts", ".java", ".cpp", ".md")
            ):
                analysis = self.analyze_file_complexity(file_path)
                full_repo_tokens += analysis["tokens"]

        full_repo_cost = (
            full_repo_tokens * 18.0
        ) / 1_000_000  # Average pricing estimate

        last_commit_data = {
            "last_analysis": datetime.now().isoformat(),
            "full_repo_cost": full_repo_cost,
            "worktree_cost": commit_analysis["total_cost"],
            "savings_potential": full_repo_cost - commit_analysis["total_cost"],
            "commit_details": {
                "files_analyzed": commit_analysis["file_count"],
                "total_tokens": commit_analysis["total_tokens"],
                "model_used": commit_analysis["model"],
            },
        }

        with open(self.last_commit_cost_file, "w") as f:
            json.dump(last_commit_data, f, indent=2)

    def track_commit(
        self, commit_message: str = "", model: str = "claude-3-sonnet"
    ) -> Dict:
        """Main method to track costs for current commit"""
        changed_files = self.get_changed_files()

        if not changed_files:
            return {"status": "no_changes", "cost": 0.0}

        # Analyze commit cost
        commit_analysis = self.analyze_commit_cost(changed_files, model)

        # Update tracking files
        self.update_commit_costs(commit_analysis, commit_message)
        self.update_last_commit_cost(commit_analysis)

        return {
            "status": "tracked",
            "cost": commit_analysis["total_cost"],
            "tokens": commit_analysis["total_tokens"],
            "files": commit_analysis["file_count"],
        }

    def get_cost_summary(self, days: int = 30) -> Dict:
        """Get cost summary for the last N days"""
        commit_costs = self.load_commit_costs()

        if not commit_costs["commits"]:
            return {"error": "No commits tracked yet"}

        # Filter commits by date
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_commits = [
            c
            for c in commit_costs["commits"]
            if datetime.fromisoformat(c["timestamp"]).timestamp() > cutoff_date
        ]

        if not recent_commits:
            return {"error": f"No commits in the last {days} days"}

        total_cost = sum(c["cost"] for c in recent_commits)
        total_tokens = sum(c["tokens"] for c in recent_commits)

        return {
            "period_days": days,
            "commit_count": len(recent_commits),
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "average_cost_per_commit": total_cost / len(recent_commits),
            "most_expensive_commit": (
                max(recent_commits,
                    key=lambda c: c["cost"]) if recent_commits else None
            ),
        }


# Export the main class
__all__ = ["ClaudeCostTracker"]


# CLI interface
if __name__ == "__main__":
    import sys

    tracker = ClaudeCostTracker()

    if len(sys.argv) < 2:
        print("Usage: python claude_cost_tracker.py [track|summary|init]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "track":
        # Track current changes
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        result = tracker.track_commit(message)

        if result["status"] == "tracked":
            print(f"✅ Tracked commit cost: ${result['cost']:.4f}")
            print(f"   Tokens: {result['tokens']:,}")
            print(f"   Files: {result['files']}")
        else:
            print("ℹ️  No changes to track")

    elif command == "summary":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        summary = tracker.get_cost_summary(days)

        if "error" in summary:
            print(summary["error"])
        else:
            print(f"\n📊 Claude Cost Summary ({days} days)")
            print("=" * 40)
            print(f"Commits tracked: {summary['commit_count']}")
            print(f"Total cost: ${summary['total_cost']:.2f}")
            print(f"Total tokens: {summary['total_tokens']:,}")
            print(f"Avg per commit: ${summary['average_cost_per_commit']:.4f}")

            if summary["most_expensive_commit"]:
                c = summary["most_expensive_commit"]
                print(f"\nMost expensive commit:")
                print(f"  {c['hash']} - ${c['cost']:.4f}")
                print(f"  {c['message'][:50]}...")

    elif command == "init":
        # Initialize tracking files
        tracker.track_commit("Initial Claude cost tracking setup")
        print("✅ Initialized Claude cost tracking files")
