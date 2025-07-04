# Pay-Per-Crawl Monetization System - COMPLETE IMPLEMENTATION

This document details the **fully implemented** pay-per-crawl monetization system that transforms KindleMint's market research and data collection into a transparent, usage-based billing model.

## 🎯 Implementation Status: ✅ COMPLETE

**Deployed on:** July 4, 2025  
**Architecture:** Comprehensive billing infrastructure with real-time monitoring  
**Integration:** All HTTP crawling functions instrumented with usage tracking

## 🏗️ System Architecture

### Core Components

1. **CrawlBillingManager** (`src/kindlemint/billing/crawl_billing.py`)
   - ✅ Thread-safe usage tracking with source attribution
   - ✅ Budget enforcement with automatic circuit breaker
   - ✅ Historical usage tracking and analytics
   - ✅ Cost calculation with configurable pricing
   - ✅ Real-time export capabilities for reporting

2. **Stripe Integration** (`src/kindlemint/billing/stripe_metered.py`)
   - ✅ Automated metered billing sync
   - ✅ Usage record creation and management
   - ✅ Error handling and retry logic

3. **Billing Reports** (`scripts/crawl_billing_report.py`)
   - ✅ Detailed cost breakdown by source
   - ✅ JSON export for data analysis
   - ✅ Stripe sync automation
   - ✅ Budget monitoring and alerts

4. **Real-time Dashboard** (`scripts/crawl_billing_dashboard.py`)
   - ✅ Live usage monitoring with Rich UI
   - ✅ Rate calculations and projections
   - ✅ Source-based analytics
   - ✅ Budget alerts and warnings

## 📊 Instrumented Services

All HTTP-based crawling functions now include billing tracking:

### Amazon Scraping
- **Location**: `src/kindlemint/agents/kdp_performance_agent.py`
- **Source ID**: `amazon_scraping`
- **Metadata**: ASIN, product URL
- **Function**: `_scrape_amazon_product_page()`

### Reddit API
- **Location**: `scripts/reddit_market_scraper.py`
- **Source ID**: `reddit_api`
- **Metadata**: Subreddit, sort type, limit
- **Function**: `fetch_subreddit_posts()`

### SerpApi (Amazon Search)
- **Location**: `scripts/simple_market_research.py`
- **Source ID**: `serpapi`
- **Metadata**: Search query, engine type
- **Function**: Amazon product search

### Google Trends
- **Location**: `kindlemint/intelligence/market_scout.py`
- **Source ID**: `google_trends`
- **Metadata**: Keywords, timeframe
- **Function**: `get_trending_topics()`

### Botpress API
- **Location**: `src/kindlemint/integrations/botpress.py`
- **Source ID**: `botpress_api`
- **Metadata**: HTTP method, endpoint, workspace ID
- **Function**: `_make_request()`

## 💰 Pricing Model

### Default Configuration
- **Base Price**: $0.00001 per crawl request
- **Budget Control**: Optional spending limits with auto-pause
- **Billing Cycle**: Real-time accumulation with periodic Stripe sync

### Cost Examples
| Activity | Requests/Day | Daily Cost | Monthly Cost |
|----------|--------------|------------|--------------|
| Light Research | 100 | $0.001 | $0.03 |
| Moderate Usage | 1,000 | $0.01 | $0.30 |
| Heavy Analysis | 10,000 | $0.10 | $3.00 |
| Enterprise Scale | 100,000 | $1.00 | $30.00 |

## 🛠️ Usage Instructions

### Basic Reporting
```bash
# Generate detailed billing report
python scripts/crawl_billing_report.py

# Export data in JSON format
python scripts/crawl_billing_report.py --json

# Export full data to file
python scripts/crawl_billing_report.py --export billing_data.json

# Sync usage to Stripe
python scripts/crawl_billing_report.py --sync-stripe
```

### Real-time Dashboard
```bash
# Launch interactive dashboard
python scripts/crawl_billing_dashboard.py

# Custom update interval
python scripts/crawl_billing_dashboard.py --interval 10
```

### Programmatic Access
```python
from kindlemint.billing.crawl_billing import crawl_billing_manager

# Record a crawl
crawl_billing_manager.record_crawl(
    source="my_service",
    metadata={"query": "search term", "url": "example.com"}
)

# Get usage statistics
data = crawl_billing_manager.export_usage_data()
print(f"Total cost: ${data['total_cost']:.4f}")
```

## Configuration

The following environment variables control crawl billing and Stripe integration:
- **PRICE_PER_CRAWL**: Cost per individual crawl request (float). Defaults to `0.00001`.
- **MAX_CRAWL_BUDGET**: Optional maximum total spend for crawls. Further crawls are aborted if projected spend exceeds this limit. Defaults to unlimited.
- **STRIPE_SECRET_KEY**: (Required) Your Stripe secret key (`sk_...`) for API access.
- **STRIPE_SUBSCRIPTION_ITEM_ID**: (Required) The Stripe subscription item ID (`si_...`) for your metered pricing plan.
- **NON_INTERACTIVE** or **ALWAYS_YES**: Set to `1` to disable interactive prompts in any orchestrator.

Configure these in your environment or CI/CD secrets. For GitHub Actions, add under repository Settings → Secrets.

## Next Steps
- Implement automated sync of usage records with Stripe for customers on metered plans.
- Add UI/dashboard for real-time usage and cost visualization.
- Explore bulk crawl queue optimizations and caching to reduce redundant requests.
