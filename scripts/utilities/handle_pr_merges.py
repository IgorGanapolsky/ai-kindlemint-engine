#!/usr/bin/env python3
"""
Handle PR merges using orchestration
"""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, check=True):
    """Run command and return output"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    
    if result.stdout:
        print(f"📄 Output: {result.stdout.strip()}")
    if result.stderr:
        print(f"⚠️  Error: {result.stderr.strip()}")
        
    if check and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        return False
    
    return result.returncode == 0

def handle_pr_171():
    """Handle PR 171 (Vercel removal)"""
    print("🔧 Handling PR #171 - Vercel removal")
    
    # Try squash merge to avoid conflicts
    success = run_cmd("gh pr merge 171 --squash --delete-branch", check=False)
    
    if success:
        print("✅ PR #171 merged successfully!")
        return True
    else:
        print("❌ Failed to merge PR #171")
        return False

def handle_pr_175():
    """Handle PR 175 (Visual QA)"""
    print("🔧 Handling PR #175 - Visual QA System")
    
    # Try squash merge
    success = run_cmd("gh pr merge 175 --squash --delete-branch", check=False)
    
    if success:
        print("✅ PR #175 merged successfully!")
        return True
    else:
        print("❌ Failed to merge PR #175")
        return False

def handle_pr_176():
    """Handle PR 176 (Alembic AI)"""
    print("🔧 Handling PR #176 - Alembic Causal AI")
    
    # Try squash merge
    success = run_cmd("gh pr merge 176 --squash --delete-branch", check=False)
    
    if success:
        print("✅ PR #176 merged successfully!")
        return True
    else:
        print("❌ Failed to merge PR #176")
        return False

def main():
    """Main orchestration"""
    print("🚀 Starting PR Merge Orchestration")
    print("="*50)
    
    # Check current PRs
    run_cmd("gh pr list --state open")
    
    # Try to merge in order
    results = []
    
    # PR 171 first (Vercel removal - smallest)
    results.append(("171", handle_pr_171()))
    
    # PR 175 next (Visual QA)
    results.append(("175", handle_pr_175()))
    
    # PR 176 last (Alembic AI - largest)
    results.append(("176", handle_pr_176()))
    
    # Summary
    print("\n" + "="*50)
    print("📊 Merge Results Summary:")
    
    success_count = 0
    for pr_num, success in results:
        status = "✅ MERGED" if success else "❌ FAILED"
        print(f"  PR #{pr_num}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Total: {success_count}/{len(results)} PRs merged successfully")
    
    if success_count == len(results):
        print("🎉 All PRs merged! Everything is now on main!")
    else:
        print("⚠️  Some PRs failed to merge. Manual intervention may be needed.")

if __name__ == "__main__":
    main()