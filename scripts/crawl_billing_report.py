#!/usr/bin/env python3
"""
Crawl Billing Report

Usage:
  python scripts/crawl_billing_report.py [--json] [--export FILENAME]
  - Prints detailed crawl usage and estimated cost breakdown
  - --json: Output in JSON format
  - --export: Export full data to file
"""

import argparse
import json
import os
import sys
from datetime import datetime
from tabulate import tabulate

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))

from kindlemint.billing.crawl_billing import crawl_billing_manager
from kindlemint.billing.stripe_metered import StripeMeteredBilling

def format_currency(amount: float) -> str:
    """Format currency with appropriate precision"""
    if amount < 0.01:
        return f"${amount:.8f}"
    elif amount < 1:
        return f"${amount:.4f}"
    else:
        return f"${amount:.2f}"

def main():
    parser = argparse.ArgumentParser(description="Generate crawl billing report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--export", help="Export full data to file")
    parser.add_argument("--sync-stripe", action="store_true", help="Sync usage to Stripe")
    args = parser.parse_args()
    
    # Get billing data
    data = crawl_billing_manager.export_usage_data()
    
    if args.json:
        print(json.dumps(data, indent=2))
        return
    
    # Console output
    print("\n" + "=" * 70)
    print("                      CRAWL BILLING REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Summary
    print("SUMMARY")
    print("-" * 30)
    print(f"Total Requests:    {data['total_requests']:,}")
    print(f"Total Cost:        {format_currency(data['total_cost'])}")
    print(f"Price per Crawl:   {format_currency(data['price_per_crawl'])}")
    
    if data['budget']:
        budget_used = (data['total_cost'] / data['budget']) * 100
        print(f"Budget:            {format_currency(data['budget'])} ({budget_used:.1f}% used)")
        if data['budget_exceeded']:
            print("⚠️  BUDGET EXCEEDED!")
    print()
    
    # Breakdown by source
    if data['usage_by_source']:
        print("USAGE BY SOURCE")
        print("-" * 30)
        
        table_data = []
        for source, count in sorted(data['usage_by_source'].items(), 
                                   key=lambda x: x[1], reverse=True):
            cost = data['cost_by_source'][source]
            percentage = (count / data['total_requests']) * 100
            table_data.append([
                source,
                f"{count:,}",
                f"{percentage:.1f}%",
                format_currency(cost)
            ])
        
        print(tabulate(table_data, 
                      headers=["Source", "Requests", "% of Total", "Cost"],
                      tablefmt="simple"))
        print()
    
    # Recent activity
    if data['recent_history']:
        print("RECENT ACTIVITY (Last 10)")
        print("-" * 30)
        
        recent = data['recent_history'][-10:]
        for entry in recent:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            print(f"{timestamp.strftime('%Y-%m-%d %H:%M')} - "
                  f"{entry['source']} - "
                  f"{entry['count']} request(s) - "
                  f"{format_currency(entry['cost'])}")
        print()
    
    # Stripe sync
    if args.sync_stripe:
        print("STRIPE SYNC")
        print("-" * 30)
        try:
            stripe_billing = StripeMeteredBilling()
            result = stripe_billing.push_usage()
            if result['status'] == 'success':
                print(f"✅ Successfully synced {data['total_requests']} requests to Stripe")
                print(f"   Usage record ID: {result['record']['id']}")
            else:
                print("ℹ️  No usage to sync")
        except Exception as e:
            print(f"❌ Stripe sync failed: {e}")
        print()
    
    # Export data
    if args.export:
        with open(args.export, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Full data exported to: {args.export}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
