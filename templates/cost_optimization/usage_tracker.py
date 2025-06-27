#!/usr/bin/env python3
"""
Claude Code Usage Tracker
Monitors and optimizes Claude Code credit usage patterns
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ClaudeSession:
    start_time: datetime
    end_time: Optional[datetime]
    task_type: str
    estimated_complexity: str
    actual_duration: Optional[float]
    lines_changed: int
    files_modified: int
    git_commits: int
    estimated_cost: float
    session_notes: str


class ClaudeCodeUsageTracker:
    """Track Claude Code usage for cost optimization"""

    def __init__(self, data_file: str = ".claude_usage_data.json"):
        self.data_file = Path(data_file)
        self.sessions: List[ClaudeSession] = []
        self.current_session: Optional[ClaudeSession] = None
        self.load_data()

    def load_data(self):
        """Load existing usage data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    for session_data in data.get("sessions", []):
                        session = ClaudeSession(**session_data)
                        session.start_time = datetime.fromisoformat(session.start_time)
                        if session.end_time:
                            session.end_time = datetime.fromisoformat(session.end_time)
                        self.sessions.append(session)
            except Exception as e:
                print(f"Warning: Could not load usage data: {e}")

    def save_data(self):
        """Save usage data to file"""
        data = {"sessions": [], "last_updated": datetime.now().isoformat()}

        for session in self.sessions:
            session_dict = asdict(session)
            session_dict["start_time"] = session.start_time.isoformat()
            if session.end_time:
                session_dict["end_time"] = session.end_time.isoformat()
            data["sessions"].append(session_dict)

        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def start_session(self, task_type: str, estimated_complexity: str, notes: str = ""):
        """Start tracking a new Claude Code session"""
        if self.current_session and not self.current_session.end_time:
            print("Warning: Previous session not ended. Ending it now.")
            self.end_session(0, 0, 0, 0)

        self.current_session = ClaudeSession(
            start_time=datetime.now(),
            end_time=None,
            task_type=task_type,
            estimated_complexity=estimated_complexity,
            actual_duration=None,
            lines_changed=0,
            files_modified=0,
            git_commits=0,
            estimated_cost=0.0,
            session_notes=notes,
        )

        print(f"🚀 Started Claude Code session: {task_type} ({estimated_complexity})")
        return self.current_session

    def end_session(
        self,
        lines_changed: int,
        files_modified: int,
        git_commits: int,
        estimated_cost: float,
        notes: str = "",
    ):
        """End the current session with metrics"""
        if not self.current_session:
            print("Warning: No active session to end")
            return

        self.current_session.end_time = datetime.now()
        self.current_session.actual_duration = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds() / 60  # minutes

        self.current_session.lines_changed = lines_changed
        self.current_session.files_modified = files_modified
        self.current_session.git_commits = git_commits
        self.current_session.estimated_cost = estimated_cost

        if notes:
            self.current_session.session_notes += f" | {notes}"

        self.sessions.append(self.current_session)

        # Calculate efficiency metrics
        cost_per_line = estimated_cost / max(lines_changed, 1)
        cost_per_minute = estimated_cost / max(self.current_session.actual_duration, 1)

        print(f"✅ Session completed:")
        print(f"   Duration: {self.current_session.actual_duration:.1f} minutes")
        print(f"   Lines changed: {lines_changed}")
        print(f"   Cost per line: ${cost_per_line:.4f}")
        print(f"   Cost per minute: ${cost_per_minute:.4f}")

        self.current_session = None
        self.save_data()

    def get_usage_report(self, days: int = 30) -> Dict:
        """Generate usage report for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_sessions = [
            s for s in self.sessions if s.start_time >= cutoff_date and s.end_time
        ]

        if not recent_sessions:
            return {"error": f"No completed sessions in the last {days} days"}

        total_cost = sum(s.estimated_cost for s in recent_sessions)
        total_duration = sum(s.actual_duration for s in recent_sessions)
        total_lines = sum(s.lines_changed for s in recent_sessions)

        # Task type analysis
        task_costs = {}
        for session in recent_sessions:
            task_type = session.task_type
            if task_type not in task_costs:
                task_costs[task_type] = {"cost": 0, "count": 0, "lines": 0}
            task_costs[task_type]["cost"] += session.estimated_cost
            task_costs[task_type]["count"] += 1
            task_costs[task_type]["lines"] += session.lines_changed

        # Most expensive sessions
        expensive_sessions = sorted(
            recent_sessions, key=lambda s: s.estimated_cost, reverse=True
        )[:5]

        report = {
            "period_days": days,
            "total_sessions": len(recent_sessions),
            "total_cost": total_cost,
            "total_duration_hours": total_duration / 60,
            "total_lines_changed": total_lines,
            "avg_cost_per_session": total_cost / len(recent_sessions),
            "avg_cost_per_line": total_cost / max(total_lines, 1),
            "avg_cost_per_hour": total_cost / max(total_duration / 60, 1),
            "task_breakdown": task_costs,
            "most_expensive_sessions": [
                {
                    "task_type": s.task_type,
                    "cost": s.estimated_cost,
                    "duration_minutes": s.actual_duration,
                    "lines_changed": s.lines_changed,
                    "notes": s.session_notes,
                }
                for s in expensive_sessions
            ],
        }

        return report

    def print_usage_report(self, days: int = 30):
        """Print formatted usage report"""
        report = self.get_usage_report(days)

        if "error" in report:
            print(report["error"])
            return

        print(f"\n📊 Claude Code Usage Report ({days} days)")
        print("=" * 50)
        print(f"Total Sessions: {report['total_sessions']}")
        print(f"Total Cost: ${report['total_cost']:.2f}")
        print(f"Total Duration: {report['total_duration_hours']:.1f} hours")
        print(f"Lines Changed: {report['total_lines_changed']:,}")
        print()
        print(f"Avg Cost/Session: ${report['avg_cost_per_session']:.2f}")
        print(f"Avg Cost/Line: ${report['avg_cost_per_line']:.4f}")
        print(f"Avg Cost/Hour: ${report['avg_cost_per_hour']:.2f}")
        print()

        print("Task Type Breakdown:")
        for task_type, data in report["task_breakdown"].items():
            avg_cost = data["cost"] / data["count"]
            avg_lines = data["lines"] / data["count"]
            print(
                f"  {task_type:20} {data['count']:3} sessions  "
                f"${data['cost']:6.2f}  ${avg_cost:5.2f}/session  "
                f"{avg_lines:4.0f} lines/session"
            )

        print("\nMost Expensive Sessions:")
        for i, session in enumerate(report["most_expensive_sessions"], 1):
            print(
                f"  {i}. {session['task_type']} - ${session['cost']:.2f} "
                f"({session['duration_minutes']:.0f}min, {session['lines_changed']} lines)"
            )

    def suggest_optimizations(self) -> List[str]:
        """Suggest cost optimization strategies based on usage patterns"""
        suggestions = []
        report = self.get_usage_report(30)

        if "error" in report:
            return ["Not enough data for optimization suggestions"]

        # High cost per line
        if report["avg_cost_per_line"] > 0.10:
            suggestions.append(
                "🔴 High cost per line detected. Consider batching similar changes "
                "and planning more comprehensive sessions."
            )

        # Short expensive sessions
        expensive_short = [
            s
            for s in report["most_expensive_sessions"]
            if s["duration_minutes"] < 30 and s["cost"] > 5
        ]
        if expensive_short:
            suggestions.append(
                "🔴 Expensive short sessions detected. Plan longer, more focused "
                "sessions to improve cost efficiency."
            )

        # Task type recommendations
        task_breakdown = report["task_breakdown"]
        if "debugging" in task_breakdown and task_breakdown["debugging"]["cost"] > 20:
            suggestions.append(
                "💡 High debugging costs. Consider using Claude Chat for strategy "
                "planning before debugging sessions."
            )

        return suggestions or ["✅ Usage patterns look efficient!"]


# CLI Usage Example
if __name__ == "__main__":
    import sys

    tracker = ClaudeCodeUsageTracker()

    if len(sys.argv) < 2:
        print("Usage: python usage_tracker.py [start|end|report|suggestions]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        task_type = input("Task type: ") or "general"
        complexity = input("Complexity (low/medium/high): ") or "medium"
        notes = input("Session notes: ") or ""
        tracker.start_session(task_type, complexity, notes)

    elif command == "end":
        lines = int(input("Lines changed: ") or "0")
        files = int(input("Files modified: ") or "0")
        commits = int(input("Git commits: ") or "0")
        cost = float(input("Estimated cost ($): ") or "0")
        notes = input("Completion notes: ") or ""
        tracker.end_session(lines, files, commits, cost, notes)

    elif command == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        tracker.print_usage_report(days)

    elif command == "suggestions":
        suggestions = tracker.suggest_optimizations()
        print("\n💡 Cost Optimization Suggestions:")
        for suggestion in suggestions:
            print(f"   {suggestion}")

    else:
        print(f"Unknown command: {command}")
