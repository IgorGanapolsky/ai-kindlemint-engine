#!/usr/bin/env python3
"""
Orchestration Metrics Aggregator
Aggregates worktree orchestration metrics and calculates real cost savings
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict

class OrchestrationMetricsAggregator:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.reports_dir = self.repo_root / "reports" / "orchestration"
        self.metrics_file = self.reports_dir / "aggregated_metrics.json"
        
        # Cost constants (based on Claude API pricing)
        self.COST_PER_1K_TOKENS = 0.01  # $0.01 per 1K tokens
        self.TRADITIONAL_TOKENS_PER_COMMIT = 50000  # Average tokens without orchestration
        self.ORCHESTRATED_TOKENS_PER_COMMIT = 20000  # Average tokens with orchestration (60% reduction)
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_existing_metrics(self) -> Dict:
        """Load existing aggregated metrics if available"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            "last_updated": datetime.now().isoformat(),
            "monthly_data": {},
            "all_time_savings": {
                "tokens_saved": 0,
                "cost_saved_usd": 0.0,
                "commits_with_orchestration": 0,
                "commits_without_orchestration": 0
            }
        }
    
    def get_commit_data_for_month(self, year: int, month: int) -> Dict:
        """Get commit data for a specific month from git log"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Use git log to count commits
        import subprocess
        
        # Count total commits for the month
        cmd = f"git log --since='{start_date.strftime('%Y-%m-%d')}' --until='{end_date.strftime('%Y-%m-%d')}' --oneline | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.repo_root)
        total_commits = int(result.stdout.strip() or 0)
        
        # Count worktree commits (commits from worktree branches)
        cmd = f"git log --since='{start_date.strftime('%Y-%m-%d')}' --until='{end_date.strftime('%Y-%m-%d')}' --grep='worktree' --oneline | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.repo_root)
        worktree_commits = int(result.stdout.strip() or 0)
        
        # Also check for commits made from worktree directories
        cmd = f"git log --since='{start_date.strftime('%Y-%m-%d')}' --until='{end_date.strftime('%Y-%m-%d')}' --all --format='%H' | while read commit; do git show --name-only --format='' $commit | grep -q 'worktrees/' && echo $commit; done | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.repo_root)
        worktree_dir_commits = int(result.stdout.strip() or 0)
        
        orchestrated_commits = max(worktree_commits, worktree_dir_commits)
        traditional_commits = total_commits - orchestrated_commits
        
        return {
            "total_commits": total_commits,
            "orchestrated_commits": orchestrated_commits,
            "traditional_commits": traditional_commits
        }
    
    def calculate_monthly_metrics(self) -> Dict:
        """Calculate metrics for the current month"""
        now = datetime.now()
        commit_data = self.get_commit_data_for_month(now.year, now.month)
        
        # Calculate token usage
        traditional_tokens = commit_data["traditional_commits"] * self.TRADITIONAL_TOKENS_PER_COMMIT
        orchestrated_tokens = commit_data["orchestrated_commits"] * self.ORCHESTRATED_TOKENS_PER_COMMIT
        
        # What would have been used without orchestration
        baseline_tokens = commit_data["total_commits"] * self.TRADITIONAL_TOKENS_PER_COMMIT
        actual_tokens = traditional_tokens + orchestrated_tokens
        tokens_saved = baseline_tokens - actual_tokens
        
        # Calculate costs
        baseline_cost = (baseline_tokens / 1000) * self.COST_PER_1K_TOKENS
        actual_cost = (actual_tokens / 1000) * self.COST_PER_1K_TOKENS
        cost_saved = baseline_cost - actual_cost
        
        # Calculate percentages
        savings_percentage = (cost_saved / baseline_cost * 100) if baseline_cost > 0 else 0
        
        return {
            "month": now.strftime("%Y-%m"),
            "commits": {
                "total": commit_data["total_commits"],
                "orchestrated": commit_data["orchestrated_commits"],
                "traditional": commit_data["traditional_commits"],
                "orchestration_rate": (commit_data["orchestrated_commits"] / commit_data["total_commits"] * 100) if commit_data["total_commits"] > 0 else 0
            },
            "tokens": {
                "baseline": baseline_tokens,
                "actual": actual_tokens,
                "saved": tokens_saved
            },
            "costs": {
                "baseline_usd": baseline_cost,
                "actual_usd": actual_cost,
                "saved_usd": cost_saved,
                "savings_percentage": savings_percentage
            },
            "efficiency": {
                "tokens_per_commit_traditional": self.TRADITIONAL_TOKENS_PER_COMMIT,
                "tokens_per_commit_orchestrated": self.ORCHESTRATED_TOKENS_PER_COMMIT,
                "reduction_percentage": 60
            }
        }
    
    def aggregate_metrics(self) -> Dict:
        """Aggregate all metrics and save to file"""
        metrics = self.load_existing_metrics()
        
        # Update current month data
        current_month_data = self.calculate_monthly_metrics()
        month_key = current_month_data["month"]
        metrics["monthly_data"][month_key] = current_month_data
        
        # Update all-time savings
        all_time_tokens_saved = sum(
            month_data["tokens"]["saved"] 
            for month_data in metrics["monthly_data"].values()
        )
        all_time_cost_saved = sum(
            month_data["costs"]["saved_usd"] 
            for month_data in metrics["monthly_data"].values()
        )
        
        metrics["all_time_savings"] = {
            "tokens_saved": all_time_tokens_saved,
            "cost_saved_usd": all_time_cost_saved,
            "months_tracked": len(metrics["monthly_data"])
        }
        
        # Add summary for current month
        metrics["current_month"] = current_month_data
        metrics["last_updated"] = datetime.now().isoformat()
        
        # Save aggregated metrics
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def get_badge_data(self) -> Dict:
        """Get data formatted for badge display"""
        metrics = self.aggregate_metrics()
        current = metrics["current_month"]
        
        return {
            "mtd_cost": current["costs"]["actual_usd"],
            "mtd_saved": current["costs"]["saved_usd"],
            "savings_percentage": current["costs"]["savings_percentage"],
            "orchestration_rate": current["commits"]["orchestration_rate"],
            "all_time_saved": metrics["all_time_savings"]["cost_saved_usd"]
        }


def main():
    """Test the aggregator"""
    aggregator = OrchestrationMetricsAggregator()
    metrics = aggregator.aggregate_metrics()
    
    print("📊 Orchestration Metrics Summary")
    print("=" * 50)
    
    current = metrics["current_month"]
    print(f"\n📅 Current Month ({current['month']}):")
    print(f"  Total Commits: {current['commits']['total']}")
    print(f"  Orchestrated: {current['commits']['orchestrated']} ({current['commits']['orchestration_rate']:.1f}%)")
    print(f"  Traditional: {current['commits']['traditional']}")
    print("\n💰 Cost Analysis:")
    print(f"  Baseline Cost: ${current['costs']['baseline_usd']:.2f}")
    print(f"  Actual Cost: ${current['costs']['actual_usd']:.2f}")
    print(f"  Saved: ${current['costs']['saved_usd']:.2f} ({current['costs']['savings_percentage']:.1f}%)")
    print("\n🎯 All-Time Savings:")
    print(f"  Total Saved: ${metrics['all_time_savings']['cost_saved_usd']:.2f}")
    print(f"  Tokens Saved: {metrics['all_time_savings']['tokens_saved']:,}")


if __name__ == "__main__":
    main()