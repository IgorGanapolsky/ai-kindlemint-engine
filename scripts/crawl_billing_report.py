#!/usr/bin/env python3
"""
Crawl Billing Report

Usage:
  python scripts/crawl_billing_report.py
  - Prints total crawl usage and estimated cost.
"""

import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))

from kindlemint.billing.crawl_billing import crawl_billing_manager

def main():
    total_requests = crawl_billing_manager.usage_count
    price_per_crawl = crawl_billing_manager.price_per_crawl
    total_cost = crawl_billing_manager.calculate_charge()

    print("Crawl Billing Report")
    print("====================")
    print(f"Total crawl requests: {total_requests}")
    print(f"Price per request: ${price_per_crawl:.8f}")
    print(f"Total estimated cost: ${total_cost:.4f}")

if __name__ == "__main__":
    main()
