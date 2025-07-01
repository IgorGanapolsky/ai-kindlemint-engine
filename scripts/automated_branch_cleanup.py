#!/usr/bin/env python3
"""
Automated Branch Cleanup Agent

Automatically prunes local and remote branches based on patterns and age.
Integrates with orchestration system for continuous branch hygiene.
"""

import asyncio
import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kindlemint.agents.github_issues_agent import GitHubIssuesAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BranchCleanupAgent:
    """Agent for automated branch management and cleanup"""
    
    def __init__(self):
        self.logger = logging.getLogger("BranchCleanupAgent")
        
        # Branch patterns to auto-delete
        self.auto_delete_patterns = [
            r"^deepsource-transform-[a-f0-9]+$",
            r"^dependabot/.*",
            r"^pixeebot/.*",
            r"^market-research-\d{4}-\d{2}-\d{2}$",
            r"^ai-tests-for-pr\d+-\d+$",
            r"^cherry/.*",
            r"^pr-\d+$"
        ]
        
        # Protected branches - never delete
        self.protected_branches = {
            "main", "develop", "staging", "feat/pr-based-development-strategy",
            "feat/automated-pr-management"
        }
        
        # Age threshold for automatic deletion (days)
        self.max_age_days = 30

    async def get_branches(self) -> Dict[str, List[str]]:
        """Get all local and remote branches"""
        # Get local branches
        result = subprocess.run(
            ["git", "branch"], 
            capture_output=True, text=True, cwd=Path.cwd()
        )
        local_branches = [
            b.strip().replace("* ", "") 
            for b in result.stdout.split('\n') 
            if b.strip() and not b.startswith("*")
        ]
        
        # Get remote branches
        result = subprocess.run(
            ["git", "branch", "-r"], 
            capture_output=True, text=True, cwd=Path.cwd()
        )
        remote_branches = [
            b.strip().replace("origin/", "") 
            for b in result.stdout.split('\n') 
            if b.strip() and not b.startswith("origin/HEAD")
        ]
        
        return {
            "local": local_branches,
            "remote": remote_branches
        }

    def should_delete_branch(self, branch_name: str) -> bool:
        """Check if branch should be deleted based on patterns"""
        if branch_name in self.protected_branches:
            return False
            
        return any(
            re.match(pattern, branch_name) 
            for pattern in self.auto_delete_patterns
        )

    async def delete_local_branch(self, branch_name: str) -> bool:
        """Delete a local branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "-D", branch_name],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            if result.returncode == 0:
                self.logger.info(f"✅ Deleted local branch: {branch_name}")
                return True
            else:
                self.logger.error(f"❌ Failed to delete local branch {branch_name}: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error deleting local branch {branch_name}: {e}")
            return False

    async def delete_remote_branch(self, branch_name: str) -> bool:
        """Delete a remote branch"""
        try:
            result = subprocess.run(
                ["git", "push", "origin", "--delete", branch_name],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            if result.returncode == 0:
                self.logger.info(f"✅ Deleted remote branch: {branch_name}")
                return True
            else:
                self.logger.error(f"❌ Failed to delete remote branch {branch_name}: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error deleting remote branch {branch_name}: {e}")
            return False

    async def cleanup_merged_branches(self) -> Dict[str, int]:
        """Clean up branches that have been merged"""
        try:
            # Get merged branches
            result = subprocess.run(
                ["git", "branch", "--merged", "main"],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            
            merged_branches = [
                b.strip().replace("* ", "") 
                for b in result.stdout.split('\n') 
                if b.strip() and not b.strip() in ["main", "develop", "staging"]
            ]
            
            deleted_count = 0
            for branch in merged_branches:
                if branch not in self.protected_branches:
                    if await self.delete_local_branch(branch):
                        deleted_count += 1
            
            return {"merged_branches_deleted": deleted_count}
            
        except Exception as e:
            self.logger.error(f"Error cleaning merged branches: {e}")
            return {"merged_branches_deleted": 0}

    async def cleanup_by_patterns(self) -> Dict[str, int]:
        """Clean up branches matching deletion patterns"""
        branches = await self.get_branches()
        stats = {"local_deleted": 0, "remote_deleted": 0}
        
        # Clean local branches
        for branch in branches["local"]:
            if self.should_delete_branch(branch):
                if await self.delete_local_branch(branch):
                    stats["local_deleted"] += 1
        
        # Clean remote branches
        for branch in branches["remote"]:
            if self.should_delete_branch(branch):
                if await self.delete_remote_branch(branch):
                    stats["remote_deleted"] += 1
        
        return stats

    async def prune_remote_tracking(self) -> bool:
        """Prune remote tracking branches"""
        try:
            result = subprocess.run(
                ["git", "remote", "prune", "origin"],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            if result.returncode == 0:
                self.logger.info("✅ Pruned remote tracking branches")
                return True
            else:
                self.logger.error(f"❌ Failed to prune remote tracking: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error pruning remote tracking: {e}")
            return False

    async def run_full_cleanup(self) -> Dict[str, any]:
        """Run complete branch cleanup"""
        print("🧹 Starting automated branch cleanup...")
        
        # Get initial state
        initial_branches = await self.get_branches()
        initial_count = len(initial_branches["local"]) + len(initial_branches["remote"])
        
        print(f"📊 Initial state: {len(initial_branches['local'])} local, {len(initial_branches['remote'])} remote branches")
        
        results = {}
        
        # 1. Clean up merged branches
        print("🔄 Cleaning merged branches...")
        merged_stats = await self.cleanup_merged_branches()
        results.update(merged_stats)
        
        # 2. Clean up by patterns
        print("🎯 Cleaning branches by patterns...")
        pattern_stats = await self.cleanup_by_patterns()
        results.update(pattern_stats)
        
        # 3. Prune remote tracking
        print("🌐 Pruning remote tracking branches...")
        results["remote_pruned"] = await self.prune_remote_tracking()
        
        # Get final state
        final_branches = await self.get_branches()
        final_count = len(final_branches["local"]) + len(final_branches["remote"])
        
        results["total_deleted"] = initial_count - final_count
        results["final_local_count"] = len(final_branches["local"])
        results["final_remote_count"] = len(final_branches["remote"])
        
        print(f"✅ Cleanup complete! Deleted {results['total_deleted']} branches")
        print(f"📊 Final state: {results['final_local_count']} local, {results['final_remote_count']} remote branches")
        
        return results

async def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 KindleMint Automated Branch Cleanup Agent")
    print("=" * 60)
    print()
    
    cleanup_agent = BranchCleanupAgent()
    
    try:
        results = await cleanup_agent.run_full_cleanup()
        
        print("\n📋 Cleanup Summary:")
        print(f"   • Merged branches deleted: {results.get('merged_branches_deleted', 0)}")
        print(f"   • Local branches deleted: {results.get('local_deleted', 0)}")
        print(f"   • Remote branches deleted: {results.get('remote_deleted', 0)}")
        print(f"   • Total branches deleted: {results.get('total_deleted', 0)}")
        print(f"   • Remaining: {results.get('final_local_count', 0)} local, {results.get('final_remote_count', 0)} remote")
        
        if results.get('total_deleted', 0) > 0:
            print("\n🎉 Repository hygiene improved! Your branch tree is now clean.")
        else:
            print("\n✨ Repository already clean - no branches needed deletion.")
            
    except Exception as e:
        print(f"❌ Branch cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())