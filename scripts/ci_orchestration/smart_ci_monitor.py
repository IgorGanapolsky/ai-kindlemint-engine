#!/usr/bin/env python3
"""
Smart CI Monitor - Detects and fixes CI failures automatically
Created by CTO to prevent orchestration death spirals
"""

import json
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timedelta


class SmartCIMonitor:
    def __init__(self):
        self.failure_threshold = 10  # Max failures per workflow per hour
        self.cascade_patterns = ["issue_comment",
                                 "pull_request_review", "workflow_run"]

    def get_recent_failures(self, hours=1):
        """Get failed runs from the last N hours"""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        cmd = f"""gh api /repos/IgorGanapolsky/ai-kindlemint-engine/actions/runs \
                  --paginate \
                  -q '.workflow_runs[] | select(.created_at > "{cutoff_time}" and .conclusion == "failure") | 
                  {{name: .name, event: .event, id: .id}}'"""

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            return [
                json.loads(line) for line in result.stdout.strip().split("\n") if line
            ]
        return []

    def analyze_failure_patterns(self, failures):
        """Group failures by workflow and event trigger"""
        patterns = defaultdict(lambda: defaultdict(int))

        for failure in failures:
            patterns[failure["name"]][failure["event"]] += 1

        return patterns

    def detect_cascades(self, patterns):
        """Detect cascade patterns in failures"""
        cascading_workflows = []

        for workflow, events in patterns.items():
            # Check if workflow is triggering cascades
            cascade_count = sum(
                events.get(trigger, 0) for trigger in self.cascade_patterns
            )

            if cascade_count >= self.failure_threshold:
                cascading_workflows.append(
                    {
                        "workflow": workflow,
                        "cascade_events": cascade_count,
                        "total_failures": sum(events.values()),
                    }
                )

        return sorted(
            cascading_workflows, key=lambda x: x["total_failures"], reverse=True
        )

    def auto_fix_cascades(self, cascading_workflows):
        """Automatically fix cascade issues"""
        fixes_applied = []

        for cascade in cascading_workflows:
            workflow_name = cascade["workflow"]
            print(f"🔧 Auto-fixing cascade in: {workflow_name}")

            # 1. Cancel running instances
            cmd = f"""gh run list --workflow "{workflow_name}" --status in_progress --json databaseId -q '.[].databaseId'"""
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True)

            if result.stdout:
                for run_id in result.stdout.strip().split("\n"):
                    subprocess.run(f"gh run cancel {run_id}", shell=True)
                    fixes_applied.append(f"Cancelled run {run_id}")

            # 2. Temporarily disable if extreme
            if cascade["total_failures"] > 20:
                subprocess.run(
                    f'gh workflow disable "{workflow_name}"', shell=True)
                fixes_applied.append(f"Disabled workflow: {workflow_name}")

                # Create issue for manual review
                issue_body = f"""## 🚨 Workflow Auto-Disabled Due to Cascade

**Workflow**: {workflow_name}
**Failures in last hour**: {cascade['total_failures']}
**Cascade events**: {cascade['cascade_events']}

### Auto-fix applied:
- Workflow temporarily disabled
- All running instances cancelled

### To re-enable:
```bash
gh workflow enable "{workflow_name}"
```

Please fix the root cause before re-enabling!
"""
                subprocess.run(
                    f"""gh issue create --title "CI: {workflow_name} auto-disabled" --body '{issue_body}' --label "ci-health,auto-generated" """,
                    shell=True,
                )

        return fixes_applied

    def generate_report(self):
        """Generate CI health report"""
        print("🏥 Smart CI Health Monitor")
        print("=" * 50)

        # Get recent failures
        failures = self.get_recent_failures()
        print(f"📊 Failures in last hour: {len(failures)}")

        if not failures:
            print("✅ CI is healthy - no recent failures")
            return

        # Analyze patterns
        patterns = self.analyze_failure_patterns(failures)
        cascades = self.detect_cascades(patterns)

        if cascades:
            print(f"\n🚨 Detected {len(cascades)} cascading workflows:")
            for cascade in cascades:
                print(
                    f"   - {cascade['workflow']}: {cascade['total_failures']} failures"
                )

            # Apply fixes
            print("\n🔧 Applying automatic fixes...")
            fixes = self.auto_fix_cascades(cascades)

            print(f"\n✅ Applied {len(fixes)} fixes:")
            for fix in fixes[:10]:  # Show first 10
                print(f"   - {fix}")
        else:
            print("✅ No cascade patterns detected")

        # Show current health
        print("\n📈 Current CI Status:")
        # More robust approach without shell pipeline
        try:
            workflow_list = subprocess.run(
                ["gh", "workflow", "list"], capture_output=True, text=True, check=False
            )
            if workflow_list.returncode == 0 and workflow_list.stdout:
                active_count = workflow_list.stdout.count("active")
            else:
                active_count = 0
        except Exception:
            active_count = 0

        print(f"   - Active workflows: {active_count}")
        print(f"   - Recent failures: {len(failures)}")
        print(f"   - Cascade risk: {'HIGH' if cascades else 'LOW'}")


if __name__ == "__main__":
    monitor = SmartCIMonitor()
    monitor.generate_report()
