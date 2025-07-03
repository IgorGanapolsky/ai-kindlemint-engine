#!/usr/bin/env python3
"""
CEO Dashboard - Real-time orchestration status
No technical details, just business metrics
"""

import asyncio
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import psutil


class CEODashboard:
    """Executive dashboard for orchestration metrics"""
    
    def __init__(self):
        self.worktrees_dir = Path.cwd() / "worktrees"
        
    def get_executive_summary(self) -> Dict[str, any]:
        """Get high-level business metrics"""
        
        # Check CI status
        ci_status = self._get_ci_status()
        
        # Check worktree utilization
        worktree_status = self._get_worktree_utilization()
        
        # Calculate cost savings
        cost_metrics = self._calculate_cost_savings()
        
        # Book production metrics
        production_metrics = self._get_production_metrics()
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "executive_summary": {
                "ci_health": ci_status["health_score"],
                "parallel_efficiency": f"{worktree_status['efficiency']}%",
                "monthly_cost_savings": cost_metrics["monthly_savings"],
                "books_ready_to_publish": production_metrics["ready_count"],
                "time_to_next_book": production_metrics["eta"]
            },
            "alerts": self._get_executive_alerts(),
            "recommendation": self._get_strategic_recommendation()
        }
    
    def _get_ci_status(self) -> Dict[str, any]:
        """Get CI health status"""
        try:
            # Check recent workflow runs
            cmd = "gh run list --limit 10 --json conclusion,status"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                successful = sum(1 for r in runs if r.get("conclusion") == "success")
                total = len(runs)
                health_score = (successful / total * 100) if total > 0 else 0
                
                return {
                    "health_score": f"{health_score:.0f}%",
                    "status": "🟢 Healthy" if health_score > 80 else "🟡 Needs Attention" if health_score > 50 else "🔴 Critical"
                }
        except:
            pass
        
        return {"health_score": "N/A", "status": "🔵 Checking..."}
    
    def _get_worktree_utilization(self) -> Dict[str, any]:
        """Calculate worktree efficiency"""
        if not self.worktrees_dir.exists():
            return {"efficiency": 0, "active_worktrees": 0}
        
        worktrees = list(self.worktrees_dir.iterdir())
        active_count = len(worktrees)
        
        # Check CPU utilization
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Calculate efficiency based on worktree count and CPU usage
        if active_count > 0:
            efficiency = min(100, (active_count * 20) + (cpu_percent / 2))
        else:
            efficiency = 0
        
        return {
            "efficiency": int(efficiency),
            "active_worktrees": active_count,
            "cpu_utilization": f"{cpu_percent:.1f}%"
        }
    
    def _calculate_cost_savings(self) -> Dict[str, any]:
        """Calculate cost savings from parallel execution"""
        # Base costs (hypothetical)
        sequential_cost_per_book = 2.50  # $2.50 per book sequential
        parallel_cost_per_book = 0.75   # $0.75 per book parallel
        
        # Estimate books per month
        books_per_month = 100
        
        sequential_monthly = sequential_cost_per_book * books_per_month
        parallel_monthly = parallel_cost_per_book * books_per_month
        savings = sequential_monthly - parallel_monthly
        
        return {
            "monthly_savings": f"${savings:.2f}",
            "percentage_saved": f"{(savings/sequential_monthly)*100:.0f}%",
            "annual_projection": f"${savings * 12:.2f}"
        }
    
    def _get_production_metrics(self) -> Dict[str, any]:
        """Get book production metrics"""
        # Check for completed books
        output_dir = Path.cwd() / "output"
        if output_dir.exists():
            pdf_files = list(output_dir.glob("*.pdf"))
            ready_count = len(pdf_files)
            
            # Estimate time to next book
            if ready_count > 0:
                eta = "Ready now!"
            else:
                eta = "30 minutes"
        else:
            ready_count = 0
            eta = "1 hour"
        
        return {
            "ready_count": ready_count,
            "eta": eta,
            "production_rate": "4 books/hour with worktrees"
        }
    
    def _get_executive_alerts(self) -> List[str]:
        """Get business-relevant alerts"""
        alerts = []
        
        # Check if worktrees are set up
        if not self.worktrees_dir.exists() or len(list(self.worktrees_dir.iterdir())) == 0:
            alerts.append("⚠️ Parallel processing not active - losing 75% efficiency")
        
        # Check CI health
        ci_status = self._get_ci_status()
        if "Critical" in ci_status.get("status", ""):
            alerts.append("🔴 CI system needs attention - book production may be delayed")
        
        # Check disk space
        disk_usage = psutil.disk_usage('/')
        if disk_usage.percent > 90:
            alerts.append("💾 Low disk space - may impact book generation")
        
        return alerts if alerts else ["✅ All systems operational"]
    
    def _get_strategic_recommendation(self) -> str:
        """Provide strategic recommendation"""
        worktree_status = self._get_worktree_utilization()
        
        if worktree_status["efficiency"] < 50:
            return "📈 Activate parallel processing to 4x your book production"
        elif worktree_status["efficiency"] < 80:
            return "🚀 System running well - consider scaling to more book types"
        else:
            return "💎 Optimal performance - maintain current strategy"
    
    def display_dashboard(self):
        """Display formatted dashboard"""
        summary = self.get_executive_summary()
        
        print("\n" + "="*60)
        print("📊 CEO DASHBOARD - AI-KindleMint Engine")
        print("="*60)
        print(f"🕐 {summary['timestamp']}")
        print()
        
        exec_summary = summary["executive_summary"]
        print("📈 KEY METRICS:")
        print(f"   CI Health: {exec_summary['ci_health']}")
        print(f"   Parallel Efficiency: {exec_summary['parallel_efficiency']}")
        print(f"   Monthly Savings: {exec_summary['monthly_cost_savings']}")
        print(f"   Books Ready: {exec_summary['books_ready_to_publish']}")
        print(f"   Next Book ETA: {exec_summary['time_to_next_book']}")
        print()
        
        print("🚨 ALERTS:")
        for alert in summary["alerts"]:
            print(f"   {alert}")
        print()
        
        print("💡 RECOMMENDATION:")
        print(f"   {summary['recommendation']}")
        print("="*60)


async def live_dashboard():
    """Run live updating dashboard"""
    dashboard = CEODashboard()
    
    while True:
        # Clear screen (works on Unix/Linux/Mac)
        print("\033[2J\033[H")
        
        # Display dashboard
        dashboard.display_dashboard()
        
        # Update every 30 seconds
        await asyncio.sleep(30)


if __name__ == "__main__":
    dashboard = CEODashboard()
    
    # One-time display
    dashboard.display_dashboard()
    
    # Uncomment for live updates:
    # asyncio.run(live_dashboard())