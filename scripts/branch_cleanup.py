#!/usr/bin/env python3
"""
Branch Cleanup Orchestrator
Identifies and removes stale branches not associated with open PRs
"""
import json
import subprocess
from datetime import datetime


def run_command(cmd):
    """Run a command and return the output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def get_remote_branches():
    """Get all remote branches"""
    output = run_command("git branch -r | grep -v HEAD")
    if output:
        branches = []
        for line in output.split("\n"):
            if "origin/" in line:
                branch = line.strip().replace("origin/", "")
                branches.append(branch)
        return set(branches)
    return set()


def get_pr_branches():
    """Get branches with active PRs"""
    output = run_command("gh pr list --json headRefName --limit 100")
    if output:
        prs = json.loads(output)
        return {pr["headRefName"] for pr in prs}
    return set()


def get_branch_last_commit(branch):
    """Get the last commit date for a branch"""
    cmd = f"git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M:%S' origin/{branch} 2>/dev/null"
    output = run_command(cmd)
    if output:
        try:
            return datetime.strptime(output, "%Y-%m-%d %H:%M:%S")
        except:
            return None
    return None


def main():
    print("🧹 Branch Cleanup Analysis")
    print("=" * 50)

    # Get branches
    remote_branches = get_remote_branches()
    pr_branches = get_pr_branches()

    # Protected branches
    protected = {"main", "develop", "staging"}

    # Find stale branches
    stale_branches = remote_branches - pr_branches - protected

    print(f"\n📊 Branch Statistics:")
    print(f"   Total remote branches: {len(remote_branches)}")
    print(f"   Branches with active PRs: {len(pr_branches)}")
    print(f"   Protected branches: {len(protected)}")
    print(f"   Stale branches: {len(stale_branches)}")

    if stale_branches:
        print(f"\n🗑️  Stale branches to clean up:")
        for branch in sorted(stale_branches):
            last_commit = get_branch_last_commit(branch)
            age = ""
            if last_commit:
                days_old = (datetime.now() - last_commit).days
                age = f" (last commit: {days_old} days ago)"
            print(f"   - {branch}{age}")

        # Create cleanup commands
        print(f"\n🔧 Cleanup Commands:")
        print("   # Delete all stale remote branches:")
        for branch in sorted(stale_branches):
            print(f"   git push origin --delete {branch}")

        print(f"\n   # Or delete all at once:")
        branches_str = " ".join(
            f":{branch}" for branch in sorted(stale_branches))
        print(f"   git push origin {branches_str}")

    # Check local branches
    local_output = run_command("git branch | grep -v '\\*' | sed 's/^ *//'")
    if local_output:
        local_branches = set(local_output.split("\n"))
        local_stale = local_branches - pr_branches - protected

        if local_stale:
            print(f"\n🗑️  Local branches to clean up:")
            for branch in sorted(local_stale):
                print(f"   - {branch}")

            print(f"\n   # Delete local branches:")
            for branch in sorted(local_stale):
                print(f"   git branch -d {branch}")


if __name__ == "__main__":
    main()
