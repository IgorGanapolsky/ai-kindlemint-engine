#!/usr/bin/env python3
"""
Workflow Cost Dashboard - Track GitHub Actions usage and costs
"""

import subprocess
import json
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Dict, List
from security import safe_command

class WorkflowCostDashboard:
    """Generate cost analytics for GitHub Actions workflows"""
    
    def __init__(self):
        self.repo = os.environ.get('GITHUB_REPOSITORY', 'IgorGanapolsky/ai-kindlemint-engine')
        self.output_dir = Path('reports/workflow-costs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub Actions pricing (as of 2024)
        self.cost_per_minute = {
            'ubuntu-latest': 0.008,  # $0.008 per minute
            'windows-latest': 0.016,  # $0.016 per minute
            'macos-latest': 0.08     # $0.08 per minute
        }
        
    def get_workflow_runs(self, days: int = 7) -> List[Dict]:
        """Get workflow runs from the past N days"""
        since = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        
        cmd = [
            'gh', 'api', 
            f'/repos/{self.repo}/actions/runs',
            '--paginate',
            '-q', f'.workflow_runs[] | select(.created_at > "{since}")'
        ]
        
        try:
            result = safe_command.run(subprocess.run, cmd, capture_output=True, text=True, check=True)
            runs = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    runs.append(json.loads(line))
            return runs
        except subprocess.CalledProcessError:
            print("Error fetching workflow runs")
            return []
    
    def calculate_costs(self, runs: List[Dict]) -> Dict:
        """Calculate costs for workflow runs"""
        total_cost = 0
        total_minutes = 0
        workflow_costs = {}
        
        for run in runs:
            # Get run duration in minutes
            if run.get('status') == 'completed':
                created = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                duration_minutes = (updated - created).total_seconds() / 60
                
                # Estimate cost (assuming ubuntu-latest)
                runner = 'ubuntu-latest'  # Default assumption
                cost = duration_minutes * self.cost_per_minute[runner]
                
                total_cost += cost
                total_minutes += duration_minutes
                
                workflow_name = run['name']
                if workflow_name not in workflow_costs:
                    workflow_costs[workflow_name] = {
                        'runs': 0,
                        'total_minutes': 0,
                        'total_cost': 0,
                        'avg_duration': 0
                    }
                
                workflow_costs[workflow_name]['runs'] += 1
                workflow_costs[workflow_name]['total_minutes'] += duration_minutes
                workflow_costs[workflow_name]['total_cost'] += cost
        
        # Calculate averages
        for workflow in workflow_costs.values():
            if workflow['runs'] > 0:
                workflow['avg_duration'] = workflow['total_minutes'] / workflow['runs']
        
        return {
            'total_cost': total_cost,
            'total_minutes': total_minutes,
            'total_runs': len(runs),
            'workflow_costs': workflow_costs,
            'projected_monthly_cost': total_cost * (30 / 7)  # Extrapolate to monthly
        }
    
    def generate_report(self, days: int = 7):
        """Generate comprehensive cost report"""
        print(f"📊 Generating workflow cost report for last {days} days...")
        
        runs = self.get_workflow_runs(days)
        costs = self.calculate_costs(runs)
        
        # Generate markdown report
        report = f"""# 📊 GitHub Actions Cost Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Period: Last {days} days

## Summary

- **Total Runs**: {costs['total_runs']}
- **Total Minutes**: {costs['total_minutes']:.0f}
- **Total Cost**: ${costs['total_cost']:.2f}
- **Projected Monthly Cost**: ${costs['projected_monthly_cost']:.2f}

## Cost by Workflow

| Workflow | Runs | Total Minutes | Avg Duration | Cost |
|----------|------|---------------|--------------|------|
"""
        
        # Sort by cost
        sorted_workflows = sorted(
            costs['workflow_costs'].items(),
            key=lambda x: x[1]['total_cost'],
            reverse=True
        )
        
        for workflow_name, stats in sorted_workflows:
            report += f"| {workflow_name} | {stats['runs']} | {stats['total_minutes']:.0f} | {stats['avg_duration']:.1f} min | ${stats['total_cost']:.2f} |\n"
        
        # Optimization recommendations
        report += f"""

## 💡 Optimization Recommendations

"""
        
        # Find expensive workflows
        expensive_workflows = [
            (name, stats) for name, stats in sorted_workflows 
            if stats['total_cost'] > costs['total_cost'] * 0.2  # >20% of total
        ]
        
        if expensive_workflows:
            report += "### High-Cost Workflows\n\n"
            for name, stats in expensive_workflows:
                report += f"- **{name}**: ${stats['total_cost']:.2f} ({stats['total_cost']/costs['total_cost']*100:.0f}% of total)\n"
                if stats['avg_duration'] > 10:
                    report += f"  - Consider optimizing: average duration is {stats['avg_duration']:.1f} minutes\n"
                if stats['runs'] > 50:
                    report += f"  - High frequency: {stats['runs']} runs in {days} days\n"
        
        # Check for schedule optimization
        scheduled_count = sum(1 for r in runs if r.get('event') == 'schedule')
        if scheduled_count > 0:
            report += f"\n### Schedule Optimization\n\n"
            report += f"- {scheduled_count} runs triggered by schedule ({scheduled_count/len(runs)*100:.0f}% of total)\n"
            report += "- Consider reducing schedule frequency or consolidating scheduled workflows\n"
        
        # Save report
        report_path = self.output_dir / f'cost_report_{datetime.now().strftime("%Y%m%d")}.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Also save JSON data
        json_path = self.output_dir / f'cost_data_{datetime.now().strftime("%Y%m%d")}.json'
        with open(json_path, 'w') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'period_days': days,
                'costs': costs,
                'run_count': len(runs)
            }, f, indent=2)
        
        print(f"✅ Report saved to: {report_path}")
        print(f"📊 Total cost (last {days} days): ${costs['total_cost']:.2f}")
        print(f"📈 Projected monthly cost: ${costs['projected_monthly_cost']:.2f}")
        
        return costs

if __name__ == "__main__":
    dashboard = WorkflowCostDashboard()
    
    # Generate weekly report
    dashboard.generate_report(days=7)
    
    # Generate monthly report
    dashboard.generate_report(days=30)
