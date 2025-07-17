#!/usr/bin/env python3
"""
Process Email Sequences

This script should be run daily (via cron or GitHub Actions) to:
1. Send scheduled emails in sequences
2. Process new subscribers
3. Track conversions
4. Generate reports
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.email import EmailAutomation

def process_daily_emails():
    """Process all email sequences for the day"""
    print("📧 Processing Daily Email Sequences")
    print("=" * 60)
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize email automation
    email_automation = EmailAutomation()
    
    # Get current stats
    stats_before = email_automation.get_stats()
    print("📊 Current Stats:")
    print(f"   Total subscribers: {stats_before.get('total_subscribers', 0)}")
    print(f"   Active subscribers: {stats_before.get('active_subscribers', 0)}")
    print(f"   Emails sent: {stats_before.get('emails_sent', 0)}")
    print(f"   Conversions: {stats_before.get('conversions', 0)}")
    print(f"   Total revenue: ${stats_before.get('total_conversions_value', 0):.2f}")
    print()
    
    # Process sequences
    print("🔄 Processing sequences...")
    results = email_automation.process_sequences()
    
    print("\n✅ Processing Complete:")
    print(f"   Subscribers processed: {results['processed']}")
    print(f"   Emails sent: {results['emails_sent']}")
    
    if results['errors']:
        print("\n⚠️  Errors encountered:")
        for error in results['errors']:
            print(f"   - {error}")
    
    # Get updated stats
    stats_after = email_automation.get_stats()
    
    # Calculate changes
    new_emails = stats_after.get('emails_sent', 0) - stats_before.get('emails_sent', 0)
    new_conversions = stats_after.get('conversions', 0) - stats_before.get('conversions', 0)
    new_revenue = stats_after.get('total_conversions_value', 0) - stats_before.get('total_conversions_value', 0)
    
    print("\n📈 Today's Performance:")
    print(f"   New emails sent: {new_emails}")
    print(f"   New conversions: {new_conversions}")
    print(f"   New revenue: ${new_revenue:.2f}")
    
    # Generate daily report
    report_dir = Path("reports/email_automation")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
    
    with open(report_file, 'w') as f:
        f.write("Email Automation Daily Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("Processing Results:\n")
        f.write(f"  Subscribers processed: {results['processed']}\n")
        f.write(f"  Emails sent: {results['emails_sent']}\n")
        f.write(f"  Errors: {len(results['errors'])}\n\n")
        
        f.write("Current Statistics:\n")
        f.write(f"  Total subscribers: {stats_after.get('total_subscribers', 0)}\n")
        f.write(f"  Active subscribers: {stats_after.get('active_subscribers', 0)}\n")
        f.write(f"  Total emails sent: {stats_after.get('emails_sent', 0)}\n")
        f.write(f"  Total conversions: {stats_after.get('conversions', 0)}\n")
        f.write(f"  Total revenue: ${stats_after.get('total_conversions_value', 0):.2f}\n")
        f.write(f"  Avg conversion value: ${stats_after.get('avg_conversion_value', 0):.2f}\n")
        
        if results['errors']:
            f.write("\nErrors:\n")
            for error in results['errors']:
                f.write(f"  - {error}\n")
    
    print(f"\n📄 Report saved to: {report_file}")
    
    return {
        'success': True,
        'emails_sent': results['emails_sent'],
        'errors': results['errors'],
        'report_file': str(report_file)
    }

def main():
    """Main entry point"""
    try:
        result = process_daily_emails()
        
        # Exit with appropriate code
        if result['errors']:
            sys.exit(1)  # Partial failure
        else:
            sys.exit(0)  # Success
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(2)  # Complete failure

if __name__ == "__main__":
    main()