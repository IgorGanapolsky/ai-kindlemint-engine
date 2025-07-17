#!/usr/bin/env python3
"""
Push crawl usage to Stripe Metered Billing

Usage:
  python scripts/push_crawl_usage.py
"""
import os
import sys

# Ensure project src is on path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(__file__, "..", "..", "src")
    ),
)

from kindlemint.billing.stripe_metered import StripeMeteredBilling


def main():
    print("🚀 Pushing crawl usage to Stripe...")
    try:
        billing = StripeMeteredBilling()
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        sys.exit(1)

    result = billing.push_usage()
    status = result.get("status")
    if status == "success":
        record = result.get("record")
        print(
            f"✅ Pushed usage: quantity={record.quantity}, "
            f"timestamp={record.timestamp}"
        )
    elif status == "no_usage":
        print("ℹ️  No usage to push.")
    else:
        print(f"❌ Error pushing usage: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
