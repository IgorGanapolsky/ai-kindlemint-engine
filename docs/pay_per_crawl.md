# Pay-Per-Crawl Strategy

This document summarizes Cloudflare's "Pay-Per-Crawl" approach and proposes how we can apply similar strategies to our business.

## Key Takeaways from Cloudflare Blog
- On-demand crawling at scale: Customers pay only for the pages they request, eliminating flat subscription costs and reducing waste.
- Usage-based pricing: Transparent per-URL (or per-page) billing, with tiered discounts for high volume.
- Scalability and reliability: Distributed crawlers with built-in retries and resilience.
- Integration simplicity: API-driven crawl initiation and status monitoring.

## Proposed Integration for KindleMint
1. **Usage Tracking**
   - Instrument all HTTP-based crawling functions (e.g., Amazon scraping, market scouting) to record each crawl request.
   - Leverage a centralized `CrawlBillingManager` to accumulate usage counts.

2. **Configurable Pricing**
   - Expose `PRICE_PER_CRAWL` as an environment variable (default `$0.00001` per request).
   - Allow override for testing or regional pricing schemes.

3. **Billing & Reporting**
   - Provide CLI tools and scripts to generate usage reports (`scripts/crawl_billing_report.py`).
   - In future releases, integrate with Stripe metered billing APIs to automate invoicing.

4. **Alerting & Thresholds**n+   - Add monitoring to alert when usage exceeds budgeted limits.
   - Enable auto-pausing of non-critical crawls based on configurable thresholds.

## Next Steps
- Implement automated sync of usage records with Stripe for customers on metered plans.
- Add UI/dashboard for real-time usage and cost visualization.
- Explore bulk crawl queue optimizations and caching to reduce redundant requests.
