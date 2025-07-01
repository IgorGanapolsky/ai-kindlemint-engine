# KindleMint Orchestration System

A comprehensive performance monitoring and business intelligence system for your KDP book portfolio.

## Overview

The orchestration system consists of four specialized agents that work together to monitor your book performance, conduct market research, and provide business intelligence:

### 🤖 Orchestration Agents

1. **KDP Performance Agent** (`kdp_performance_agent.py`)
   - Monitors individual book performance metrics
   - Tracks Best Seller Rank (BSR)
   - Collects sales data and page reads
   - Monitors reviews and ratings
   - Tracks pricing and availability

2. **Business Analytics Agent** (`business_analytics_agent.py`)
   - Generates comprehensive business reports
   - Calculates ROI and financial projections
   - Provides performance benchmarking
   - Creates executive dashboards
   - Identifies growth opportunities

3. **Market Research Agent** (`market_research_agent.py`)
   - Conducts competitive analysis
   - Researches market trends
   - Identifies pricing opportunities
   - Analyzes market gaps
   - Provides SEO insights

4. **Automation Coordinator** (`automation_coordinator.py`)
   - Orchestrates all other agents
   - Schedules automated workflows
   - Coordinates data flow between agents
   - Manages task execution
   - Generates comprehensive reports

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install aiohttp beautifulsoup4 pandas numpy
```

### 2. Run the Orchestration System

```bash
python -m kindlemint.orchestration_runner
```

### 3. Initial Setup

The system will automatically:
- Discover books from your `books/active_production` directory
- Extract metadata and ASIN information
- Begin performance monitoring
- Start market research workflows
- Generate initial business intelligence reports

## 📊 What It Does

### Automated Workflows

- **Hourly**: Book performance monitoring
- **Daily**: Comprehensive analysis and reporting (2 AM)
- **Weekly**: Deep market research (Sunday 3 AM)
- **Daily**: Coordination summaries (11 PM)

### Data Collection

- **Book Performance**: BSR, ratings, reviews, pricing, availability
- **Market Intelligence**: Competitor analysis, trend identification
- **Business Metrics**: Revenue estimates, ROI calculations, growth projections

### Reports Generated

- **Performance Reports**: Individual book metrics and trends
- **Business Intelligence**: Portfolio analysis, financial projections
- **Market Research**: Competitive landscape, opportunities
- **Executive Dashboards**: Key metrics and insights

## 📁 Data Storage Structure

```
books/
├── performance_data/          # KDP performance metrics
│   ├── active_books.json      # List of monitored books
│   ├── {book_id}_metrics.json # Individual book metrics
│   └── monitoring_summary.json
├── analytics_data/            # Business intelligence reports
│   ├── business_report_*.json
│   ├── executive_dashboard_*.json
│   └── analytics_cache.json
├── market_research/           # Market research data
│   ├── competitor_analysis_*.json
│   ├── niche_research_*.json
│   └── market_data.json
└── coordination_data/         # Workflow coordination
    ├── active_workflows.json
    ├── coordination_metrics.json
    └── daily_summary_*.json
```

## 🔧 Configuration

### Workflow Configuration

Edit `books/workflow_config.json` to customize:

```json
{
  "workflows": {
    "comprehensive_analysis": {
      "schedule": "daily_2am",
      "enabled": true,
      "timeout_minutes": 60
    },
    "performance_monitoring": {
      "schedule": "hourly",
      "enabled": true,
      "timeout_minutes": 30
    }
  }
}
```

### Agent Configuration

Each agent can be configured with:
- Monitoring intervals
- Data storage paths
- Rate limiting settings
- Performance thresholds

## 📈 Key Metrics Tracked

### Performance Metrics
- Best Seller Rank (BSR)
- Customer ratings and reviews
- Price tracking
- Availability status
- Page reads (KU)

### Business Metrics
- Estimated revenue
- ROI calculations
- Cost analysis
- Break-even projections
- Market positioning

### Market Intelligence
- Competitor analysis
- Pricing landscape
- Market gaps identification
- Trend analysis
- SEO opportunities

## 🎯 Current Limitations & Future Enhancements

### Current State (MVP)
- Public data scraping (Amazon product pages)
- Estimated metrics (not actual sales data)
- Basic competitive analysis
- Conservative revenue projections

### Planned Enhancements
- KDP Reports API integration (when available)
- Real-time sales data
- Advanced ML-based predictions
- Automated pricing optimization
- Content performance correlation

## 📊 Sample Output

### Daily Executive Summary
```json
{
  "portfolio_overview": {
    "total_books": 6,
    "active_books": 6,
    "monitoring_coverage": 100.0
  },
  "financial_snapshot": {
    "estimated_monthly_revenue": 150,
    "estimated_annual_revenue": 1800
  },
  "performance_highlights": {
    "top_performers": ["book_1", "book_2"],
    "avg_rating": 4.2
  },
  "recommendations": [
    "Scale book production to reach profitability threshold",
    "Focus on high-performing niches"
  ]
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **No Book Data Found**
   - Ensure books are in `books/active_production` directory
   - Check `amazon_kdp_metadata.json` files exist
   - Verify ASIN data is present

2. **Rate Limiting Errors**
   - System includes automatic rate limiting
   - Delays between requests are built-in
   - Monitor logs for retry attempts

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Log Files
- `orchestration_system.log` - Main system logs
- Individual agent logs in console output

## 💡 Business Value

### Immediate Benefits
- **Visibility**: Know how your books are performing
- **Intelligence**: Understand your market position
- **Automation**: Reduce manual monitoring effort

### Strategic Benefits
- **Data-Driven Decisions**: Make publishing decisions based on data
- **Competitive Advantage**: Identify market gaps and opportunities
- **Scalability**: Monitor growing portfolio efficiently

### ROI Calculation
- Time saved: ~10 hours/week of manual monitoring
- Better decisions: Potential 20-30% improvement in book performance
- Market opportunities: Identify profitable niches faster

## 🤝 Support

As your CTO, I recommend:

1. **Start Simple**: Run the basic system for 1 week to collect baseline data
2. **Analyze Results**: Review initial reports and identify patterns
3. **Optimize Gradually**: Adjust monitoring frequency and focus areas
4. **Scale Systematically**: Use insights to guide new book production

The system is designed to provide immediate value while building the foundation for advanced business intelligence as your portfolio grows.

---

**Ready to take your KDP business to the next level with data-driven insights!** 🚀