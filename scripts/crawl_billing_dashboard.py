#!/usr/bin/env python3
"""
Real-time Crawl Billing Dashboard

Usage:
  python scripts/crawl_billing_dashboard.py [--interval SECONDS]
  - Displays real-time crawl usage and costs
  - --interval: Update interval in seconds (default: 5)
"""

import argparse
import os
import sys
import time
from datetime import datetime
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kindlemint.billing.crawl_billing import crawl_billing_manager
from kindlemint.billing.stripe_metered import StripeMeteredBilling

console = Console()

class CrawlBillingDashboard:
    """Real-time dashboard for crawl billing monitoring"""
    
    def __init__(self, update_interval=5):
        self.update_interval = update_interval
        self.history = deque(maxlen=50)  # Keep last 50 data points
        self.start_time = datetime.now()
        self.initial_requests = crawl_billing_manager.usage_count
        self.stripe_billing = None
        
        # Try to initialize Stripe
        try:
            self.stripe_billing = StripeMeteredBilling()
        except Exception as e:
            console.print(f"[yellow]Warning: Stripe integration unavailable: {e}[/yellow]")
    
    def format_currency(self, amount: float) -> str:
        """Format currency with appropriate precision"""
        if amount < 0.01:
            return f"${amount:.8f}"
        elif amount < 1:
            return f"${amount:.4f}"
        else:
            return f"${amount:.2f}"
    
    def format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def get_rate_per_hour(self, current_requests: int, elapsed_seconds: int) -> float:
        """Calculate requests per hour rate"""
        if elapsed_seconds == 0:
            return 0
        return (current_requests - self.initial_requests) * 3600 / elapsed_seconds
    
    def create_summary_table(self, data: dict, elapsed: int) -> Table:
        """Create summary statistics table"""
        table = Table(title="📊 Summary Statistics", show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")
        
        # Current stats
        table.add_row("Total Requests", f"{data['total_requests']:,}")
        table.add_row("Total Cost", self.format_currency(data['total_cost']))
        table.add_row("Price per Crawl", self.format_currency(data['price_per_crawl']))
        
        # Session stats
        session_requests = data['total_requests'] - self.initial_requests
        session_cost = session_requests * data['price_per_crawl']
        table.add_row("Session Requests", f"{session_requests:,}")
        table.add_row("Session Cost", self.format_currency(session_cost))
        
        # Rate calculations
        rate_per_hour = self.get_rate_per_hour(data['total_requests'], elapsed)
        cost_per_hour = rate_per_hour * data['price_per_crawl']
        table.add_row("Rate (req/hour)", f"{rate_per_hour:.1f}")
        table.add_row("Cost Rate ($/hour)", self.format_currency(cost_per_hour))
        
        # Budget info
        if data['budget']:
            budget_used = (data['total_cost'] / data['budget']) * 100
            budget_remaining = data['budget'] - data['total_cost']
            table.add_row("Budget Used", f"{budget_used:.1f}%")
            table.add_row("Budget Remaining", self.format_currency(budget_remaining))
            
            # Time to budget exhaustion
            if cost_per_hour > 0:
                hours_to_exhaustion = budget_remaining / cost_per_hour
                table.add_row("Est. Time to Budget", f"{hours_to_exhaustion:.1f} hours")
        
        return table
    
    def create_source_table(self, data: dict) -> Table:
        """Create usage by source table"""
        table = Table(title="🌐 Usage by Source")
        table.add_column("Source", style="cyan")
        table.add_column("Requests", justify="right", style="yellow")
        table.add_column("% of Total", justify="right", style="magenta")
        table.add_column("Cost", justify="right", style="green")
        
        if data['usage_by_source']:
            total = data['total_requests']
            for source, count in sorted(data['usage_by_source'].items(), 
                                       key=lambda x: x[1], reverse=True):
                cost = data['cost_by_source'][source]
                percentage = (count / total * 100) if total > 0 else 0
                table.add_row(
                    source,
                    f"{count:,}",
                    f"{percentage:.1f}%",
                    self.format_currency(cost)
                )
        else:
            table.add_row("No data", "-", "-", "-")
        
        return table
    
    def create_activity_panel(self, data: dict) -> Panel:
        """Create recent activity panel"""
        activities = []
        
        if data['recent_history']:
            for entry in data['recent_history'][-10:]:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                time_str = timestamp.strftime('%H:%M:%S')
                source = entry['source']
                count = entry['count']
                cost = self.format_currency(entry['cost'])
                
                # Color code by source
                source_colors = {
                    'amazon_scraping': 'yellow',
                    'reddit_api': 'blue',
                    'serpapi': 'green',
                    'google_trends': 'red',
                    'botpress_api': 'magenta'
                }
                color = source_colors.get(source, 'white')
                
                activities.append(f"[dim]{time_str}[/dim] [{color}]{source}[/{color}] - {count} req - {cost}")
        else:
            activities.append("[dim]No recent activity[/dim]")
        
        return Panel(
            "\n".join(activities),
            title="📜 Recent Activity",
            border_style="blue"
        )
    
    def create_alerts_panel(self, data: dict) -> Panel:
        """Create alerts and warnings panel"""
        alerts = []
        
        # Budget alerts
        if data['budget']:
            budget_used_pct = (data['total_cost'] / data['budget']) * 100
            if data['budget_exceeded']:
                alerts.append("[red bold]⚠️  BUDGET EXCEEDED![/red bold]")
            elif budget_used_pct >= 90:
                alerts.append(f"[red]⚠️  Budget critical: {budget_used_pct:.1f}% used[/red]")
            elif budget_used_pct >= 75:
                alerts.append(f"[yellow]⚠️  Budget warning: {budget_used_pct:.1f}% used[/yellow]")
        
        # Rate alerts
        rate_per_hour = self.get_rate_per_hour(data['total_requests'], 
                                               (datetime.now() - self.start_time).seconds)
        if rate_per_hour > 10000:
            alerts.append(f"[yellow]📈 High request rate: {rate_per_hour:.0f} req/hour[/yellow]")
        
        # Stripe sync status
        if self.stripe_billing and data['total_requests'] > 0:
            alerts.append("[green]✅ Stripe sync available[/green]")
        
        if not alerts:
            alerts.append("[green]✅ All systems normal[/green]")
        
        return Panel(
            "\n".join(alerts),
            title="🚨 Alerts & Status",
            border_style="red" if any("EXCEEDED" in a for a in alerts) else "green"
        )
    
    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        # Get current data
        data = crawl_billing_manager.export_usage_data()
        elapsed = (datetime.now() - self.start_time).seconds
        
        # Create header
        header = Panel(
            Align.center(
                Text(f"🚀 KindleMint Crawl Billing Dashboard\n"
                     f"Running for: {self.format_duration(elapsed)} | "
                     f"Last Update: {datetime.now().strftime('%H:%M:%S')}",
                     style="bold blue"),
                vertical="middle"
            ),
            height=3
        )
        
        # Create components
        summary_table = self.create_summary_table(data, elapsed)
        source_table = self.create_source_table(data)
        activity_panel = self.create_activity_panel(data)
        alerts_panel = self.create_alerts_panel(data)
        
        # Layout structure
        layout.split_column(
            Layout(header, size=3),
            Layout(name="main")
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(Panel(summary_table, title="", border_style="green"), size=15),
            Layout(alerts_panel)
        )
        
        layout["right"].split_column(
            Layout(Panel(source_table, title="", border_style="cyan")),
            Layout(activity_panel)
        )
        
        return layout
    
    def run(self):
        """Run the dashboard"""
        console.print("[bold green]Starting Crawl Billing Dashboard...[/bold green]")
        console.print(f"[dim]Update interval: {self.update_interval} seconds[/dim]")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")
        
        try:
            with Live(self.create_layout(), refresh_per_second=1) as live:
                while True:
                    time.sleep(self.update_interval)
                    live.update(self.create_layout())
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard stopped.[/yellow]")

def main():
    parser = argparse.ArgumentParser(description="Real-time crawl billing dashboard")
    parser.add_argument("--interval", type=int, default=5, 
                       help="Update interval in seconds")
    args = parser.parse_args()
    
    dashboard = CrawlBillingDashboard(update_interval=args.interval)
    dashboard.run()

if __name__ == "__main__":
    main()