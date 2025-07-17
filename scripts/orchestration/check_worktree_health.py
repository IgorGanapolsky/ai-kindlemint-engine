#!/usr/bin/env python3
"""
Check health and usage of Git worktrees
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def run_command(cmd: str) -> str:
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_worktree_info() -> List[Dict]:
    """Get information about all worktrees"""
    output = run_command("git worktree list --porcelain")
    worktrees = []
    current = {}
    
    for line in output.split('\n'):
        if line.startswith('worktree'):
            if current:
                worktrees.append(current)
            current = {'path': line.split()[1]}
        elif line.startswith('HEAD'):
            current['commit'] = line.split()[1]
        elif line.startswith('branch'):
            current['branch'] = line.split()[1].replace('refs/heads/', '')
    
    if current:
        worktrees.append(current)
    
    return worktrees

def check_worktree_status(worktree: Dict) -> Dict:
    """Check detailed status of a worktree"""
    path = Path(worktree['path'])
    
    # Get last commit date
    cmd = f"cd {path} && git log -1 --format=%cd --date=relative 2>/dev/null"
    last_commit = run_command(cmd) or "unknown"
    
    # Check if behind main
    cmd = f"cd {path} && git rev-list --count HEAD..origin/main 2>/dev/null"
    behind_count = run_command(cmd) or "0"
    
    # Check for uncommitted changes
    cmd = f"cd {path} && git status --porcelain 2>/dev/null | wc -l"
    uncommitted = int(run_command(cmd) or "0")
    
    # Get last modified file
    cmd = f"find {path} -type f -name '*.py' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1"
    run_command(cmd)
    
    return {
        **worktree,
        'last_commit': last_commit,
        'behind_main': int(behind_count),
        'uncommitted_changes': uncommitted,
        'status': 'stale' if int(behind_count) > 10 else 'current',
        'health': 'good' if int(behind_count) < 10 and uncommitted == 0 else 'needs_attention'
    }

def generate_report():
    """Generate worktree health report"""
    worktrees = get_worktree_info()
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_worktrees': len(worktrees),
        'worktrees': []
    }
    
    print("🔍 Git Worktree Health Check")
    print("=" * 80)
    
    for wt in worktrees:
        status = check_worktree_status(wt)
        report['worktrees'].append(status)
        
        # Color coding
        health_icon = "✅" if status['health'] == 'good' else "⚠️"
        
        print(f"\n{health_icon} {Path(status['path']).name}")
        print(f"   Branch: {status['branch']}")
        print(f"   Last commit: {status['last_commit']}")
        print(f"   Behind main: {status['behind_main']} commits")
        print(f"   Uncommitted: {status['uncommitted_changes']} files")
    
    # Summary
    healthy = sum(1 for wt in report['worktrees'] if wt['health'] == 'good')
    stale = sum(1 for wt in report['worktrees'] if wt['status'] == 'stale')
    
    print("\n" + "=" * 80)
    print("📊 Summary:")
    print(f"   Total worktrees: {len(worktrees)}")
    print(f"   Healthy: {healthy}")
    print(f"   Need attention: {len(worktrees) - healthy}")
    print(f"   Stale (>10 commits behind): {stale}")
    
    # Save report
    report_path = Path("reports/orchestration/worktree_health.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    # Recommendations
    if stale > 0:
        print("\n⚡ Recommended Actions:")
        print("   1. Update stale worktrees: git pull origin main")
        print("   2. Clean up unused worktrees: git worktree prune")
        print("   3. Commit or stash uncommitted changes")

if __name__ == "__main__":
    generate_report()