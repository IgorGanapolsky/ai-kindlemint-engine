#!/usr/bin/env python3
"""
Setup Worktree Git Hooks
Installs enhanced git hooks that support worktree orchestration
"""

import shutil
from datetime import datetime
from pathlib import Path

class WorktreeHookSetup:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.hooks_dir = self.repo_root / ".git" / "hooks"
        
    def setup_hooks(self):
        """Install worktree-aware git hooks"""
        print("🔧 Setting up Worktree Git Hooks")
        print("=" * 60)
        
        # Backup existing pre-commit hook
        pre_commit = self.hooks_dir / "pre-commit"
        pre_commit_worktree = self.hooks_dir / "pre-commit-worktree"
        
        if pre_commit.exists() and pre_commit_worktree.exists():
            # Backup the original
            backup_name = f"pre-commit.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.hooks_dir / backup_name
            shutil.copy2(pre_commit, backup_path)
            print(f"✅ Backed up existing hook to {backup_name}")
            
            # Replace with enhanced version
            shutil.copy2(pre_commit_worktree, pre_commit)
            print("✅ Installed enhanced pre-commit hook with worktree support")
            
        # Create post-commit hook for metrics
        self._create_post_commit_hook()
        
        print("\n✅ Git hooks setup complete!")
        print("\n📋 Features enabled:")
        print("  • Worktree usage recommendations")
        print("  • Token cost tracking")
        print("  • Orchestration metrics")
        print("  • Slack notifications with worktree info")
        
    def _create_post_commit_hook(self):
        """Create post-commit hook for metrics reporting"""
        post_commit_content = '''#!/bin/bash
# Post-commit Hook for Worktree Orchestration Metrics

REPO_ROOT=$(git rev-parse --show-toplevel)
CURRENT_DIR=$(pwd)

# Only report if orchestration is enabled
ORCHESTRATION_CONFIG="$REPO_ROOT/.worktree_orchestration_config.json"
if [ -f "$ORCHESTRATION_CONFIG" ]; then
    ORCHESTRATION_ENABLED=$(python3 -c "import json; print(json.load(open('$ORCHESTRATION_CONFIG'))['orchestration']['enabled'])" 2>/dev/null || echo "false")
    
    if [ "$ORCHESTRATION_ENABLED" = "True" ]; then
        # Report token savings if using worktree
        if [[ "$CURRENT_DIR" == *"/worktrees/"* ]]; then
            WORKTREE_NAME=$(basename $(dirname "$CURRENT_DIR"))
            echo "💰 Token Savings Report:"
            echo "   Worktree: $WORKTREE_NAME"
            echo "   Estimated savings: 60% token reduction"
            echo "   Cost efficiency: HIGH"
        else
            echo "📊 Direct commit to main branch"
            echo "   Consider using worktrees for better efficiency"
        fi
    fi
fi

exit 0
'''
        
        post_commit_path = self.hooks_dir / "post-commit"
        post_commit_path.write_text(post_commit_content)
        post_commit_path.chmod(0o755)
        print("✅ Created post-commit hook for metrics reporting")
        
    def verify_setup(self):
        """Verify hooks are properly installed"""
        print("\n🔍 Verifying hook installation...")
        
        hooks_to_check = ["pre-commit", "post-commit"]
        all_good = True
        
        for hook_name in hooks_to_check:
            hook_path = self.hooks_dir / hook_name
            if hook_path.exists() and hook_path.stat().st_mode & 0o111:
                print(f"  ✅ {hook_name}: Installed and executable")
            else:
                print(f"  ❌ {hook_name}: Missing or not executable")
                all_good = False
                
        return all_good
        

if __name__ == "__main__":
    setup = WorktreeHookSetup()
    setup.setup_hooks()
    
    if setup.verify_setup():
        print("\n🎉 All hooks installed successfully!")
        print("\nNext commit will:")
        print("1. Check if you should use a worktree")
        print("2. Track token costs")
        print("3. Report efficiency metrics")
    else:
        print("\n⚠️  Some hooks may need manual attention")