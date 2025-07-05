#!/usr/bin/env python3
"""
Generate Analytics Report

This script generates comprehensive analytics reports for the email funnel:
- Conversion rates at each stage
- Revenue metrics
- Email performance
- Actionable recommendations

Can be run daily/weekly via cron to monitor performance.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.analytics import ConversionTracker


def generate_daily_report():
    """Generate daily analytics report"""
    print("📊 Generating Analytics Report")
    print("=" * 60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize tracker
    tracker = ConversionTracker()
    
    # Get funnel metrics
    print("🎯 Funnel Performance (Last 30 Days)")
    print("-" * 40)
    
    metrics = tracker.get_funnel_metrics(30)
    stages = metrics['funnel_stages']
    rates = metrics['conversion_rates']
    
    print(f"Visitors:    {stages['visitors']:,}")
    print(f"Signups:     {stages['signups']:,} ({rates['visitor_to_signup']}% conversion)")
    print(f"Engaged:     {stages['engaged']:,} ({rates['signup_to_engaged']}% of signups)")
    print(f"Customers:   {stages['customers']:,} ({rates['engaged_to_customer']}% of engaged)")
    print(f"\n📈 Overall Conversion Rate: {rates['overall']}%")
    
    # Revenue metrics
    print("\n💰 Revenue Metrics (Last 3 Months)")
    print("-" * 40)
    
    revenue = tracker.get_revenue_metrics(3)
    print(f"Total Revenue:        ${revenue['total_revenue']:,.2f}")
    print(f"Total Purchases:      {revenue['total_purchases']}")
    print(f"Average Order Value:  ${revenue['average_order_value']:.2f}")
    
    if revenue['monthly_revenue']:
        print("\nMonthly Breakdown:")
        for month, amount in revenue['monthly_revenue'].items():
            print(f"  {month}: ${amount:,.2f}")
    
    if revenue['top_products']:
        print("\nTop Products:")
        for product, amount in list(revenue['top_products'].items())[:3]:
            print(f"  {product}: ${amount:,.2f}")
    
    # Email performance
    print("\n📧 Email Performance")
    print("-" * 40)
    
    email_perf = tracker.get_email_performance()
    if email_perf:
        print("{:<20} {:>8} {:>8} {:>10} {:>8} {:>10}".format(
            "Email Type", "Sent", "Opens", "Open Rate", "Clicks", "CTR"
        ))
        print("-" * 70)
        
        for email_type, stats in email_perf.items():
            print("{:<20} {:>8} {:>8} {:>9}% {:>8} {:>9}%".format(
                email_type,
                stats['sent'],
                stats['opens'],
                stats['open_rate'],
                stats['clicks'],
                stats['click_rate']
            ))
    
    # User segments
    print("\n👥 User Segments")
    print("-" * 40)
    
    segments = tracker._get_user_segments()
    total_users = sum(segments.values())
    
    for segment, count in segments.items():
        percentage = (count / total_users * 100) if total_users > 0 else 0
        print(f"{segment.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Recommendations
    print("\n💡 Recommendations")
    print("-" * 40)
    
    recommendations = tracker._generate_recommendations()
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("✅ All metrics looking good! Keep up the great work.")
    
    # Export HTML dashboard
    print("\n📄 Exporting Dashboard...")
    
    reports_dir = Path("reports/analytics")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    dashboard_file = reports_dir / f"dashboard_{datetime.now().strftime('%Y%m%d')}.html"
    dashboard_path = tracker.export_analytics_dashboard(str(dashboard_file))
    
    print(f"✅ Dashboard exported to: {dashboard_path}")
    
    # Save text report
    text_report_file = reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Capture all the printed output
    import io
    from contextlib import redirect_stdout
    
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        # Re-run all the prints to capture them
        print("📊 Analytics Report")
        print("=" * 60)
        print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("🎯 Funnel Performance (Last 30 Days)")
        print("-" * 40)
        print(f"Visitors:    {stages['visitors']:,}")
        print(f"Signups:     {stages['signups']:,} ({rates['visitor_to_signup']}% conversion)")
        print(f"Engaged:     {stages['engaged']:,} ({rates['signup_to_engaged']}% of signups)")
        print(f"Customers:   {stages['customers']:,} ({rates['engaged_to_customer']}% of engaged)")
        print(f"\n📈 Overall Conversion Rate: {rates['overall']}%")
        
        print("\n💰 Revenue Metrics (Last 3 Months)")
        print("-" * 40)
        print(f"Total Revenue:        ${revenue['total_revenue']:,.2f}")
        print(f"Total Purchases:      {revenue['total_purchases']}")
        print(f"Average Order Value:  ${revenue['average_order_value']:.2f}")
        
        if recommendations:
            print("\n💡 Recommendations")
            print("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
    
    # Save the captured output
    with open(text_report_file, 'w') as f:
        f.write(buffer.getvalue())
    
    print(f"✅ Text report saved to: {text_report_file}")
    
    return {
        'success': True,
        'dashboard_file': str(dashboard_path),
        'text_report_file': str(text_report_file),
        'metrics': metrics,
        'revenue': revenue
    }


def generate_weekly_summary():
    """Generate weekly executive summary"""
    print("\n📊 Weekly Executive Summary")
    print("=" * 60)
    
    tracker = ConversionTracker()
    
    # Compare this week vs last week
    this_week = tracker.get_funnel_metrics(7)
    last_week = tracker.get_funnel_metrics(14)  # Will include this week, so we'll calculate
    
    print("📈 Week-over-Week Growth:")
    
    # Calculate growth rates
    for stage in ['visitors', 'signups', 'customers']:
        this_week_count = this_week['funnel_stages'][stage]
        # Approximate last week by subtracting this week from 14-day total
        last_week_count = max(0, last_week['funnel_stages'][stage] - this_week_count)
        
        if last_week_count > 0:
            growth = ((this_week_count - last_week_count) / last_week_count) * 100
            sign = "+" if growth > 0 else ""
            print(f"  {stage.capitalize()}: {sign}{growth:.1f}%")
        else:
            print(f"  {stage.capitalize()}: New this week!")
    
    # Key insights
    print("\n🔑 Key Insights:")
    
    overall_rate = this_week['conversion_rates']['overall']
    if overall_rate > 2:
        print("  ✅ Excellent conversion rate - funnel is performing well")
    elif overall_rate > 1:
        print("  ⚠️  Good conversion rate - room for improvement")
    else:
        print("  ❌ Low conversion rate - urgent optimization needed")
    
    # Action items
    print("\n🎯 Action Items for Next Week:")
    recommendations = tracker._generate_recommendations()[:3]  # Top 3
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate analytics reports')
    parser.add_argument('--type', choices=['daily', 'weekly', 'both'], 
                       default='daily', help='Type of report to generate')
    
    args = parser.parse_args()
    
    if args.type in ['daily', 'both']:
        result = generate_daily_report()
        
    if args.type in ['weekly', 'both']:
        generate_weekly_summary()
    
    print("\n✅ Analytics report generation complete!")


if __name__ == "__main__":
    main()